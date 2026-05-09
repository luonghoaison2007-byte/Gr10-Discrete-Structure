#Phần cơ bản
#download: pip install networkx matplotlib
#1.Vẽ đồ thị trực quan , Dùng 1 đồ thị duy nhất
#1.1 Nhập đồ thị
import heapq
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
# CẤU TRÚC DỮ LIỆU CHUNG
# edges   : list[(u, v, weight)]   – danh sách cạnh (có trọng số)
# directed: bool                   – Cố định False = đồ thị VÔ HƯỚNG


edges    = []        # [(u, v, weight), ...]
directed = False     # CỐ ĐỊNH: đồ thị vô hướng


#1 VẼ ĐÒ THỊ TRỰC QUAN
#1.1 Nhập đồ thị từ người dùng
def input_graph():
    """Nhập đồ thị vô hướng từ bàn phím (hỗ trợ trọng số tuỳ chọn)."""
    global directed
    loai = input("Đồ thị có hướng? (y/n): ").strip().lower()
    directed = loai == 'y' ## True nếu gõ 'y', False nếu không
    n = int(input("Nhập số cạnh: "))
    new_edges = []
    for _ in range(n):
        raw = input("Nhập cạnh (u v [trọng_số]): ").split()
        u, v = raw[0], raw[1]
        w = float(raw[2]) if len(raw) >= 3 else 1.0   # mặc định trọng số = 1
        new_edges.append((u, v, w))
    return new_edges
 
 
def build_nx_graph(edges, directed):
    """Tạo đối tượng NetworkX từ danh sách cạnh."""
    G = nx.DiGraph() if directed else nx.Graph() # có hướng → DiGraph, vô hướng → Graph
    for u, v, w in edges:
        G.add_edge(u, v, weight=w) # thêm cạnh với trọng số (dưới dạng thuộc tính 'weight')
    return G
 
#1.2 Vẽ đồ thị trực quan 
def draw_graph(edges, directed):
    """Vẽ đồ thị trực quan với nhãn trọng số."""
    if not edges:
        print("Chưa có đồ thị nào để vẽ.")
        return
 
    G   = build_nx_graph(edges, directed)
    pos = nx.spring_layout(G, seed=42)   # seed=42 → vị trí cố định
 
    edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}
 
    plt.figure(figsize=(8, 6))

    nx.draw(G, pos,
        with_labels=True,
        node_color='skyblue',
        node_size=700,
        font_size=12,
        arrows=directed,
        arrowsize=20 if directed else 10,
        width=2) #hiện trọng số cạnh
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    title = "Đồ thị có hướng" if directed else "Đồ thị vô hướng"
    plt.title(title)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)
    plt.show()


#2 LƯU VÀ TẢI ĐỒ THỊ
FILENAME = "graph.txt"
 
 
def save_graph(edges, directed):
    """Lưu đồ thị vào file (ghi đè)."""
    with open(FILENAME, 'w') as f:
        f.write(f"directed={'yes' if directed else 'no'}\n")  #Lưu đúng đồ thị 
        for u, v, w in edges:
            f.write(f"{u} {v} {w}\n") #Lưu từng cạnh theo định dạng: u v trọng_số
    print(f"✔ Đã lưu đồ thị vào '{FILENAME}'.")
 

def load_graph():
    """Tải đồ thị từ file."""
    global directed
    loaded_edges = []
    try:
        with open(FILENAME, 'r') as f:
            lines = f.readlines()
 
        # Dòng đầu: directed=yes/no
        first = lines[0].strip()
        directed = first.split('=')[1] == 'yes' if first.startswith('directed') else False
        start = 1 if first.startswith('directed') else 0
 
        for line in lines[start:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                u, v = parts[0], parts[1]
                w = float(parts[2]) if len(parts) >= 3 else 1.0
                loaded_edges.append((u, v, w))
 
        print(f"✔ Đã tải đồ thị từ '{FILENAME}'.")
    except FileNotFoundError:
        print(f"✘ File '{FILENAME}' không tồn tại.")
    return loaded_edges



#3 TÌM ĐƯỜNG ĐI NGẮN NHẤT (DIJKSTRA)
def build_adj(edges, directed):
    """Xây dựng danh sách kề từ danh sách cạnh."""
    graph = {}
    for u, v, w in edges:
        if u not in graph: graph[u] = []
        if v not in graph: graph[v] = []
        graph[u].append((v, w))
        if not directed:
            graph[v].append((u, w))
    return graph
 
 
def dijkstra(graph, start):
    """
    Thuật toán Dijkstra – tìm khoảng cách ngắn nhất từ đỉnh start đến mọi đỉnh.
    graph : {đỉnh: [(đỉnh_kề, trọng_số), ...]}
    Trả về: (dist, prev)
        dist : {đỉnh: khoảng_cách_nhỏ_nhất}
        prev : {đỉnh: đỉnh_trước} – dùng để truy vết đường đi
    """
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
 
    pq = [(0, start)]   # (khoảng cách hiện tại, đỉnh)
 
    while pq:
        current_dist, u = heapq.heappop(pq)
 
        # Bỏ qua nếu đã tìm được đường ngắn hơn trước đó
        if current_dist > dist[u]:
            continue
 
        for v, weight in graph[u]:
            new_dist = current_dist + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))
 
    return dist, prev
 
 
def reconstruct_path(prev, start, end):
    if start not in prev or end not in prev:           # ← thêm dòng này: kiểm tra trước
        return []
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev.get(current)   # ← dùng .get() thay vì [] cho an toàn
    path.reverse()
    if path and path[0] == start:     # ← thêm "path and" để tránh IndexError
        return path
    return []
 
 
def shortest_path_menu(edges, directed):
    """Giao diện con cho phần tìm đường đi ngắn nhất."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return
 
    graph = build_adj(edges, directed)
    all_nodes = list(graph.keys())
    print(f"Các đỉnh hiện có: {', '.join(sorted(all_nodes))}")
 
    start = input("Nhập đỉnh bắt đầu: ").strip()
    end   = input("Nhập đỉnh kết thúc (để trống = in tất cả): ").strip()
 
    if start not in graph:
        print(f"✘ Đỉnh '{start}' không tồn tại trong đồ thị.")
        return
 
    dist, prev = dijkstra(graph, start)
 
    if end == "":
        # In khoảng cách từ start đến mọi đỉnh
        print(f"\nKhoảng cách ngắn nhất từ '{start}':")
        for node in sorted(dist):
            d = dist[node]
            if d == float('inf'):
                print(f"  {start} → {node} : Không có đường đi")
            else:
                path = reconstruct_path(prev, start, node)
                path_str = " → ".join(path)
                print(f"  {start} → {node} : {d:.1f}   [{path_str}]")
    else:
        if end not in graph:
            print(f"✘ Đỉnh '{end}' không tồn tại trong đồ thị.")
            return
        d = dist[end]
        if d == float('inf'):
            print(f"Không có đường đi từ '{start}' đến '{end}'.")
        else:
            path = reconstruct_path(prev, start, end)
            path_str = " → ".join(path)
            print(f"\n✔ Đường đi ngắn nhất: {path_str}")
            print(f"   Tổng trọng số     : {d:.1f}")
 
    # Vẽ đồ thị và tô màu đường đi ngắn nhất (nếu có đỉnh đích cụ thể)
    if end and end in graph and dist[end] != float('inf'):
        highlight_path(edges, directed, reconstruct_path(prev, start, end))
 
 
def highlight_path(edges, directed, path):
    """Vẽ đồ thị và tô màu đường đi ngắn nhất."""
    G   = build_nx_graph(edges, directed)
    pos = nx.spring_layout(G, seed=42)
 
    path_edges = list(zip(path[:-1], path[1:]))
 
    node_colors = ['#FF6B6B' if n in path else 'skyblue' for n in G.nodes()]
    edge_colors = []
    for u, v in G.edges():
        if (u, v) in path_edges or (not directed and (v, u) in path_edges):
            edge_colors.append('#FF6B6B')
        else:
            edge_colors.append('#AAAAAA')
 
    edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}
 
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors,
            edge_color=edge_colors, node_size=700, font_size=12,
            arrows=directed, arrowsize=20, width=2)
    plt.title("Đường đi ngắn nhất (màu đỏ)")
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)
    plt.show()



#4. DUYỆT ĐỒ THỊ (BFS / DFS)
def bfs(G, start):
    """BFS - trả về (order, parent)"""
    visited, queue, order, parent = set(), deque([start]), [], {start: None}
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for nb in sorted(G.neighbors(node)):
                if nb not in visited and nb not in parent:
                    parent[nb] = node
                    queue.append(nb)
    return order, parent


def dfs(G, start):
    """DFS - trả về (order, parent)"""
    visited, order, parent = set(), [], {start: None}
    def visit(node):
        visited.add(node)
        order.append(node)
        for nb in sorted(G.neighbors(node)):
            if nb not in visited:
                parent[nb] = node
                visit(nb)
    visit(start)
    return order, parent


def draw_traversal(edges, directed, order, parent, title):
    """Vẽ đồ thị và làm nổi bật thứ tự duyệt + cây duyệt."""
    G   = build_nx_graph(edges, directed)
    pos = nx.spring_layout(G, seed=42)
    tree_edges  = [(parent[v], v) for v in parent if parent[v] is not None]
    cmap        = plt.cm.YlOrRd
    color_map   = {node: cmap(0.2 + 0.7 * i / max(len(order)-1, 1))
                   for i, node in enumerate(order)}
    node_colors = [color_map.get(n, (0.7, 0.9, 1.0, 1.0)) for n in G.nodes()]
    edge_colors = ['#E74C3C' if (u,v) in tree_edges or (not directed and (v,u) in tree_edges)
                   else '#CCCCCC' for u, v in G.edges()]
    labels      = {n: f"{n}\n(#{order.index(n)+1})" if n in order else n for n in G.nodes()}
    edge_labels = {(u,v): f"{d['weight']:.0f}" for u,v,d in G.edges(data=True)}
    plt.figure(figsize=(9, 6))
    nx.draw(G, pos, labels=labels, node_color=node_colors, edge_color=edge_colors,
            node_size=900, font_size=9, arrows=directed, arrowsize=20, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
    plt.title(f"{title}\nThứ tự: {' → '.join(order)}")
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)
    plt.show()


def traversal_menu(edges, directed):
    """Giao diện con cho phần duyệt đồ thị."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return

    G = build_nx_graph(edges, directed)
    print(f"Các đỉnh hiện có: {', '.join(sorted(G.nodes()))}")
    start = input("Nhập đỉnh bắt đầu duyệt: ").strip()

    if start not in G.nodes():
        print(f"✘ Đỉnh '{start}' không tồn tại trong đồ thị.")
        return

    print("\n  a. BFS\n  b. DFS\n  c. Cả hai")
    sub = input("Chọn: ").strip().lower()

    # Map lựa chọn → (hàm, tên)
    methods = {'a': (bfs, 'BFS'), 'b': (dfs, 'DFS')}
    to_run  = [('a', 'BFS'), ('b', 'DFS')] if sub == 'c' else [(sub, methods[sub][1])] if sub in methods else []

    if not to_run:
        print("Lựa chọn không hợp lệ.")
        return

    for key, name in to_run:
        fn = methods[key][0]
        order, parent = fn(G, start)
        if order:
            print(f"\n✔ {name} từ '{start}': {' → '.join(order)}")
            draw_traversal(edges, directed, order, parent, f"{name} từ đỉnh '{start}'")

#5. KIỂM TRA 1 ĐỒ THỊ CÓ PHẢI LÀ 2 PHÍA HAY KHÔNG?
def is_bipartite(edges):
    # Kiểm tra đồ thị có phải là đồ thị 2 phía không.
    #- Nếu 2 đỉnh kề nhau cùng màu → KHÔNG phải 2 phía
    #- Tô màu xong hết mà không xung đột → LÀ đồ thị 2 phía
    #Lưu ý: dùng đỉnh dạng chuỗi ("A","B",...) thay vì số nguyên
    # Xây dựng danh sách kề (vô hướng, không cần trọng số)
    graph = {}
    for u, v, w in edges:
        if u not in graph: graph[u] = []
        if v not in graph: graph[v] = []
        graph[u].append(v)
        graph[v].append(u)   # vô hướng → thêm cả 2 chiều
 
    color = {}   # {đỉnh: 0 hoặc 1} – thay mảng color[] trong demo
 
    for start in graph:
        if start not in color:          # chưa tô màu → bắt đầu BFS từ đây
            queue = deque([start])
            color[start] = 0
 
            while queue:
                u = queue.popleft()
                for v in graph[u]:
                    if v not in color:              # chưa tô → tô màu ngược
                        color[v] = 1 - color[u]
                        queue.append(v)
                    elif color[v] == color[u]:      # cùng màu → xung đột!
                        return False, color, graph
 
    return True, color, graph
 
 
def draw_bipartite(edges, color):
    """Vẽ đồ thị và tô 2 màu cho 2 tập đỉnh."""
    G  = build_nx_graph(edges, directed)
    pos = nx.spring_layout(G, seed=42)
 
    # Tập A (màu 0 → xanh dương), Tập B (màu 1 → cam)
    node_colors = ['#3498DB' if color.get(n) == 0 else '#E67E22' for n in G.nodes()]
 
    edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}
 
    # Tạo nhãn kèm tên tập
    set_A = sorted([n for n in color if color[n] == 0])
    set_B = sorted([n for n in color if color[n] == 1])
 
    plt.figure(figsize=(9, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors,
            node_size=800, font_size=12, font_color='white',
            width=2, edge_color='#888888')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.title(
        f"Đồ thị 2 phía ✔\n"
        f"Tập A (xanh): {{{', '.join(set_A)}}}    "
        f"Tập B (cam): {{{', '.join(set_B)}}}"
    )
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)
    plt.show()
 
 
def bipartite_menu(edges):
    """Giao diện con cho phần kiểm tra đồ thị 2 phía."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return
    if directed:
        print("⚠ Kiểm tra đồ thị 2 phía chỉ áp dụng cho đồ thị VÔ HƯỚNG.")
        print("  Đồ thị hiện tại là có hướng — kết quả có thể không chính xác.")

    result, color, graph = is_bipartite(edges)
 
    if result:
        set_A = sorted([n for n in color if color[n] == 0])
        set_B = sorted([n for n in color if color[n] == 1])
        print("\n✔ Đây LÀ đồ thị 2 phía!")
        print(f"   Tập A: {{{', '.join(set_A)}}}")
        print(f"   Tập B: {{{', '.join(set_B)}}}")
        draw_bipartite(edges, color)
    else:
        print("\n✘ Đây KHÔNG phải đồ thị 2 phía!")
        print("   (Tồn tại cạnh nối 2 đỉnh cùng tập)")

#6. CHUYỂN ĐỔI MA TRẬN KỀ → DANH SÁCH KỀ → DANH SÁCH CẠNH
def edges_to_adjacency_matrix(edges, directed):
    """
    Danh sách cạnh → Ma trận kề
    Ô [i][j] = trọng số nếu có cạnh, 0 nếu không có.
    Vô hướng: ma trận đối xứng. Có hướng: chỉ 1 chiều.
    """
    nodes = sorted(set(u for u, v, w in edges) | set(v for u, v, w in edges)) #Lấy danh sách đỉnh
    idx   = {node: i for i, node in enumerate(nodes)}
    n     = len(nodes)
    matrix = [[0] * n for _ in range(n)] #Gán trọng số vào ma trận
    for u, v, w in edges:
        matrix[idx[u]][idx[v]] = w
        if not directed:
            matrix[idx[v]][idx[u]] = w   # vô hướng → đối xứng
    return nodes, matrix
 
 
def edges_to_adjacency_list(edges, directed):
    """
    Danh sách cạnh → Danh sách kề
    {đỉnh: [(đỉnh_kề, trọng_số), ...]}
    """
    adj = {}
    for u, v, w in edges:
        if u not in adj: adj[u] = []
        if v not in adj: adj[v] = []
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))   # vô hướng → thêm chiều ngược
    return adj
 
 
# ── CHUYỂN TỪ Ma trận kề → các dạng khác ─────────────────
 
def adjacency_matrix_to_edges(nodes, matrix, directed):
    """Ma trận kề → Danh sách cạnh."""
    edges_out = []
    n = len(nodes)
    for i in range(n):
        # Có hướng: duyệt cả j, Vô hướng: chỉ j > i để tránh trùng
        start_j = 0 if directed else i + 1
        for j in range(start_j, n):
            if i != j and matrix[i][j] != 0:
                edges_out.append((nodes[i], nodes[j], matrix[i][j]))
    return edges_out
 
 
def adjacency_matrix_to_adj_list(nodes, matrix):
    """Ma trận kề → Danh sách kề."""
    adj = {node: [] for node in nodes}
    n   = len(nodes)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0:
                adj[nodes[i]].append((nodes[j], matrix[i][j]))
    return adj
 
 
# ── CHUYỂN TỪ Danh sách kề → các dạng khác ───────────────
 
def adj_list_to_edges(adj, directed):
    """Danh sách kề → Danh sách cạnh."""
    edges_out = []
    seen = set()
    for u in adj:
        for v, w in adj[u]:
            if directed:
                edges_out.append((u, v, w))   # có hướng → giữ nguyên chiều
            else:
                key = (min(u, v), max(u, v))  # vô hướng → tránh trùng (A,B) và (B,A)
                if key not in seen:
                    seen.add(key)
                    edges_out.append((u, v, w))
    return edges_out
 
 
def adj_list_to_matrix(adj):
    """Danh sách kề → Ma trận kề."""
    nodes = sorted(adj.keys())
    idx   = {node: i for i, node in enumerate(nodes)}
    n     = len(nodes)
    matrix = [[0] * n for _ in range(n)]
    for u in adj:
        for v, w in adj[u]:
            matrix[idx[u]][idx[v]] = w
    return nodes, matrix
 
 
# ── IN ĐẸP ────────────────────────────────────────────────
 
def print_adjacency_matrix(nodes, matrix):
    """In ma trận kề ra màn hình dạng bảng."""
    col_w = max(len(str(n)) for n in nodes) + 2   # độ rộng cột
    # Header
    print("\n  Ma trận kề:")
    header = " " * (col_w + 1) + "".join(f"{n:>{col_w}}" for n in nodes)
    print(header)
    print(" " * (col_w + 1) + "-" * (col_w * len(nodes)))
    for i, node in enumerate(nodes):
        row = f"{node:>{col_w}} |" + "".join(
            f"{int(matrix[i][j]) if matrix[i][j] == int(matrix[i][j]) else matrix[i][j]:>{col_w}}"
            for j in range(len(nodes))
        )
        print(row)
 
 
def print_adjacency_list(adj):
    """In danh sách kề ra màn hình."""
    print("\n  Danh sách kề:")
    for node in sorted(adj.keys()):
        neighbors = ", ".join(
            f"{v}(w={int(w) if w == int(w) else w})" for v, w in adj[node]
        )
        print(f"    {node}: [{neighbors}]")
 
 
def print_edge_list(edges_list):
    """In danh sách cạnh ra màn hình."""
    print("\n  Danh sách cạnh:")
    for u, v, w in edges_list:
        ww = int(w) if w == int(w) else w
        print(f"    ({u}, {v}, trọng_số={ww})")

#Menu phần 6
def representation_menu(edges, directed):
    """Giao diện con cho phần chuyển đổi biểu diễn."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return
 
    loai_str = "có hướng" if directed else "vô hướng"
 
    while True:
        print(f"\n  --- Chuyển đổi biểu diễn ({loai_str}) ---")
        print("  a. Xem tất cả 3 dạng")
        print("  b. Danh sách cạnh → Ma trận kề")
        print("  c. Danh sách cạnh → Danh sách kề")
        print("  d. Ma trận kề     → Danh sách kề")
        print("  e. Ma trận kề     → Danh sách cạnh")
        print("  f. Danh sách kề   → Ma trận kề")
        print("  g. Danh sách kề   → Danh sách cạnh")
        print("  0. Quay lại")
        sub = input("  Chọn: ").strip().lower()
 
        if sub == '0':
            break
 
        elif sub == 'a':
            nodes, matrix = edges_to_adjacency_matrix(edges, directed)
            adj           = edges_to_adjacency_list(edges, directed)
            print_edge_list(edges)
            print_adjacency_list(adj)
            print_adjacency_matrix(nodes, matrix)
 
        elif sub == 'b':
            nodes, matrix = edges_to_adjacency_matrix(edges, directed)
            print_adjacency_matrix(nodes, matrix)
 
        elif sub == 'c':
            adj = edges_to_adjacency_list(edges, directed)
            print_adjacency_list(adj)
 
        elif sub == 'd':
            nodes, matrix = edges_to_adjacency_matrix(edges, directed)
            adj = adjacency_matrix_to_adj_list(nodes, matrix)
            print_adjacency_list(adj)
 
        elif sub == 'e':
            nodes, matrix = edges_to_adjacency_matrix(edges, directed)
            edges_out     = adjacency_matrix_to_edges(nodes, matrix, directed)
            print_edge_list(edges_out)
 
        elif sub == 'f':
            adj           = edges_to_adjacency_list(edges, directed)
            nodes, matrix = adj_list_to_matrix(adj)
            print_adjacency_matrix(nodes, matrix)
 
        elif sub == 'g':
            adj       = edges_to_adjacency_list(edges, directed)
            edges_out = adj_list_to_edges(adj, directed)
            print_edge_list(edges_out)
 
        else:
            print("  Lựa chọn không hợp lệ.")

#PHẦN NÂNG CAO
#7.1 PRIM'S ALGORITHM (TÌM CÂY KHUNG NHỎ NHẤT)
def prim(graph, start):
    """Thuật toán Prim - tìm cây khung nhỏ nhất"""
    visited = set([start])
    edges_mst = []
    total_weight = 0

    pq = []
    for v, w in graph[start]:
        heapq.heappush(pq, (w, start, v))

    while pq:
        weight, u, v = heapq.heappop(pq)

        if v in visited:
            continue

        visited.add(v)
        edges_mst.append((u, v, weight))
        total_weight += weight

        for next_v, next_w in graph[v]:
            if next_v not in visited:
                heapq.heappush(pq, (next_w, v, next_v))

    return edges_mst, total_weight
#Vẽ cây khung nhỏ nhất
def draw_mst(edges, mst_edges):
    """Vẽ MST (cạnh đỏ)"""
    G = build_nx_graph(edges, False)
    pos = nx.spring_layout(G, seed=42)

    mst_set = {(u, v) for u, v, w in mst_edges}
    mst_set |= {(v, u) for u, v, w in mst_edges}

    edge_colors = []
    for u, v in G.edges():
        if (u, v) in mst_set:
            edge_colors.append('red')
        else:
            edge_colors.append('#CCCCCC')

    edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos,
            with_labels=True,
            node_color='skyblue',
            edge_color=edge_colors,
            node_size=700,
            font_size=12,
            width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Minimum Spanning Tree (Prim)")
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)
    plt.show()
#MENU PRIM
def prim_menu(edges):
    if not edges:
        print("Chưa có đồ thị.")
        return

    if directed:
        print("⚠ Prim chỉ dùng cho đồ thị vô hướng.")
        return

    graph = build_adj(edges, False)

    print(f"Các đỉnh: {', '.join(sorted(graph.keys()))}")
    start = input("Nhập đỉnh bắt đầu: ").strip()

    if start not in graph:
        print("Đỉnh không tồn tại.")
        return

    mst_edges, total = prim(graph, start)

    # ✅ Kiểm tra liên thông (đặt ĐÚNG chỗ)
    if len(mst_edges) != len(graph) - 1:
        print("⚠ Đồ thị KHÔNG liên thông → Không có MST đầy đủ")
    else:
        print("\n✔ Cây khung nhỏ nhất (MST):")
        for u, v, w in mst_edges:
            print(f"{u} - {v} (w={w})")

        print(f"Tổng trọng số: {total}")

    draw_mst(edges, mst_edges)

#7.2 KRUSKAL
class DisjointSet:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank   = {n: 0 for n in nodes}

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])  # nén đường
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u == root_v:
            return False  # tạo chu trình
        # union by rank
        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            self.parent[root_v] = root_u
            self.rank[root_u] += 1

        return True
def kruskal(edges):
    # edges: [(u, v, weight)]
    edges.sort(key=lambda x: x[2])  # sắp xếp theo trọng số

    nodes = set(u for u,v,w in edges) | set(v for u,v,w in edges)
    ds = DisjointSet(nodes)
    mst = []
    total_weight = 0

    for u, v, w in edges:
        if ds.union(u, v):
            mst.append((u, v, w))
            total_weight += w

    return mst, total_weight
def kruskal_menu(edges):
    if not edges:
        print("Chưa có đồ thị.")
        return
    if directed:
        print("⚠ Kruskal chỉ dùng cho đồ thị vô hướng.")
        return

    mst, total = kruskal(edges)

    if len(mst) != len(set(u for u,v,w in edges) | set(v for u,v,w in edges)) - 1:
        print("⚠ Đồ thị KHÔNG liên thông → Không có MST đầy đủ")
    else:
        print("\n✔ Cây khung nhỏ nhất (MST - Kruskal):")
        for u, v, w in mst:
            print(f"  {u} - {v} (w={w})")
        print(f"Tổng trọng số: {total}")

    draw_mst(edges, mst)   # dùng lại hàm draw_mst của Prim




#7.3 FORD-FULKERSON (TÌM LUỒNG CỰC ĐẠI)
def ford_fulkerson_menu():
    # Tạo đồ thị có hướng với dung lượng (capacity)
    G = nx.DiGraph()
    n = int(input("Nhập số cạnh (có dung lượng): "))
    for _ in range(n):
        u, v, c = input("Nhập cạnh (u v capacity): ").split()
        G.add_edge(u, v, capacity=int(c))

    s = input("Nhập đỉnh nguồn (source): ").strip()
    t = input("Nhập đỉnh đích (sink): ").strip()

    flow_value, flow_dict = nx.maximum_flow(G, s, t)
    print(f"✔ Giá trị luồng cực đại: {flow_value}")
    print("Chi tiết luồng:")
    for u in flow_dict:
        for v in flow_dict[u]:
            if flow_dict[u][v] > 0:
                print(f"  {u} → {v} : {flow_dict[u][v]}")

    # Vẽ trực quan
    pos = nx.spring_layout(G, seed=42)
    edge_labels = {(u, v): f"{d['capacity']}" for u, v, d in G.edges(data=True)}
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=700,
            arrows=True, arrowsize=20, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.title(f"Ford-Fulkerson: max flow = {flow_value}")
    plt.show()

#7.4 FLEURY (TÌM ĐƯỜNG ĐI EULER)
def fleury_menu(edges):
    """Tìm đường đi Euler bằng thuật toán Fleury."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return
    if directed:
        print("⚠ Fleury chỉ áp dụng cho đồ thị VÔ HƯỚNG.")
        return

    # Xây dựng danh sách kề từ edges chung (giữ nguyên cấu trúc code gốc)
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append(v)
        graph[v].append(u)

    def add_edge(u, v):
        graph[u].append(v)
        graph[v].append(u)

    def remove_edge(u, v):
        graph[u].remove(v)
        graph[v].remove(u)

    def dfs_fleury(v, visited):
        visited.add(v)
        count = 1
        for i in graph[v]:
            if i not in visited:
                count += dfs_fleury(i, visited)
        return count

    def is_valid_edge(u, v):
        if len(graph[u]) == 1:
            return True
        count1 = dfs_fleury(u, set())
        remove_edge(u, v)
        count2 = dfs_fleury(u, set())
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

    print(f"Các đỉnh hiện có: {', '.join(sorted(graph.keys()))}")
    start = input("Nhập đỉnh bắt đầu: ").strip()
    if start not in graph:
        print(f"✘ Đỉnh '{start}' không tồn tại.")
        return

    result = fleury(start)

    print("Đường đi Euler:")
    for u, v in result:
        print(f"  {u} → {v}")


#7.5 HIERHOLZER (TÌM ĐƯỜNG ĐI EULER)
def hierholzer_menu(edges):
    """Tìm đường đi Euler bằng thuật toán Hierholzer."""
    if not edges:
        print("Chưa có đồ thị. Hãy nhập hoặc tải đồ thị trước.")
        return
    if directed:
        print("⚠ Hierholzer chỉ áp dụng cho đồ thị VÔ HƯỚNG.")
        return

    # Xây dựng danh sách kề từ edges chung
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append(v)
        graph[v].append(u)

    # Kiểm tra điều kiện Euler
    odd_vertices = [v for v in graph if len(graph[v]) % 2 != 0]
    if len(odd_vertices) not in (0, 2):
        print(f"\n✘ Đồ thị KHÔNG có đường đi Euler!")
        print(f"   (Có {len(odd_vertices)} đỉnh bậc lẻ, cần 0 hoặc 2)")
        return

    print(f"Các đỉnh hiện có: {', '.join(sorted(graph.keys()))}")
    if len(odd_vertices) == 2:
        print(f"   Gợi ý: nên bắt đầu từ đỉnh bậc lẻ ({odd_vertices[0]} hoặc {odd_vertices[1]})")
    start = input("Nhập đỉnh bắt đầu: ").strip()
    if start not in graph:
        print(f"✘ Đỉnh '{start}' không tồn tại.")
        return

    # Thuật toán Hierholzer
    stack = [start]
    path  = []
    while stack:
        v = stack[-1]
        if graph[v]:              # còn cạnh → đi tiếp
            u = graph[v].pop()
            graph[u].remove(v)    # vô hướng → xóa cả chiều ngược
            stack.append(u)
        else:                     # hết cạnh → thêm vào đường đi
            path.append(stack.pop())
    path = path[::-1]

    # In kết quả
    print(f"\n✔ Đường đi Euler: {' → '.join(path)}")
#Main Chính
def main():
    global edges, directed
 
    while True:
        loai_str = "có hướng" if directed else "vô hướng"
        print(f"\n{'='*45}")
        print(f"   ĐỒ THỊ ({loai_str}) – {len(edges)} cạnh")
        print(f"{'='*45}")
        print("  1. Nhập đồ thị mới")
        print("  2. Lưu đồ thị vào file")
        print("  3. Tải đồ thị từ file")
        print("  4. Vẽ đồ thị trực quan")
        print("  5. Tìm đường đi ngắn nhất (Dijkstra)")
        print("  6. Duyệt đồ thị (BFS / DFS)")
        print("  7. Kiểm tra đồ thị 2 phía")
        print("  8. Chuyển đổi biểu diễn đồ thị")
        print("  --- Nâng cao ---")   
        print("  9. Prim (Minimum Spanning Tree)")
        print("  10. Kruskal (Minimum Spanning Tree)")
        print("  11. Trực quan hóa Ford-Fulkeron")
        print("  12. Fleury (Đường đi Euler)")
        print("  13. Hierholzer (Đường đi Euler)")
        print("  0. Thoát")
        print(f"{'='*45}")
 
        choice = input("Chọn: ").strip()
 
        if choice == '1':
            edges    = input_graph()
            print(f"✔ Đã nhập {len(edges)} cạnh.")
 
        elif choice == '2':
            if edges:
                save_graph(edges, directed)
            else:
                print("Chưa có đồ thị nào để lưu.")
 
        elif choice == '3':
            loaded = load_graph()
            if loaded:
                edges = loaded
 
        elif choice == '4':
            draw_graph(edges, directed)
 
        elif choice == '5':
            shortest_path_menu(edges, directed)
 
        elif choice == '6':
            traversal_menu(edges, directed)
 
        elif choice == '7':
            bipartite_menu(edges)

        elif choice == '8':
            representation_menu(edges, directed)

        elif choice == '9':
            prim_menu(edges)
 
        elif choice == '10':
            kruskal_menu(edges)
 
        elif choice == '11':
            ford_fulkerson_menu()
        
        elif choice == '12':
            fleury_menu(edges)

        elif choice == '13':
            hierholzer_menu(edges)

        elif choice == '0':
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, thử lại.")
 
 
if __name__ == "__main__":
    main()
        
  
