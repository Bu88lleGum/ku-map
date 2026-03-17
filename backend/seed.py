from sqlmodel import Session, create_engine
from app.models.node import Node
from app.models.edge import Edge
from app.core.database import DATABASE_URL
from app.models.enums import NodeType, EdgeType

engine = create_engine(DATABASE_URL)

def seed_data():
    with Session(engine) as session:
        # 1. Создаем два узла (например, Кабинет 101 и Выход)
        n1 = Node(
            name="Room 101", 
            floor=1, 
            type=NodeType.ROOM,
            geom="POINT(30.5 50.5)" # Координаты внутри здания
        )
        n2 = Node(
            name="Hallway Exit", 
            floor=1, 
            type=NodeType.HALLWAY,
            geom="POINT(32.0 50.5)"
        )
        
        session.add(n1)
        session.add(n2)
        session.flush() # Получаем ID узлов

        # 2. Соединяем их ребром
        e1 = Edge(
            source_node_id=n1.id,
            target_node_id=n2.id,
            floor=1,
            type=EdgeType.CORRIDOR,
            weight=1.5
        )
        
        session.add(e1)
        session.commit()
        print("Данные успешно добавлены!")

if __name__ == "__main__":
    seed_data()