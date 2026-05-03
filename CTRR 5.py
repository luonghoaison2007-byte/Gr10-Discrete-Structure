from collections import deque

def is_bipartite(graph, n):
    color = [-1] * n  

    for start in range(n):
        if color[start] == -1:
            queue = deque([start])
            color[start] = 0

            while queue:
                u = queue.popleft()
                for v in graph[u]:
                    if color[v] == -1:
                        color[v] = 1 - color[u]
                        queue.append(v)
                    elif color[v] == color[u]:
                        return False
    return True
n = 4
graph = {
    0: [1, 3],
    1: [0, 2],
    2: [1, 3],
    3: [0, 2]
}

print("Là đồ thị 2 phía?" , is_bipartite(graph, n))