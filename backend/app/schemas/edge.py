from pydantic import BaseModel
from app.models.enums import EdgeType

class EdgeCreate(BaseModel):
    source_node_id: int
    target_node_id: int
    type: EdgeType = EdgeType.CORRIDOR

class EdgeRead(EdgeCreate):
    id: int
    weight: float

    class Config:
        from_attributes = True