from sqlmodel import SQLModel, Field, Column, Relationship
from geoalchemy2 import Geometry
from typing import List, TYPE_CHECKING
from .enums import NodeType

if TYPE_CHECKING:
    from .edge import Edge

class Node(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    floor: int = Field(index=True)
    type: NodeType = Field(default=NodeType.ROOM)

    # POINT(x y)
    geom: str = Field(sa_column=Column(Geometry("POINT", srid=3857)))


    outgoing_edges: List["Edge"] = Relationship(
        back_populates="source_node", 
        sa_relationship_kwargs={"primaryjoin": "Node.id==Edge.source_node_id"}
    )
    incoming_edges: List["Edge"] = Relationship(
        back_populates="target_node", 
        sa_relationship_kwargs={"primaryjoin": "Node.id==Edge.target_node_id"}
    )