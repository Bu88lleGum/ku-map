from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.node import NodeCreate, NodeRead
from app.crud import crud_node

router = APIRouter()

@router.post("/", response_model=NodeRead)
def add_node(node_in: NodeCreate, session: Session = Depends(get_session)):
    return crud_node.create_node(session, node_in)

@router.get("/", response_model=list[NodeRead])
def read_nodes(session: Session = Depends(get_session)):
    return crud_node.get_nodes(session)


@router.get("/floor/{floor_id}", response_model=list[NodeRead])
def read_nodes_by_floor(floor_id: int, session: Session = Depends(get_session)):
    nodes = crud_node.get_nodes_by_floor(session, floor_id)
    if not nodes:
        return [] # Возвращаем пустой список, если этаж пуст
    return nodes