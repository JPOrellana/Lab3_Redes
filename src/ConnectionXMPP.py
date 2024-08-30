import slixmpp
import asyncio
import json

class ClienteXMPP(slixmpp.ClientXMPP):
    def __init__(self, jid, password, algoritmo):
        super().__init__(jid, password)

        self.algoritmo = algoritmo  # Instancia del algoritmo que se va a usar, e.g., DifusionAlgoritmo
        self.add_event_handler("session_start", self.iniciar_sesion)
        self.add_event_handler("message", self.manejar_mensaje)
        self.add_event_handler("got_online", self.vecino_encontrado)  # Evento para descubrir vecinos cuando se conectan
        self.vecinos = set()

    async def iniciar_sesion(self, event):
        self.send_presence()  # Enviar presencia a todos los nodos
        await self.get_roster()  # Obtener lista de usuarios conectados

    def manejar_mensaje(self, msg):
        if msg['type'] in ('chat', 'normal'):
            mensaje_json = json.loads(msg['body'])
            tipo_mensaje = mensaje_json.get('type')

            if tipo_mensaje == "send_routing":
                self.algoritmo.recibir_mensaje(mensaje_json['from'], msg['id'], mensaje_json['data'])
            elif tipo_mensaje == "echo":
                self.enviar_echo_response(mensaje_json['from'])
            elif tipo_mensaje == "echo_response":
                self.algoritmo.recibir_echo_response(mensaje_json)
            # Aquí se pueden agregar más tipos de mensajes según sea necesario

    def enviar_mensaje(self, destino, mensaje_json):
        self.send_message(mto=destino, mbody=json.dumps(mensaje_json), mtype='chat')

    def enviar_echo_response(self, destino):
        mensaje = {
            "type": "echo_response",
            "from": self.boundjid.bare,
        }
        self.enviar_mensaje(destino, mensaje)

    def vecino_encontrado(self, presence):
        """
        Maneja el evento de encontrar un nuevo vecino.
        """
        vecino_jid = presence['from'].bare
        if vecino_jid != self.boundjid.bare:
            print(f"Vecino encontrado: {vecino_jid}")
            self.vecinos.add(vecino_jid)
            self.algoritmo.agregar_vecino(vecino_jid)

