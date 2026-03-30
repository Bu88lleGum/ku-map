export interface Node {
  id: number;
  name: string;
  x: number;
  y: number;
  floor: number;
  type?: 'room' | 'hallway' | 'stairs';
}

export interface PathNode {
  id: number;
  name: string;
  x: number;
  y: number;
  floor: number;
}

export interface PathResult {
  path_nodes: PathNode[];
  length_meters: number;
  time_seconds: number;
  points: string[];
  instructions: string[];
  geom_wkt: string;
}

export interface Edge {
  id: number;
  from_node_id: number;
  to_node_id: number;
  floor: number;
}
