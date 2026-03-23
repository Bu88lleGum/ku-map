from enum import Enum

class EdgeType(str, Enum):
    CORRIDOR = "corridor"
    STAIRS = "stairs"
    ELEVATOR = "elevator"
    DOOR = "door"

class NodeType(str, Enum):
    ROOM = "room"
    STAIRS = "stairs"
    HALLWAY = "hallway"
    INFO_TERMINAL = "info terminal"
    ELEVATOR = "elevator"