import { Node, PathResult, Edge } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

export const api = {
  getNodes: async (): Promise<Node[]> => {
    const res = await fetch(`${BASE_URL}/nodes/`);
    if (!res.ok) throw new Error('Failed to fetch nodes');
    return res.json();
  },

  getNodesByFloor: async (floor: number): Promise<Node[]> => {
    const res = await fetch(`${BASE_URL}/nodes/floor/${floor}`);
    if (!res.ok) throw new Error('Failed to fetch nodes');
    return res.json();
  },

  getEdgesByFloor: async (floor: number): Promise<Edge[]> => {
    const res = await fetch(`${BASE_URL}/edges/floor/${floor}`);
    if (!res.ok) throw new Error('Failed to fetch edges');
    return res.json();
  },

  calculatePath: async (startId: number, endId: number): Promise<PathResult> => {
    const res = await fetch(
      `${BASE_URL}/navigation/calculate-path?start_id=${startId}&end_id=${endId}`
    );
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail?.detail ?? 'Путь не найден');
    }
    return res.json();
  },
};
