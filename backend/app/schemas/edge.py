from pydantic import BaseModel
from app.models.enums import EdgeType

class EdgeBase(BaseModel):
    source_node_id: int
    target_node_id: int
    type: EdgeType = EdgeType.CORRIDOR
    floor: int

class EdgeCreate(EdgeBase):
    pass

class EdgeRead(EdgeCreate):
    id: int
    weight: float

    class Config:
        from_attributes = True