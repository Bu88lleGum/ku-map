from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.crud import crud_edge
from app.schemas.edge import EdgeCreate, EdgeRead

router = APIRouter()

@router.post("/", response_model=EdgeRead)
def create_edge(edge_in: EdgeCreate, session: Session = Depends(get_session)):
    return crud_edge.create_edge(session, edge_in)

@router.get("/", response_model=list[EdgeRead])
def read_edges(session: Session = Depends(get_session)):
    return crud_edge.get_edges(session)