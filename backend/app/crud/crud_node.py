from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.node import Node
from app.schemas.node import NodeCreate
from geoalchemy2.shape import to_shape

def create_node(session: Session, node_in: NodeCreate) -> dict:
    # 1. Сначала проверяем, есть ли такое имя в базе
    existing = session.exec(select(Node).where(Node.name == node_in.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Точка с именем '{node_in.name}' уже существует")

    # 2. Только если имени нет — создаем объект
    db_node = Node(
        name=node_in.name,
        floor=node_in.floor,
        type=node_in.type,
        geom=f"POINT({node_in.x} {node_in.y})"
    )
    
    session.add(db_node)
    session.commit()
    session.refresh(db_node)

    # 3. Формируем ответ
    point = to_shape(db_node.geom)
    node_data = db_node.model_dump()
    node_data.update({
        "x": point.x,
        "y": point.y
    })
    
    return node_data

def get_nodes(session: Session) -> list[dict]:
    statement = select(Node)
    db_nodes = session.exec(statement).all()
    
    results = []
    for node in db_nodes:
        if node.geom:
            point = to_shape(node.geom)
            node_data = node.model_dump() 
            node_data["x"] = point.x
            node_data["y"] = point.y
            results.append(node_data)
        
    return results