import asyncio
import json
import time
import logging

from slixmpp import ClientXMPP
from NetConfig import NetConfig
from Dijkstra import dijkstra
from aioconsole import ainput
from json import JSONDecodeError


class RoutingLSR(ClientXMPP):
    def __init__(self, jid, password, config: NetConfig):
        super().__init__(jid, password)
        print(f"LSR activo para el usuario: {jid}\n")
        print("INFO: Asegúrese de que la topología de red esté completa antes de enviar mensajes\n")

        self.log = logging.getLogger(__name__)

        self.user_jid = jid
        self.user_id = config.jid_node_map[jid]
        self.neighbors = config.neighbors_of(self.user_id)

        self._init_event_handlers()
        self.messages_sent = set()
        self.network_config = config

        self.echo_times = {}
        self.weight_tables = {
            self.user_id: {
                'table': {neighbor_id: 10_000.0 for neighbor_id in self.neighbors},
                'version': 0
            }
        }

        self.shortest_distances = None
        self.shortest_paths = None

    async def prompt_send_message(self):
        while True:
            destination = await ainput("Ingrese el nodo de destino: ")
            message_data = await ainput("Ingrese el mensaje: ")
            sender_id = self.user_id

            if destination not in self.network_config.node_map:
                print("ERROR: El nodo de destino no se encuentra en la red\n")
                return

            receiver_jid = self.network_config.node_map[destination]
            hops = 0

            if destination not in self.neighbors:
                message_string = f'{{\"type\": \"send_routing\", \"from\": \"{sender_id}\", \"to\": \"{destination}\", \"data\": \"{message_data}\" , \"hops\": \"{hops + 1}\"}}'
                self.send_message(mto=receiver_jid, mbody=message_string, mtype='chat')
                return

            message_string = f'{{\"type\": \"message\", \"from\": \"{sender_id}\", \"data\": \"{message_data}\" }}'
            self.send_message(mto=receiver_jid, mbody=message_string, mtype='chat')

    def _send_echo(self):
        echo_message = '{\"type\": \"echo\"}'
        for neighbor_id in self.neighbors:
            neighbor_jid = self.network_config.node_map[neighbor_id]
            self.send_message(mto=neighbor_jid, mbody=echo_message, mtype='chat')
            self.echo_times[neighbor_jid] = time.time()

    def _init_event_handlers(self):
        self.add_event_handler('session_start', self.start_session)
        self.add_event_handler('message', self.process_message)

    async def start_session(self, event):
        self.send_presence()
        await self.get_roster()
        self._send_echo()
        await asyncio.create_task(self.prompt_send_message())

    async def process_message(self, msg):
        if msg['type'] not in ('chat', 'normal'):
            return
        
        sender_jid = str(msg["from"]).split("/")[0]
        body = msg['body']

        try:
            body = json.loads(body)
        except JSONDecodeError:
            print(f"ERROR: El mensaje de {sender_jid} no es compatible con JSON!")
            return

        try:
            msg_type = body['type']

            if msg_type == 'echo':
                echo_response = '{\"type\": \"echo_response\"}'
                self.send_message(mto=sender_jid, mbody=echo_response, mtype='chat')

            elif msg_type == 'echo_response':
                elapsed = time.time() - self.echo_times[sender_jid]
                sender_id = self.network_config.jid_map[sender_jid]
                self.weight_tables[self.user_id]['table'][sender_id] = elapsed
                self.weight_tables[self.user_id]['version'] += 1
                self.broadcast_weights(self.user_id)

            elif msg_type == 'weights':
                table = body['table']
                version = body['version']
                user = body['from']
                node_id = self.network_config.jid_map[user]

                if node_id not in self.weight_tables:
                    self.weight_tables[node_id] = {
                        'table': table,
                        'version': version
                    }
                    self.broadcast_weights(node_id)

                    processed_table = self.prepare_dijkstra_table()
                    self.shortest_distances, self.shortest_paths = dijkstra(processed_table, self.user_id)
                    return

                if self.weight_tables[node_id]['version'] < version:
                    self.weight_tables[node_id] = {
                        'table': table,
                        'version': version
                    }
                    self.broadcast_weights(node_id)

                    processed_table = self.prepare_dijkstra_table()
                    self.shortest_distances, self.shortest_paths = dijkstra(processed_table, self.user_id)

            elif msg_type == 'send_routing':
                destination_id = body['to']
                sender_id = body['from']
                data = body['data']
                hops = body['hops']

                next_hop_id = self.get_next_hop(destination_id)
                receiver_jid = self.network_config.node_map[next_hop_id]

                if destination_id != self.user_id:
                    routing_msg = f'{{\"type\": \"send_routing\", \"from\": \"{sender_id}\", \"to\": \"{destination_id}\", \"data\": \"{data}\" , \"hops\": \"{hops + 1}\"}}'
                    self.send_message(mto=receiver_jid, mbody=routing_msg, mtype='chat')
                    return

                final_msg = f'{{\"type\": \"message\", \"from\": \"{sender_id}\", \"data\": \"{data}\" }}'
                self.send_message(mto=receiver_jid, mbody=final_msg, mtype='chat')

            elif msg_type == 'message':
                print("Mensaje recibido:")

        except KeyError:
            print("ERROR: El mensaje recibido no está correctamente formateado: \n")

    def prepare_dijkstra_table(self):
        processed_table = {}
        for node_id, table_info in self.weight_tables.items():
            processed_table[node_id] = table_info['table']

        return processed_table

    def get_next_hop(self, destination_id):
        current_node = self.user_id
        while current_node != destination_id:
            for neighbor in self.shortest_paths[current_node]:
                if self.shortest_distances[neighbor] < self.shortest_distances[current_node]:
                    return neighbor
            current_node = neighbor
        return destination_id

    def broadcast_weights(self, node_id):
        if node_id not in self.weight_tables:
            print(f"ERROR: No se pudo transmitir los pesos para el nodo id: {node_id}\n")
            return

        table = self.weight_tables[node_id]['table']
        version = self.weight_tables[node_id]['version']
        node_jid = self.network_config.node_map[node_id]
        weights_message = f'{{\"type\": \"weights\", \"table\": {json.dumps(table)}, \"version\": {version}, \"from\": \"{node_jid}\" }}'

        for neighbor_id in self.neighbors:
            neighbor_jid = self.network_config.node_map[neighbor_id]
            self.send_message(mto=neighbor_jid, mbody=weights_message, mtype='chat')
