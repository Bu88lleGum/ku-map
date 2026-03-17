from sqlmodel import SQLModel, Field, Column
from geoalchemy2 import Geometry

class Wall(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    floor: int = Field(index=True)
    # LINESTRING(x1 y1, x2 y2)
    geom: str = Field(sa_column=Column(Geometry("LINESTRING")))