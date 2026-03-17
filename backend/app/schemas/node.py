from pydantic import BaseModel
from app.models.enums import NodeType

class NodeBase(BaseModel):
    name: str
    floor: int
    type: NodeType

class NodeCreate(NodeBase):
    x: float
    y: float

class NodeRead(NodeBase):
    id: int
    # Мы будем возвращать x и y отдельно для удобства фронтенда
    x: float
    y: float

    class Config:
        from_attributes = True