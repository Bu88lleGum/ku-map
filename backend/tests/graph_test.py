import networkx as nx
import json
import math
import matplotlib.pyplot as plt

def intersect(a, b, c, d):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)

def get_dist(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Загрузка
with open("map_data.json", "r") as f:
    data = json.load(f)

G = nx.Graph()

for node in data["nodes"]:
    G.add_node(node["id"], pos=(node["x"], node["y"]), floor=node["floor"])

walls = [(w["p1"], w["p2"]) for w in data.get("walls", [])]

# Построение графа с расчетом штрафа
for edge in data["edges"]:
    u, v = edge["from"], edge["to"]
    node_u = G.nodes[u]
    node_v = G.nodes[v]
    p1, p2 = node_u['pos'], node_v['pos']
    
    # Проверка на стены (только если на одном этаже)
    blocked = False
    if node_u['floor'] == node_v['floor']:
        for wall in walls:
            if intersect(p1, p2, wall[0], wall[1]):
                blocked = True
                break
    
    if not blocked:
        # ЛОГИКА ШТРАФА: если этажи разные, ставим вес 15, иначе - считаем метры
        if node_u['floor'] != node_v['floor']:
            dist = 15.0 
            print(f"Добавлен переход между этажами: {u} <-> {v} (Штраф: {dist}м)")
        else:
            dist = get_dist(p1, p2)
            
        G.add_edge(u, v, weight=dist)

# Поиск пути
start, end = "Room_1", "Room_201"
try:
    path = nx.shortest_path(G, source=start, target=end, weight="weight")
    length = nx.shortest_path_length(G, source=start, target=end, weight="weight")
    # Расчет времени для ВСЕГО пути
    speed = 1.2 # м/с
    total_time = length / speed
    print(f"\nИТОГОВЫЙ ПУТЬ: {path}")
    print(f"Общая дистанция (с учетом штрафов): {length:.2f}м")
    print(f"Примерное время в пути: {total_time:.1f} сек")
except nx.NetworkXNoPath:
    print("Путь не найден!")
# --- ВИЗУАЛИЗАЦИЯ ---
pos = nx.get_node_attributes(G, 'pos')
plt.figure(figsize=(10, 8))

# 1. Рисуем стены (черным)
for wall in walls:
    plt.plot([wall[0][0], wall[1][0]], [wall[0][1], wall[1][1]], 'k-', lw=5, label="Wall")

# 2. Рисуем все возможные ребра графа (те, что НЕ перекрыты)
nx.draw_networkx_edges(G, pos, width=1, edge_color='blue', alpha=0.3, style='dashed')

# 3. Рисуем узлы
nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
nx.draw_networkx_labels(G, pos)

# 4. Если путь существует — рисуем его красным
if path:
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=5, edge_color='red')
    plt.title(f"Путь найден: {start} -> {end}")
else:
    plt.title(f"ПУТЬ ЗАБЛОКИРОВАН СТЕНАМИ", color='red')

plt.grid(True)
plt.show()