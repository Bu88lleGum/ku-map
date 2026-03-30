import { useState, useCallback } from 'react';
import { api } from '../api';
import { Node, PathResult } from '../types';

export function useNavigation() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [pathResult, setPathResult] = useState<PathResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNodes = useCallback(async () => {
    try {
      const data = await api.getNodes();
      setNodes(data);
    } catch {
      setError('Не удалось загрузить список узлов');
    }
  }, []);

  const findPath = useCallback(async (startId: number, endId: number) => {
    setLoading(true);
    setError(null);
    setPathResult(null);
    try {
      const result = await api.calculatePath(startId, endId);
      setPathResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Путь не найден');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearPath = useCallback(() => {
    setPathResult(null);
    setError(null);
  }, []);

  return { nodes, pathResult, loading, error, loadNodes, findPath, clearPath };
}
