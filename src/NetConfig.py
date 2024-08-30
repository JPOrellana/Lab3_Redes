import json
import re

class NetConfig:
    def __init__(self):
        self.topo_map = {}
        self.node_map = {}
        self.jid_map = {}
        self.load_topo_data()
        self.load_name_data()
        self.reverse_map()
        self.validate_net_config()

    def reverse_map(self):
        self.jid_map = {v: k for k, v in self.node_map.items()}

    def load_topo_data(self):
        content = "{'type':'topo', 'config':{'A': ['B'], 'B': ['C'], 'C': ['A']}}"
        content = re.sub(r"'", '"', content)
        data = json.loads(content)
        if data['type'] != 'topo':
            raise ValueError("Invalid topology data.")
        self.topo_map = data['config']

    def load_name_data(self):
        content = "{'type':'names', 'config':{'A': 'sag18173@alumchat.lol', 'B': 'sag18173-test1@alumchat.lol', 'C': 'sag18173-test2@alumchat.lol'}}"
        content = re.sub(r"'", '"', content)
        data = json.loads(content)
        if data['type'] != 'names':
            raise ValueError("Invalid names data.")
        self.node_map = data['config']

    def validate_net_config(self):
        for node in self.node_map.keys():
            if node not in self.topo_map:
                raise ValueError(f"Node '{node}' not found in topology.")

    def neighbors_of(self, node_id):
        print(f"Neighbors of '{node_id}':")
        return self.topo_map.get(node_id, [])

    def name_of(self, node_id):
        print(f"Name of '{node_id}':")
        return self.node_map.get(node_id, None)

    def __str__(self):
        topo_info = "Topology:\n"
        for node, neighbors in self.topo_map.items():
            topo_info += f"{node} -> {', '.join(neighbors)}\n"

        name_info = "Node Names:\n"
        for node_id, node_name in self.node_map.items():
            name_info += f"{node_id}: {node_name}\n"

        return topo_info + "\n" + name_info

