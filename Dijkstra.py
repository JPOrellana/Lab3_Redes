import heapq

def dijkstra(graph, start):
    # Inicializar la distancia de todos los nodos a infinito
    distances = {node: float('inf') for node in graph}
    # La distancia al nodo de inicio es 0
    distances[start] = 0
    # Cola de prioridad para gestionar el nodo siguiente con la menor distancia
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Si encontramos una distancia mayor que la registrada, la ignoramos
        if current_distance > distances[current_node]:
            continue
        
        # Explorar los nodos vecinos
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            # Si se encuentra una distancia más corta, se actualiza la distancia y la cola de prioridad
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

# Ejemplo de uso:
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1}
}

start_node = 'A'
shortest_paths = dijkstra(graph, start_node)

print(f"Shortest paths from {start_node}: {shortest_paths}")
