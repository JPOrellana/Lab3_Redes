from ConnectionXMPP import ClienteXMPP
import json

class DifusionAlgoritmo:
    def __init__(self, nodo_id, vecinos):
        """
        Inicializa el nodo con su ID y los vecinos con los que puede comunicarse.
        """
        self.nodo_id = nodo_id
        self.red_vecinos = vecinos
        self.mensajes_recibidos = set()
        self.cliente_xmpp = ClienteXMPP(nodo_id, "password", self)

    def conectar(self):
        """
        Inicia la conexión XMPP.
        """
        self.cliente_xmpp.connect()
        self.cliente_xmpp.process(forever=False)

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

