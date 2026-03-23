from sqlmodel import Session, select
from app.models.edge import Edge
from app.models.node import Node
from app.schemas.edge import EdgeCreate
from geoalchemy2.shape import to_shape
import math

def create_edge(session: Session, edge_in: EdgeCreate) -> Edge:
    node_from = session.get(Node, edge_in.source_node_id)
    node_to = session.get(Node, edge_in.target_node_id)
    
    if not node_from or not node_to:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Одна или обе точки не найдены")

    # Проверяем этаж (если ребро на одном этаже)
    # Если ребро соединяет этажи (лестница), логику можно усложнить
    edge_floor = node_from.floor 

    p1 = to_shape(node_from.geom)
    p2 = to_shape(node_to.geom)
    weight = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    db_edge = Edge(
        source_node_id=edge_in.source_node_id,
        target_node_id=edge_in.target_node_id, 
        type=edge_in.type,
        weight=weight,
        floor=edge_floor # Обязательное поле из твоей модели!
    )
    
    session.add(db_edge)
    session.commit()
    session.refresh(db_edge)
    return db_edge

def get_edges(session: Session):
    return session.exec(select(Edge)).all()

def get_edges_by_floor(session: Session, floor_id: int) -> list[Edge]:
    # Выбираем только те ребра, которые принадлежат указанному этажу
    statement = select(Edge).where(Edge.floor == floor_id)
    return session.exec(statement).all()