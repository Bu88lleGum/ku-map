from sqlmodel import SQLModel, Field, Relationship
from .enums import EdgeType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node

class Edge(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_node_id: int = Field(foreign_key="node.id")
    target_node_id: int = Field(foreign_key="node.id")
    floor: int = Field(index=True)
    
    type: EdgeType = Field(default=EdgeType.CORRIDOR)

    weight: float = Field(default=1.0) # Расстояние или время прохождения

    source_node: "Node" = Relationship(
        back_populates="outgoing_edges",
        sa_relationship_kwargs={"primaryjoin": "Edge.source_node_id==Node.id"}
    )
    target_node: "Node" = Relationship(
        back_populates="incoming_edges",
        sa_relationship_kwargs={"primaryjoin": "Edge.target_node_id==Node.id"}
    )