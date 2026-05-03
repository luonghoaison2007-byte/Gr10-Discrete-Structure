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

n = int(input("Nhập số đỉnh: "))
m = int(input("Nhập số cạnh: "))

graph = {i: [] for i in range(n)}

print("Nhập các cạnh (u v):")
for _ in range(m):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    graph[u].append(v)
    graph[v].append(u)

print("Là đồ thị 2 phía?", is_bipartite(graph, n))