import React, { useRef, useEffect, useState, useCallback } from 'react';
import { PathNode, Node } from '../types';

interface FloorMapProps {
  floor: number;
  pathNodes: PathNode[];
  allNodes: Node[];
}

const FLOOR_IMAGES: Record<number, string> = {
  1: '/images/floor1.png',
  2: '/images/floor2.png',
  3: '/images/floor3.png',
};

function getBounds(nodes: Node[]) {
  if (nodes.length === 0) return { minX: -5, maxX: 70, minY: 5, maxY: 50 };
  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const pad = 6;
  return {
    minX: Math.min(...xs) - pad,
    maxX: Math.max(...xs) + pad,
    minY: Math.min(...ys) - pad,
    maxY: Math.max(...ys) + pad,
  };
}

function toSvg(x: number, y: number, b: ReturnType<typeof getBounds>, vw: number, vh: number) {
  return {
    cx: ((x - b.minX) / (b.maxX - b.minX)) * vw,
    cy: ((y - b.minY) / (b.maxY - b.minY)) * vh,
  };
}

interface Transform { x: number; y: number; scale: number }

export const FloorMap: React.FC<FloorMapProps> = ({ floor, pathNodes, allNodes }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ w: 900, h: 560 });
  const [tf, setTf] = useState<Transform>({ x: 0, y: 0, scale: 1 });
  const [imgLoaded, setImgLoaded] = useState(false);
  const [animKey, setAnimKey] = useState(0);
  const dragging = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setDims({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    setDims({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    setTf({ x: 0, y: 0, scale: 1 });
    setAnimKey((k) => k + 1);
    setImgLoaded(false);
  }, [floor, pathNodes.length]);

  const VW = 1000;
  const VH = 620;
  const bounds = getBounds(allNodes);

  const floorPath = pathNodes.filter((n) => n.floor === floor);
  const floorAll  = allNodes.filter((n) => n.floor === floor);

  const pts = floorPath.map((n) => toSvg(n.x, n.y, bounds, VW, VH));
  const poly = pts.map((p) => `${p.cx},${p.cy}`).join(' ');
  const totalLen = pts.reduce((acc, p, i) => {
    if (i === 0) return 0;
    const q = pts[i - 1];
    return acc + Math.hypot(p.cx - q.cx, p.cy - q.cy);
  }, 0);

  // Zoom toward cursor
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.85 : 1.18;
    setTf((t) => {
      const s = Math.max(0.5, Math.min(6, t.scale * delta));
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return t;
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      return { scale: s, x: mx - (mx - t.x) * (s / t.scale), y: my - (my - t.y) * (s / t.scale) };
    });
  }, []);

  const onDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    dragging.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current) return;
    const dx = e.clientX - lastPos.current.x;
    const dy = e.clientY - lastPos.current.y;
    lastPos.current = { x: e.clientX, y: e.clientY };
    setTf((t) => ({ ...t, x: t.x + dx, y: t.y + dy }));
  }, []);

  const onUp = useCallback(() => { dragging.current = false; }, []);

  const resetView = () => setTf({ x: 0, y: 0, scale: 1 });

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full overflow-hidden rounded-xl bg-[#0b1018] select-none"
      style={{ cursor: dragging.current ? 'grabbing' : 'grab' }}
      onWheel={handleWheel}
      onMouseDown={onDown}
      onMouseMove={onMove}
      onMouseUp={onUp}
      onMouseLeave={onUp}
    >
      {/* Transform layer */}
      <div
        style={{
          transform: `translate(${tf.x}px,${tf.y}px) scale(${tf.scale})`,
          transformOrigin: '0 0',
          width: '100%',
          height: '100%',
          willChange: 'transform',
        }}
      >
        {/* Loading spinner */}
        {!imgLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-slate-700 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}

        {/* Floor image */}
        <img
          key={`img-${floor}`}
          src={FLOOR_IMAGES[floor]}
          alt={`Этаж ${floor}`}
          onLoad={() => setImgLoaded(true)}
          className="absolute inset-0 w-full h-full object-contain pointer-events-none"
          style={{ opacity: imgLoaded ? 1 : 0, transition: 'opacity 0.25s' }}
          draggable={false}
        />

        {/* SVG overlay */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          viewBox={`0 0 ${VW} ${VH}`}
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <filter id={`glow-${floor}`}>
              <feGaussianBlur stdDeviation="5" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <filter id={`sg-${floor}`}>
              <feGaussianBlur stdDeviation="2.5" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {/* Background nodes */}
          {floorAll.map((node) => {
            if (floorPath.some((p) => p.id === node.id)) return null;
            const { cx, cy } = toSvg(node.x, node.y, bounds, VW, VH);
            const stairs = node.type === 'stairs';
            return (
              <g key={`bg-${node.id}`}>
                <circle cx={cx} cy={cy} r={stairs ? 5 : 3.5}
                  fill={stairs ? '#f59e0b' : '#334155'} opacity={stairs ? 0.55 : 0.4} />
                {stairs && (
                  <text x={cx} y={cy - 9} textAnchor="middle" fontSize={9}
                    fill="#f59e0b" opacity={0.5} fontFamily="monospace">↕</text>
                )}
              </g>
            );
          })}

          {/* Path: outer glow */}
          {pts.length > 1 && (
            <polyline key={`glow-${animKey}`} points={poly}
              fill="none" stroke="#3b82f6" strokeWidth={16}
              strokeOpacity={0.1} strokeLinecap="round" strokeLinejoin="round"
              filter={`url(#glow-${floor})`} />
          )}

          {/* Path: animated line */}
          {pts.length > 1 && (
            <polyline key={`line-${animKey}`} points={poly}
              fill="none" stroke="#60a5fa" strokeWidth={3.5}
              strokeLinecap="round" strokeLinejoin="round"
              strokeDasharray={`${totalLen} ${totalLen}`}
              strokeDashoffset={totalLen}
              style={{ animation: 'kumap-draw 1.5s cubic-bezier(.4,0,.2,1) forwards' }} />
          )}

          {/* Directional arrows */}
          {pts.length > 1 && pts.slice(1).map((p, i) => {
            const q = pts[i];
            const mx = (q.cx + p.cx) / 2;
            const my = (q.cy + p.cy) / 2;
            const ang = (Math.atan2(p.cy - q.cy, p.cx - q.cx) * 180) / Math.PI;
            return (
              <g key={`arr-${i}`}
                transform={`translate(${mx},${my}) rotate(${ang})`}
                style={{ animation: `kumap-fade 0.3s ease ${1.3 + i * 0.06}s both`, opacity: 0 }}>
                <polygon points="-6,-3.5 6,0 -6,3.5" fill="#93c5fd" opacity={0.75} />
              </g>
            );
          })}

          {/* Path nodes */}
          {floorPath.map((node, i) => {
            const { cx, cy } = toSvg(node.x, node.y, bounds, VW, VH);
            const isStart = i === 0 && pathNodes[0]?.id === node.id;
            const isEnd   = i === floorPath.length - 1 && pathNodes[pathNodes.length - 1]?.id === node.id;
            const color   = isStart ? '#22c55e' : isEnd ? '#ef4444' : '#3b82f6';
            const r       = isStart || isEnd ? 9 : 5;
            const delay   = 1.0 + i * 0.09;

            return (
              <g key={`pn-${node.id}`}
                style={{ animation: `kumap-pop 0.35s cubic-bezier(.34,1.56,.64,1) ${delay}s both`, opacity: 0 }}>
                {/* Pulse ring for start/end */}
                {(isStart || isEnd) && (
                  <circle cx={cx} cy={cy} r={r + 7} fill={color} opacity={0.12} />
                )}
                <circle cx={cx} cy={cy} r={r + 4} fill={color} opacity={0.15} />
                <circle cx={cx} cy={cy} r={r} fill={color} filter={`url(#sg-${floor})`} />
                <circle cx={cx} cy={cy} r={r * 0.45} fill="white" opacity={0.6} />

                {/* Label chip */}
                {(isStart || isEnd) && (
                  <g>
                    <rect x={cx - 20} y={cy - 26} width={40} height={15} rx={4}
                      fill="#0b1018" opacity={0.9} />
                    <rect x={cx - 20} y={cy - 26} width={40} height={15} rx={4}
                      fill="none" stroke={color} strokeWidth={0.8} opacity={0.6} />
                    <text x={cx} y={cy - 15} textAnchor="middle"
                      fontSize={10} fontWeight="700"
                      fontFamily="IBM Plex Mono, monospace" fill={color}>
                      {node.name}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Floor badge */}
      <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-black/75 border border-white/10 backdrop-blur-sm pointer-events-none">
        <span className="text-xs font-semibold tracking-[0.15em] text-slate-300 uppercase font-mono">
          Этаж {floor}
        </span>
        {floorPath.length > 0 && (
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
        )}
      </div>

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-1.5">
        {([
          { label: '+', fn: () => setTf((t) => ({ ...t, scale: Math.min(6, t.scale * 1.3) })) },
          { label: '−', fn: () => setTf((t) => ({ ...t, scale: Math.max(0.5, t.scale / 1.3) })) },
          { label: '⊙', fn: resetView },
        ] as const).map(({ label, fn }) => (
          <button key={label} onClick={fn}
            className="w-8 h-8 rounded-md bg-black/75 border border-white/10 backdrop-blur-sm text-slate-400 hover:text-white hover:border-white/25 text-sm font-mono transition-all flex items-center justify-center pointer-events-auto">
            {label}
          </button>
        ))}
      </div>

      {/* Zoom level */}
      {tf.scale !== 1 && (
        <div className="absolute bottom-4 left-3 text-[10px] text-slate-600 font-mono pointer-events-none">
          {Math.round(tf.scale * 100)}%
        </div>
      )}

      <style>{`
        @keyframes kumap-draw {
          to { stroke-dashoffset: 0; }
        }
        @keyframes kumap-fade {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes kumap-pop {
          from { opacity: 0; transform: scale(0.3); }
          to   { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
};
