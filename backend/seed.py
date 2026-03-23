import geopandas as gpd
from sqlmodel import select, Session, create_engine, SQLModel, text
from app.models.node import Node
from app.models.edge import Edge
from app.models.wall import Wall
from app.core.database import DATABASE_URL
from app.models.enums import NodeType, EdgeType
from pathlib import Path

engine = create_engine(DATABASE_URL)
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DATA_PATH = SCRIPT_DIR / "data" / "processed"


def get_node_type(t: str) -> NodeType:
    t_clean = str(t).strip().lower()
    mapping = {
        "room": NodeType.ROOM,
        "hallway": NodeType.HALLWAY,
        "stairs": NodeType.STAIRS,
        "stair": NodeType.STAIRS,
        "elevator": NodeType.ELEVATOR
    }
    return mapping.get(t_clean, NodeType.HALLWAY)

def get_edge_type(t: str) -> EdgeType:
    mapping = {
        "Corridor": EdgeType.CORRIDOR,
        "Stairs": EdgeType.STAIRS,
        "Elevator": EdgeType.ELEVATOR,
        "Room": EdgeType.DOOR,
    }
    return mapping.get(t, EdgeType.CORRIDOR)

def find_node_id(coord, floor, coord_to_id, tolerance=0.2):
    """
    Поиск ID узла с учетом этажа и допуска.
    Ключ в словаре теперь: (x, y, floor)
    """
    x1, y1 = round(coord[0], 5), round(coord[1], 5)
    floor = int(floor)
    
    # 1. Пробуем точное совпадение
    exact_key = (x1, y1, floor)
    if exact_key in coord_to_id:
        return coord_to_id[exact_key]
    
    # 2. Поиск в радиусе tolerance на ТОМ ЖЕ этаже
    for (x2, y2, f2), node_id in coord_to_id.items():
        if f2 == floor:
            dist = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
            if dist <= tolerance:
                return node_id
    return None

def connect_stairs(session):
    print("--- Связывание лестниц между этажами ---")
    statement = select(Node).where(Node.type == NodeType.STAIRS)
    stair_nodes = session.exec(statement).all()
    
    # Группируем лестницы по координатам, чтобы связывать пролеты одной лестницы
    # (В вашем случае точка одна [51.31, 21.529], так что сработает корректно)
    stair_nodes.sort(key=lambda x: x.floor)

    for i in range(len(stair_nodes) - 1):
        n1, n2 = stair_nodes[i], stair_nodes[i+1]
        if n2.floor == n1.floor + 1:
            # Создаем двустороннюю связь между этажами
            session.add(Edge(source_node_id=n1.id, target_node_id=n2.id, floor=n1.floor, type=EdgeType.STAIRS, weight=15.0))
            session.add(Edge(source_node_id=n2.id, target_node_id=n1.id, floor=n2.floor, type=EdgeType.STAIRS, weight=10.0))

# --- ОСНОВНАЯ ФУНКЦИЯ ---

def seed_from_geojson():
    print("Подготовка базы данных...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    SQLModel.metadata.create_all(engine) 

    nodes_path = BASE_DATA_PATH / "nodes.geojson"
    edges_path = BASE_DATA_PATH / "edges.geojson"
    walls_path = BASE_DATA_PATH / "walls.geojson"

    with Session(engine) as session:
        print("Очистка таблиц...")
        session.execute(text("TRUNCATE TABLE node, edge, wall RESTART IDENTITY CASCADE;"))
        session.commit()

        # 1. Загрузка Узлов
        coord_to_id = {}
        if nodes_path.exists():
            gdf_nodes = gpd.read_file(nodes_path)
            print(f"Загрузка {len(gdf_nodes)} узлов...")
            for _, row in gdf_nodes.iterrows():
                x, y = row.geometry.x, row.geometry.y
                node = Node(
                    name=str(row['name']),
                    floor=int(row['floor']),
                    type=get_node_type(row['type']),
                    geom=f"SRID=3857;POINT({x} {y})"
                )
                session.add(node)
                # Ключ: (x, y, floor)
                coord_to_id[(round(x, 5), round(y, 5), int(row['floor']))] = node
        
        session.flush() # Получаем ID для существующих узлов
        for key, node_obj in coord_to_id.items():
            coord_to_id[key] = node_obj.id

        # 2. Загрузка Ребер + Авто-создание недостающих узлов
        if edges_path.exists():
            gdf_edges = gpd.read_file(edges_path)
            print(f"Обработка {len(gdf_edges)} ребер...")
            
            for _, row in gdf_edges.iterrows():
                coords = list(row.geometry.coords)
                floor = int(row['floor'])
                
                # Точки начала и конца линии
                p_start = coords[0]
                p_end = coords[-1]
                
                endpoint_ids = []
                for p in [p_start, p_end]:
                    node_id = find_node_id(p, floor, coord_to_id)
                    
                    if node_id is None:
                        # Если узла нет в nodes.geojson, создаем его автоматически (Hallway)
                        new_node = Node(
                            name=f"AutoNode_{floor}_{round(p[0], 1)}",
                            floor=floor,
                            type=NodeType.HALLWAY,
                            geom=f"SRID=3857;POINT({p[0]} {p[1]})"
                        )
                        session.add(new_node)
                        session.flush()
                        node_id = new_node.id
                        coord_to_id[(round(p[0], 5), round(p[1], 5), floor)] = node_id
                        print(f"Создан недостающий узел на этаже {floor}: {p}")
                    
                    endpoint_ids.append(node_id)

                # Добавляем само ребро (двустороннее для навигации)
                e_type = get_edge_type(row.get('type', 'Corridor'))
                weight = row.geometry.length
                
                session.add(Edge(source_node_id=endpoint_ids[0], target_node_id=endpoint_ids[1], 
                                 floor=floor, type=e_type, weight=weight))
                session.add(Edge(source_node_id=endpoint_ids[1], target_node_id=endpoint_ids[0], 
                                 floor=floor, type=e_type, weight=weight))

        # 3. Вертикальное связывание (лестницы)
        connect_stairs(session)

        # 4. Стены
        if walls_path.exists():
            gdf_walls = gpd.read_file(walls_path)
            for _, row in gdf_walls.iterrows():
                session.add(Wall(floor=int(row['floor']), geom=f"SRID=3857;{row.geometry.wkt}"))
        
        session.commit()
        print("Импорт завершен!")

if __name__ == "__main__":
    seed_from_geojson()