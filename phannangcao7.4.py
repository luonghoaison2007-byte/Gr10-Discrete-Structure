from collections import defaultdict

graph = defaultdict(list)
def add_edge(u, v):
    graph[u].append(v)
    graph[v].append(u)
def remove_edge(u, v):
    graph[u].remove(v)
    graph[v].remove(u)
def dfs(v, visited):
    visited.add(v)
    count = 1
    for i in graph[v]:
        if i not in visited:
            count += dfs(i, visited)
    return count
def is_valid_edge(u, v):
    if len(graph[u]) == 1:
        return True

    visited = set()
    count1 = dfs(u, visited)

    remove_edge(u, v)

    visited = set()
    count2 = dfs(u, visited)

    add_edge(u, v)

    return count1 == count2
def fleury(start):
    u = start
    path = []

    while len(graph[u]) > 0:
        for v in graph[u]:
            if is_valid_edge(u, v):
                path.append((u, v))
                remove_edge(u, v)
                u = v
                break

    return path
n = int(input("Nhập số đỉnh: "))
m = int(input("Nhập số cạnh: "))

print("Nhập các cạnh (u v):")
for _ in range(m):
    u, v = map(int, input().split())
    add_edge(u, v)

start = int(input("Nhập đỉnh bắt đầu: "))

result = fleury(start)

print("Đường đi Euler:")
for u, v in result:
    print(f"{u} -> {v}")