/**
 * SVG port of CityscapeWidget from src/gui/login_window.py.
 *
 * The original paints onto a 120px-tall widget using fractional coordinates,
 * so the same fractions map cleanly onto an SVG viewBox. Using viewBox units
 * of 1000x120 keeps the window grid spacing (8px / 10px in the original) at
 * the same visual proportion it has in the desktop app.
 */

// (x fraction, width fraction, height fraction) — copied from the Python list.
const BUILDINGS: [number, number, number][] = [
  [0.02, 0.08, 0.7],
  [0.08, 0.06, 0.5],
  [0.13, 0.1, 0.85],
  [0.22, 0.07, 0.55],
  [0.28, 0.09, 0.75],
  [0.36, 0.06, 0.45],
  [0.41, 0.11, 0.9],
  [0.5, 0.07, 0.6],
  [0.56, 0.08, 0.7],
  [0.63, 0.1, 0.8],
  [0.72, 0.06, 0.5],
  [0.77, 0.09, 0.65],
  [0.85, 0.07, 0.75],
  [0.91, 0.08, 0.55],
];

const VW = 1000;
const VH = 120;

const BUILDING_FILL = "rgba(255, 255, 255, 0.07)";
const WINDOW_FILL = "rgba(0, 212, 170, 0.16)";

export function Cityscape() {
  return (
    <svg
      viewBox={`0 0 ${VW} ${VH}`}
      preserveAspectRatio="none"
      className="h-[120px] w-full"
      aria-hidden="true"
      focusable="false"
    >
      {BUILDINGS.map(([xf, wf, hf], i) => {
        const bx = VW * xf;
        const bw = VW * wf;
        const bh = VH * hf;
        const by = VH - bh;

        // Same nested loop as the original paintEvent, just emitting <rect>
        // elements instead of calling drawRect.
        const windows: { x: number; y: number }[] = [];
        const cols = Math.max(1, Math.floor(bw / 22));
        const rows = Math.max(1, Math.floor(bh / 12));
        for (let row = 0; row < rows; row++) {
          for (let col = 0; col < cols; col++) {
            const wx = bx + 8 + col * 22;
            const wy = by + 6 + row * 10;
            if (wx + 6 < bx + bw - 4 && wy + 3 < VH - 4) {
              windows.push({ x: wx, y: wy });
            }
          }
        }

        return (
          <g key={i}>
            <rect x={bx} y={by} width={bw} height={bh} fill={BUILDING_FILL} />
            {windows.map((w, j) => (
              <rect
                key={j}
                x={w.x}
                y={w.y}
                width={6}
                height={3}
                fill={WINDOW_FILL}
              />
            ))}
          </g>
        );
      })}
    </svg>
  );
}
