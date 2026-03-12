import networkx as nx
import math

class PathfinderService:
    def __init__(self):
        self.G = nx.Graph()
        self.walls = []

    def _intersect(self, a, b, c, d):
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)

    def build_graph(self, data):
        self.G.clear()
        # Загружаем узлы
        for node in data["nodes"]:
            self.G.add_node(node["id"], pos=(node["x"], node["y"]), floor=node["floor"])
        
        self.walls = [(w["p1"], w["p2"]) for w in data.get("walls", [])]

        # Строим ребра
        for edge in data["edges"]:
            u, v = edge["from"], edge["to"]
            node_u, node_v = self.G.nodes[u], self.G.nodes[v]
            
            blocked = False
            if node_u['floor'] == node_v['floor']:
                for wall in self.walls:
                    if self._intersect(node_u['pos'], node_v['pos'], wall[0], wall[1]):
                        blocked = True
                        break
            
            if not blocked:
                weight = 15.0 if node_u['floor'] != node_v['floor'] else \
                         math.dist(node_u['pos'], node_v['pos'])
                self.G.add_edge(u, v, weight=weight)

    def find_path(self, start_id, end_id):
        try:
            # 1. Находим кратчайший путь (список ID)
            path_ids = nx.shortest_path(self.G, source=start_id, target=end_id, weight="weight")
            length = nx.shortest_path_length(self.G, source=start_id, target=end_id, weight="weight")
            
            # 2. Собираем подробные данные о каждой точке пути для фронтенда
            detailed_path = []
            for node_id in path_ids:
                node_data = self.G.nodes[node_id]
                detailed_path.append({
                    "id": node_id,
                    "x": node_data["pos"][0],
                    "y": node_data["pos"][1],
                    "floor": node_data["floor"]
                })

            return {
                "path_nodes": detailed_path, # Теперь тут полные данные
                "length": round(length, 2),
                "time": round(length / 1.2, 1)
            }
        except nx.NetworkXNoPath:
            return None