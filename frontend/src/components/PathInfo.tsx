import React from 'react';
import { PathResult } from '../types';
import { formatTime } from '../utils/coords';

interface PathInfoProps {
  result: PathResult;
}

export const PathInfo: React.FC<PathInfoProps> = ({ result }) => {
  const floorsUsed = [...new Set(result.path_nodes.map((n) => n.floor))].sort();
  const hasStairs = floorsUsed.length > 1;

  return (
    <div className="space-y-4">
      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Расстояние', value: `${result.length_meters.toFixed(0)} м` },
          { label: 'Время', value: formatTime(result.time_seconds) },
          { label: 'Этажей', value: hasStairs ? floorsUsed.join('→') : String(floorsUsed[0]) },
        ].map(({ label, value }) => (
          <div key={label} className="bg-slate-800/60 rounded-lg px-3 py-2.5 border border-slate-700/40">
            <div className="text-xs text-slate-500 mb-1 tracking-wider uppercase">{label}</div>
            <div className="text-sm font-semibold text-white">{value}</div>
          </div>
        ))}
      </div>

      {/* Instructions */}
      <div>
        <div className="text-xs font-medium text-slate-500 tracking-widest uppercase mb-2">
          Маршрут
        </div>
        <ol className="space-y-1">
          {result.instructions.map((step, i) => {
            const isFirst = i === 0;
            const isLast = i === result.instructions.length - 1;
            const isStairs = step.includes('этаж') || step.includes('Под');

            return (
              <li key={i} className="flex items-start gap-3 py-1.5">
                <div
                  className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                    isFirst
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : isLast
                      ? 'bg-red-500/20 text-red-400'
                      : isStairs
                      ? 'bg-amber-500/20 text-amber-400'
                      : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  {isFirst ? '▶' : isLast ? '◉' : isStairs ? '⬆' : i}
                </div>
                <span className={`text-sm leading-tight ${isFirst || isLast ? 'text-white font-medium' : 'text-slate-300'}`}>
                  {step}
                </span>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
};
