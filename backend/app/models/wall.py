from sqlmodel import SQLModel, Field, Column
from geoalchemy2 import Geometry
from sqlalchemy import Any

class Wall(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    floor: int = Field(index=True)
    # LINESTRING(x1 y1, x2 y2)
    # geom: str = Field(sa_column=Column(Geometry("LINESTRING")))
    geom: Any = Field(
        sa_column=Column(
            Geometry(geometry_type="POLYGON", srid=3857)
        )
    )