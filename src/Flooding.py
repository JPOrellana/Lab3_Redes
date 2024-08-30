import asyncio
import sys

# Solución para problemas con aiodns en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from ConnectionXMPP import ClienteXMPP

class DifusionAlgoritmo:
    def __init__(self, nodo_id, password):
        """
        Inicializa el nodo con su JID y contraseña.
        """
        self.nodo_id = nodo_id
        self.red_vecinos = set()  # Usaremos un set para almacenar dinámicamente los vecinos
        self.mensajes_recibidos = set()
        self.cliente_xmpp = ClienteXMPP(nodo_id, password, self)

    def conectar(self):
        """
        Inicia la conexión XMPP.
        """
        print("Intentando conectar al servidor XMPP...")
        self.cliente_xmpp.connect()
        print("Conexión iniciada, procesando...")
        self.cliente_xmpp.process(forever=False)
        print("Conexión procesada.")

    def agregar_vecino(self, vecino_jid):
        """
        Agrega un vecino a la lista de vecinos del nodo.
        """
        self.red_vecinos.add(vecino_jid)
        print(f"Vecino agregado: {vecino_jid}")

    def propagar_mensaje(self, origen, mensaje_id, contenido):
        """
        Envía el mensaje a todos los vecinos del nodo actual, excepto al origen.
        """
        for vecino in self.red_vecinos:
            if vecino != origen:
                self.enviar_a_vecino(vecino, mensaje_id, contenido)
    
    def enviar_a_vecino(self, vecino, mensaje_id, contenido):
        """
        Lógica para enviar un mensaje a un vecino específico.
        Se envía el mensaje utilizando el cliente XMPP.
        """
        mensaje = {
            "type": "send_routing",
            "to": vecino,
            "from": self.nodo_id,
            "data": contenido,
            "hops": len(self.red_vecinos)
        }
        self.cliente_xmpp.enviar_mensaje(vecino, mensaje)

    def recibir_mensaje(self, origen, mensaje_id, contenido):
        """
        Procesa un mensaje recibido, reenviándolo si no se ha visto antes.
        """
        if mensaje_id not in self.mensajes_recibidos:
            self.mensajes_recibidos.add(mensaje_id)
            print(f"Mensaje recibido de {origen}: {contenido}")
            self.propagar_mensaje(origen, mensaje_id, contenido)
        else:
            print(f"Mensaje {mensaje_id} ya procesado, ignorando.")
    
    def enviar_echo(self, vecino):
        """
        Envía un mensaje de tipo echo para medir tiempos de respuesta.
        """
        mensaje = {
            "type": "echo",
            "from": self.nodo_id,
        }
        self.cliente_xmpp.enviar_mensaje(vecino, mensaje)
    
    def recibir_echo_response(self, mensaje):
        """
        Procesa el mensaje echo_response, calculando el tiempo de respuesta.
        """
        # Lógica para calcular el tiempo de recepción y envío
        tiempo_recepcion = 0  # Esto debería ser calculado en base a timestamps reales
        print(f"Echo response recibido. Tiempo de respuesta: {tiempo_recepcion}ms")

# Ejemplo de cómo configurar un nodo específico
if __name__ == "__main__":
    # JID (Jabber ID) y contraseña del nodo
    nodo_id = "ore21970-te@alumchat.lol"
    password = "pruebas"

    # Crear instancia del algoritmo y conectar
    difusion = DifusionAlgoritmo(nodo_id, password)
    difusion.conectar()
