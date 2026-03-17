import networkx as nx
from sqlmodel import Session, select
from app.models.node import Node
from app.models.edge import Edge
from app.models.wall import Wall
from geoalchemy2.shape import to_shape # Поможет превратить геометрию в объект Python

class PathfinderService:
    def __init__(self, session: Session):
        self.session = session
        self.G = nx.Graph()

    def load_graph_from_db(self):
        """Загружает все данные из БД и строит граф NetworkX"""
        self.G.clear()

        # 1. Загружаем все узлы
        nodes = self.session.exec(select(Node)).all()
        for node in nodes:
            # to_shape(node.geom) превращает Point в объект с .x и .y
            point = to_shape(node.geom)
            self.G.add_node(
                node.id, 
                pos=(point.x, point.y), 
                floor=node.floor,
                name=node.name
            )

        # 2. Загружаем все ребра
        edges = self.session.exec(select(Edge)).all()
        for edge in edges:
            self.G.add_edge(
                edge.source_node_id, 
                edge.target_node_id, 
                weight=edge.weight,
                type=edge.type
            )

    def find_path(self, start_id: int, end_id: int):
        # Если граф пуст (например, первый запуск), загружаем его
        if not self.G.nodes:
            self.load_graph_from_db()

        try:
            path_ids = nx.shortest_path(self.G, source=start_id, target=end_id, weight="weight")
            length = nx.shortest_path_length(self.G, source=start_id, target=end_id, weight="weight")
            
            detailed_path = []
            for node_id in path_ids:
                node_data = self.G.nodes[node_id]
                detailed_path.append({
                    "id": node_id,
                    "name": node_data.get("name"),
                    "x": node_data["pos"][0],
                    "y": node_data["pos"][1],
                    "floor": node_data["floor"]
                })

            return {
                "path_nodes": detailed_path,
                "length": round(length, 2),
                "time_seconds": round(length / 1.2, 1) # Примерная скорость 1.2 м/с
            }
        except nx.NetworkXNoPath:
            return None