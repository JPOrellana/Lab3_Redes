import slixmpp
import asyncio
import json
import ssl
import logging

# Habilitar logging detallado
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

class ClienteXMPP(slixmpp.ClientXMPP):
    def __init__(self, jid, password, algoritmo):
        super().__init__(jid, password)

        self.algoritmo = algoritmo  # Instancia del algoritmo que se va a usar, e.g., DifusionAlgoritmo
        self.add_event_handler("session_start", self.iniciar_sesion)
        self.add_event_handler("message", self.manejar_mensaje)
        self.add_event_handler("got_online", self.vecino_encontrado)  # Evento para detectar vecinos

        # Configurar SSL para actuar como cliente
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # Habilitar debug detallado
        self.use_ipv6 = False  # Desactivar IPv6 si no es necesario
        self.register_plugin('xep_0030')  # Servicio de descubrimiento de XMPP
        self.register_plugin('xep_0199')  # Ping XMPP para mantener la conexión viva

    async def iniciar_sesion(self, event):
        print(f"{self.boundjid.bare} está enviando presencia...")
        self.send_presence()  # Enviar presencia a todos los nodos
        await self.get_roster()  # Obtener lista de usuarios conectados
        print(f"{self.boundjid.bare} presencia enviada.")

        # Depuración del estado de conexión
        print(f"Conectado a: {self.boundjid.full}")
        print(f"Estado: {self.get_status()}")

        # Enviar un ping al servidor para verificar el estado de la conexión
        print("Enviando ping al servidor...")
        await self.plugin['xep_0199'].send_ping(self.boundjid.host)
        print("Ping enviado y respuesta recibida.")

    def manejar_mensaje(self, msg):
        print(f"{self.boundjid.bare} recibió un mensaje de {msg['from'].bare}")
        if msg['type'] in ('chat', 'normal'):
            mensaje_json = json.loads(msg['body'])
            tipo_mensaje = mensaje_json.get('type')
            print(f"Contenido del mensaje: {mensaje_json}")

            if tipo_mensaje == "send_routing":
                self.algoritmo.recibir_mensaje(mensaje_json['from'], msg['id'], mensaje_json['data'])
            elif tipo_mensaje == "echo":
                self.enviar_echo_response(mensaje_json['from'])
            elif tipo_mensaje == "echo_response":
                self.algoritmo.recibir_echo_response(mensaje_json)
            # Aquí se pueden agregar más tipos de mensajes según sea necesario

    def enviar_mensaje(self, destino, mensaje_json):
        print(f"{self.boundjid.bare} está enviando mensaje a {destino}: {mensaje_json}")
        self.send_message(mto=destino, mbody=json.dumps(mensaje_json), mtype='chat')

    def enviar_echo_response(self, destino):
        mensaje = {
            "type": "echo_response",
            "from": self.boundjid.bare,
        }
        self.enviar_mensaje(destino, mensaje)

    def vecino_encontrado(self, presence):
        vecino_jid = presence['from'].bare
        if vecino_jid != self.boundjid.bare:
            print(f"{self.boundjid.bare} encontró al vecino: {vecino_jid}")
            self.algoritmo.agregar_vecino(vecino_jid)
