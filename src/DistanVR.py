import asyncio
import sys

# Solución para problemas con aiodns en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from ConnectionXMPP import ClienteXMPP

class DistanceVectorRouting:
    def __init__(self, nodo_id, password):
        """
        Inicializa el nodo con su JID y contraseña.
        """
        self.nodo_id = nodo_id
        self.red_vecinos = set()  # Usaremos un set para almacenar dinámicamente los vecinos
        self.mensajes_recibidos = set()
        self.tabla_rutas = {}  # Tabla de rutas: {nodo_destino: (costo, siguiente_salto)}
        self.inicializar_tabla()
        self.cliente_xmpp = ClienteXMPP(nodo_id, password, self)

    def inicializar_tabla(self):
        # Inicializar la tabla de rutas consigo mismo (costo 0, siguiente salto es el mismo nodo)
        self.tabla_rutas[self.nodo_id] = (0, self.nodo_id)

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
        # Propagar la tabla a los nuevos vecinos
        self.enviar_tabla(vecino_jid)

    def actualizar_tabla(self, vecino, tabla_vecino):
        # Revisar las rutas que llegan a través del vecino
        tabla_actualizada = False
        for destino, (costo_vecino, salto_vecino) in tabla_vecino.items():
            nuevo_costo = costo_vecino + 1  # Añadir 1 al costo para llegar al vecino
            if destino not in self.tabla_rutas or nuevo_costo < self.tabla_rutas[destino][0]:
                self.tabla_rutas[destino] = (nuevo_costo, vecino)
                tabla_actualizada = True

        # Si la tabla se actualizó, propagar la nueva tabla a los vecinos
        if tabla_actualizada:
            self.propagar_tabla()

    def propagar_tabla(self):
        for vecino in self.red_vecinos:
            self.enviar_tabla(vecino)

    def enviar_tabla(self, vecino):
        mensaje = {
            "type": "send_routing",
            "from": self.nodo_id,
            "tabla_rutas": self.tabla_rutas
        }
        self.cliente_xmpp.enviar_mensaje(vecino, mensaje)

    def recibir_mensaje(self, origen, mensaje_id, contenido):
        """
        Procesa un mensaje recibido, actualiza la tabla de rutas si es necesario.
        """
        if mensaje_id not in self.mensajes_recibidos:
            self.mensajes_recibidos.add(mensaje_id)
            print(f"Mensaje recibido de {origen}: {contenido}")
            
            if 'tabla_rutas' in contenido:
                self.actualizar_tabla(origen, contenido['tabla_rutas'])
            else:
                print("Mensaje no contiene tabla de rutas, ignorado.")
        else:
            print(f"Mensaje {mensaje_id} ya procesado, ignorando.")

# Ejemplo de cómo configurar un nodo específico
if __name__ == "__main__":
    # JID (Jabber ID) y contraseña del nodo
    nodo_id = "ore21970-te@alumchat.lol"
    password = "pruebas"

    # Crear instancia del algoritmo y conectar
    routing = DistanceVectorRouting(nodo_id, password)
    routing.conectar()
