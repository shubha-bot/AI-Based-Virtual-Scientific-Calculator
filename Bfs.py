import heapq
def best_first_search(graph, heuristic, start, goal):
    visited = set()
    pq = [(heuristic[start], start, [start])]   # (priority, node, path)

    while pq:
        _, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic[neighbor], neighbor, path + [neighbor]))

    return None
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['G'],
    'F': ['G'],
    'G': []
}
heuristic = {
    'A': 8,
    'B': 5,
    'C': 4,
    'D': 7,
    'E': 3,
    'F': 2,
    'G': 0
}
path = best_first_search(graph, heuristic, 'A', 'G')
print("Path found:", path)