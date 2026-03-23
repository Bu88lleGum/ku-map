import networkx as nx
from sqlmodel import Session, select
from app.models.node import Node
from app.models.edge import Edge
# to_shape превращает бинарные данные PostGIS в объект с .x и .y
from geoalchemy2.shape import to_shape 

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
            point = to_shape(node.geom)
            self.G.add_node(
                node.id, 
                pos=(point.x, point.y), 
                floor=node.floor,
                name=node.name,
                type=node.type # 'Room', 'Stair', 'Hallway' и т.д.
            )

        # 2. Загружаем все ребра (связи)
        # В методе load_graph_from_db
        edges = self.session.exec(select(Edge)).all()
        for edge in edges:
            weight = edge.weight
            # Приводим к нижнему регистру для надежности
            edge_type = edge.type.lower() if edge.type else ""

            if edge_type == "stairs" and (weight is None or weight < 0.1):
                weight = 15.0 
            if edge_type == "elevator" and (weight is None or weight < 0.1):
                weight = 10.0 
            
            self.G.add_edge(
                edge.source_node_id, 
                edge.target_node_id, 
                weight=weight or 1.0, 
                type=edge.type
            )
    def generate_instructions(self, path_data):
        """Создает детальный пошаговый гид"""
        if not path_data:
            return []

        instructions = [f"Начните путь от {path_data[0]['name']}"]
        
        for i in range(1, len(path_data) - 1):
            curr = path_data[i]
            prev = path_data[i-1]
            
            # Проверяем переход по этажам
            if curr["floor"] > prev["floor"]:
                instructions.append(f"Поднимитесь на {curr['floor']} этаж")
            elif curr["floor"] < prev["floor"]:
                instructions.append(f"Спуститесь на {curr['floor']} этаж")
            else:
                # Просто перечисляем точки на одном этаже
                instructions.append(f"Проследуйте через {curr['name']}")

        instructions.append(f"Прибытие в {path_data[-1]['name']}")
        return instructions
    
    def find_path(self, start_id: int, end_id: int):
        if not self.G.nodes:
            self.load_graph_from_db()

        try:
            # Вычисляем кратчайший путь (список ID узлов)
            path_ids = nx.shortest_path(self.G, source=start_id, target=end_id, weight="weight")
            length = nx.shortest_path_length(self.G, source=start_id, target=end_id, weight="weight")
            
            detailed_path = []
            for node_id in path_ids:
                node_data = self.G.nodes[node_id]
                detailed_path.append({
                    "id": node_id,
                    "name": node_data.get("name") or f"Точка {node_id}",
                    "x": node_data["pos"][0],
                    "y": node_data["pos"][1],
                    "floor": node_data["floor"]
                })

            # Формируем геометрию для фронтенда (LineString)
            # Это строка вида 'LINESTRING(x1 y1, x2 y2, ...)'
            geom_points = [f"{n['x']} {n['y']}" for n in detailed_path]
            path_wkt = f"LINESTRING({', '.join(geom_points)})"

            return {
                "path_nodes": detailed_path, # Полные данные объектов
                "length_meters": round(length, 2),
                "time_seconds": round(length / 1.2, 1), 
                "points": [n["name"] for n in detailed_path], # Твой список A -> B -> C
                "instructions": self.generate_instructions(detailed_path), # Текстовый гид
                "geom_wkt": path_wkt # Строка для отрисовки на карте
            }

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None