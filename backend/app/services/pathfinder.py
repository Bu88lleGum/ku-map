import math
import networkx as nx
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from geoalchemy2.shape import to_shape 

from app.models.node import Node
from app.models.edge import Edge

class PathfinderService:
    SCALE = 500 

    def __init__(self, session: Session):
        self.session = session
        self.G = nx.Graph()

    def is_peak_hour(self):
        """Проверка часа пик (например, обеденное время 12:00 - 13:00)"""
        # Устанавливаем время Казахстана (UTC+5)
        now = datetime.now(timezone(timedelta(hours=5)))
        # Час пик: с 12:00 до 13:00
        return now.hour == 12

    def load_graph_from_db(self):
        self.G.clear()

        nodes = self.session.exec(select(Node)).all()
        for node in nodes:
            point = to_shape(node.geom)
            self.G.add_node(
                node.id, 
                pos=(point.x, point.y), 
                floor=node.floor,
                name=node.name,
                type=node.type
            )

        peak = self.is_peak_hour()
        edges = self.session.exec(select(Edge)).all()
        
        for edge in edges:
            u = self.G.nodes.get(edge.source_node_id)
            v = self.G.nodes.get(edge.target_node_id)
            
            if not u or not v:
                continue

            edge_type = (edge.type or "").upper()

            if u['floor'] == v['floor']:
                # Обычный горизонтальный путь
                weight = math.sqrt((u['pos'][0] - v['pos'][0])**2 + (u['pos'][1] - v['pos'][1])**2)
            else:
                # МЕЖДУ ЭТАЖАМИ
                floor_diff = abs(u['floor'] - v['floor'])
                
                # Базовый штраф за ОДИН этаж в метрах
                if "STAIRS" in edge_type:
                    penalty_per_floor = 30  # Лестница тяжелее
                elif "ELEVATOR" in edge_type:
                    # В час пик лифт ждать очень долго
                    penalty_per_floor = 100 if peak else 15
                else:
                    penalty_per_floor = 20
                
                # Итоговый вес: штраф * кол-во этажей * SCALE
                weight = (penalty_per_floor * floor_diff) * self.SCALE

            self.G.add_edge(edge.source_node_id, edge.target_node_id, weight=weight, type=edge_type)

    def generate_instructions(self, path_data):
        if not path_data:
            return []

        instructions = [f"Начните путь от {path_data[0]['name']}"]
        
        for i in range(1, len(path_data)):
            curr = path_data[i]
            prev = path_data[i-1]
            
            if curr["floor"] > prev["floor"]:
                instructions.append(f"Поднимитесь на {curr['floor']} этаж")
            elif curr["floor"] < prev["floor"]:
                instructions.append(f"Спуститесь на {curr['floor']} этаж")
            elif curr.get("type") == "room" and i != len(path_data)-1:
                instructions.append(f"Пройдите через {curr['name']}")

        instructions.append(f"Прибытие в {path_data[-1]['name']}")
        
        # Убираем дубликаты идущих подряд этажей
        final_inst = []
        for inst in instructions:
            if not final_inst or inst != final_inst[-1]:
                final_inst.append(inst)
        return final_inst

    def find_path(self, start_id: int, end_id: int):
        # Всегда перезагружаем, если нужно учитывать время (час пик) динамически
        self.load_graph_from_db()

        try:
            path_ids = nx.shortest_path(self.G, source=start_id, target=end_id, weight="weight")
            raw_length = nx.shortest_path_length(self.G, source=start_id, target=end_id, weight="weight")
            
            meters = round(raw_length / self.SCALE, 2)
            # Если время в пути слишком маленькое для 10 этажей, 
            # значит SCALE или штрафы нужно еще подкрутить.
            seconds = round(meters / 1.1, 1) 

            detailed_path = []
            for node_id in path_ids:
                node_data = self.G.nodes[node_id]
                detailed_path.append({
                    "id": node_id,
                    "name": node_data.get("name"),
                    "x": node_data["pos"][0],
                    "y": node_data["pos"][1],
                    "floor": node_data["floor"],
                    "type": node_data.get("type")
                })

            return {
                "path_nodes": detailed_path,
                "length_meters": meters, 
                "time_seconds": seconds,
                "peak_hour_active": self.is_peak_hour(),
                "instructions": self.generate_instructions(detailed_path),
                "geom_wkt": f"LINESTRING({', '.join([f'{n['x']} {n['y']}' for n in detailed_path])})"
            }

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None