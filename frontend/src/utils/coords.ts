// Backend coords are in percentage-like units (0-70 range approx)
// Map image is displayed at a given width/height
// We need to convert node x,y to pixel positions on the image

export function toCanvasCoords(
  x: number,
  y: number,
  mapWidth: number,
  mapHeight: number,
  coordBounds = { minX: -5, maxX: 70, minY: 5, maxY: 50 }
): { cx: number; cy: number } {
  const { minX, maxX, minY, maxY } = coordBounds;
  const cx = ((x - minX) / (maxX - minX)) * mapWidth;
  const cy = ((y - minY) / (maxY - minY)) * mapHeight;
  return { cx, cy };
}

export function formatTime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} сек`;
  return `${Math.round(seconds / 60)} мин`;
}
