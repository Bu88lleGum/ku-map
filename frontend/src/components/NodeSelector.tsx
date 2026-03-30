import React, { useState, useRef, useEffect } from 'react';
import { Node } from '../types';

interface NodeSelectorProps {
  nodes: Node[];
  value: number | null;
  onChange: (id: number) => void;
  placeholder: string;
  label: string;
  accentColor: string;
}

export const NodeSelector: React.FC<NodeSelectorProps> = ({
  nodes,
  value,
  onChange,
  placeholder,
  label,
  accentColor,
}) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef<HTMLDivElement>(null);

  const selected = nodes.find((n) => n.id === value);

  const filtered = nodes
    .filter(
      (n) =>
        n.name.toLowerCase().includes(search.toLowerCase()) ||
        String(n.floor).includes(search)
    )
    .sort((a, b) => {
      // Rooms first, then by name
      if (a.type === 'room' && b.type !== 'room') return -1;
      if (a.type !== 'room' && b.type === 'room') return 1;
      return a.name.localeCompare(b.name, undefined, { numeric: true });
    })
    .slice(0, 50);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as EventTarget & HTMLElement)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const typeLabel: Record<string, string> = {
    room: 'Аудитория',
    hallway: 'Коридор',
    stairs: 'Лестница',
  };

  return (
    <div ref={ref} className="relative">
      <label className="block text-xs font-medium tracking-widest uppercase mb-2" style={{ color: accentColor }}>
        {label}
      </label>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-slate-800/80 border border-slate-700/60 text-sm transition-all hover:border-slate-500 focus:outline-none"
        style={{ borderColor: open ? accentColor + '80' : undefined }}
      >
        <span className={selected ? 'text-white' : 'text-slate-500'}>
          {selected ? (
            <span className="flex items-center gap-2">
              <span className="font-semibold">{selected.name}</span>
              <span className="text-xs text-slate-400">Этаж {selected.floor}</span>
            </span>
          ) : placeholder}
        </span>
        <svg className={`w-4 h-4 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-slate-700/60 bg-slate-900/95 backdrop-blur-sm shadow-2xl overflow-hidden">
          <div className="p-2 border-b border-slate-700/40">
            <input
              autoFocus
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Поиск..."
              className="w-full bg-slate-800 text-sm text-white placeholder-slate-500 px-3 py-2 rounded-md outline-none border border-transparent focus:border-slate-600"
            />
          </div>
          <ul className="max-h-56 overflow-y-auto py-1">
            {filtered.map((node) => (
              <li key={node.id}>
                <button
                  onClick={() => { onChange(node.id); setOpen(false); setSearch(''); }}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-sm hover:bg-slate-800/80 transition-colors text-left ${
                    value === node.id ? 'bg-slate-800' : ''
                  }`}
                >
                  <span className="font-medium text-white">{node.name}</span>
                  <span className="flex items-center gap-2 text-xs text-slate-400">
                    <span>{typeLabel[node.type || ''] || node.type}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">Эт. {node.floor}</span>
                  </span>
                </button>
              </li>
            ))}
            {filtered.length === 0 && (
              <li className="px-4 py-3 text-sm text-slate-500 text-center">Ничего не найдено</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};
