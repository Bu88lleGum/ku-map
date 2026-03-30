import React, { useEffect, useState, useCallback } from 'react';
import { useNavigation } from './hooks/useNavigation';
import { FloorMap } from './components/FloorMap';
import { NodeSelector } from './components/NodeSelector';
import { PathInfo } from './components/PathInfo';

const FLOORS = [1, 2, 3];

function SkeletonBlock({ className }: { className?: string }) {
  return (
    <div className={`rounded-lg bg-slate-800/60 animate-pulse ${className ?? ''}`} />
  );
}

export default function App() {
  const { nodes, pathResult, loading, error, loadNodes, findPath, clearPath } = useNavigation();
  const [nodesLoading, setNodesLoading] = useState(true);
  const [startId, setStartId] = useState<number | null>(null);
  const [endId, setEndId] = useState<number | null>(null);
  const [activeFloor, setActiveFloor] = useState<number>(1);

  useEffect(() => {
    setNodesLoading(true);
    loadNodes().finally(() => setNodesLoading(false));
  }, [loadNodes]);

  // Auto-switch to floor where path starts
  useEffect(() => {
    if (pathResult && pathResult.path_nodes.length > 0) {
      setActiveFloor(pathResult.path_nodes[0].floor);
    }
  }, [pathResult]);

  const floorsWithPath = pathResult
    ? [...new Set(pathResult.path_nodes.map((n) => n.floor))].sort()
    : [];

  const handleFind = useCallback(() => {
    if (startId && endId) findPath(startId, endId);
  }, [startId, endId, findPath]);

  const handleSwap = useCallback(() => {
    setStartId(endId);
    setEndId(startId);
    clearPath();
  }, [startId, endId, clearPath]);

  const handleClear = useCallback(() => {
    clearPath();
    setStartId(null);
    setEndId(null);
  }, [clearPath]);

  // Keyboard shortcut: Enter to find path
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && startId && endId && !loading) handleFind();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [startId, endId, loading, handleFind]);

  return (
    <div className="min-h-screen h-screen flex flex-col bg-[#080c14] text-white overflow-hidden"
      style={{ fontFamily: "'IBM Plex Mono', monospace" }}>

      {/* ── Header ── */}
      <header className="flex-shrink-0 border-b border-slate-800/70 px-5 h-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded-md bg-blue-500/15 border border-blue-500/35 flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <span className="text-sm font-semibold tracking-[0.18em] uppercase text-white">KuMap</span>
          <span className="hidden sm:inline text-xs text-slate-600 tracking-widest">
            / {nodes.length > 0 ? `${nodes.length} узлов` : 'загрузка...'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${nodes.length > 0 ? 'bg-emerald-400' : 'bg-slate-600'} ${nodes.length > 0 ? 'animate-pulse' : ''}`} />
          <span className="text-xs text-slate-500">
            {nodes.length > 0 ? 'API online' : 'connecting...'}
          </span>
        </div>
      </header>

      {/* ── Body ── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Sidebar ── */}
        <aside className="w-72 flex-shrink-0 border-r border-slate-800/70 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">

            {/* Node selectors */}
            {nodesLoading ? (
              <div className="space-y-4">
                <div>
                  <SkeletonBlock className="w-16 h-3 mb-2" />
                  <SkeletonBlock className="w-full h-11" />
                </div>
                <div>
                  <SkeletonBlock className="w-12 h-3 mb-2" />
                  <SkeletonBlock className="w-full h-11" />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <NodeSelector
                  nodes={nodes}
                  value={startId}
                  onChange={(id) => { setStartId(id); clearPath(); }}
                  placeholder="Начальная точка"
                  label="Откуда"
                  accentColor="#22c55e"
                />

                {/* Swap button */}
                <div className="flex justify-center">
                  <button
                    onClick={handleSwap}
                    disabled={!startId && !endId}
                    className="w-8 h-8 rounded-full border border-slate-700 bg-slate-800/60 hover:border-slate-500 hover:bg-slate-700/60 text-slate-400 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed text-sm flex items-center justify-center"
                    title="Поменять местами"
                  >
                    ⇅
                  </button>
                </div>

                <NodeSelector
                  nodes={nodes}
                  value={endId}
                  onChange={(id) => { setEndId(id); clearPath(); }}
                  placeholder="Конечная точка"
                  label="Куда"
                  accentColor="#ef4444"
                />
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={handleFind}
                disabled={!startId || !endId || loading || nodesLoading}
                className="flex-1 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-35 disabled:cursor-not-allowed text-sm font-semibold tracking-wider transition-all active:scale-[0.98] flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Поиск...
                  </>
                ) : 'Построить путь'}
              </button>
              {(pathResult || startId || endId) && (
                <button
                  onClick={handleClear}
                  className="px-3 py-2.5 rounded-lg border border-slate-700/80 hover:border-slate-500 text-slate-400 hover:text-white text-sm transition-all"
                  title="Очистить"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Keyboard hint */}
            {startId && endId && !loading && !pathResult && (
              <p className="text-center text-[10px] text-slate-600">
                или нажмите <kbd className="px-1 py-0.5 rounded border border-slate-700 text-slate-500">Enter</kbd>
              </p>
            )}

            {/* Error */}
            {error && (
              <div className="px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/25 text-red-400 text-xs leading-relaxed">
                <span className="font-semibold">Ошибка: </span>{error}
              </div>
            )}

            {/* Path info */}
            {pathResult && (
              <div className="border-t border-slate-800/60 pt-4">
                <PathInfo result={pathResult} />
              </div>
            )}

            {/* Empty state */}
            {!pathResult && !loading && !error && !nodesLoading && (
              <div className="py-8 text-center space-y-3">
                <div className="text-3xl opacity-20 select-none">⬡</div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Выберите начальную<br />и конечную точку
                </p>
              </div>
            )}
          </div>
        </aside>

        {/* ── Map area ── */}
        <main className="flex-1 flex flex-col overflow-hidden bg-[#080c14]">

          {/* Floor tabs */}
          <div className="flex-shrink-0 flex items-end gap-0.5 px-4 pt-3 border-b border-slate-800/70">
            {FLOORS.map((floor) => {
              const hasPath = floorsWithPath.includes(floor);
              const isActive = activeFloor === floor;
              return (
                <button
                  key={floor}
                  onClick={() => setActiveFloor(floor)}
                  className={`relative px-5 py-2 text-xs font-semibold tracking-[0.12em] uppercase rounded-t-lg transition-all ${
                    isActive
                      ? 'bg-slate-800/80 text-white border border-b-0 border-slate-700/60'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'
                  }`}
                >
                  Этаж {floor}
                  {hasPath && (
                    <span
                      className={`ml-2 inline-block w-1.5 h-1.5 rounded-full ${
                        isActive ? 'bg-blue-400 animate-pulse' : 'bg-blue-600'
                      }`}
                    />
                  )}
                </button>
              );
            })}
          </div>

          {/* Map canvas */}
          <div className="flex-1 p-4 overflow-hidden">
            <FloorMap
              floor={activeFloor}
              pathNodes={pathResult?.path_nodes ?? []}
              allNodes={nodes}
            />
          </div>

          {/* Cross-floor hint */}
          {floorsWithPath.length > 1 && (
            <div className="flex-shrink-0 px-4 pb-3 flex items-center gap-2">
              <span className="text-amber-400 text-xs">⬆</span>
              <span className="text-xs text-slate-500">
                Маршрут проходит по этажам{' '}
                <span className="text-slate-300 font-semibold">{floorsWithPath.join(', ')}</span>
                {' '}— переключайтесь между вкладками
              </span>
              <div className="ml-auto flex gap-1">
                {floorsWithPath.map((f) => (
                  <button key={f} onClick={() => setActiveFloor(f)}
                    className={`px-2 py-0.5 rounded text-[10px] font-mono transition-all ${
                      activeFloor === f
                        ? 'bg-blue-600/30 text-blue-300 border border-blue-500/40'
                        : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-500'
                    }`}>
                    {f}
                  </button>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
