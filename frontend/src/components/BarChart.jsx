/**
 * BarChart
 *
 * SVG bar chart with a fixed coordinate system so labels are never
 * distorted. Uses a viewBox with a real pixel width so text sizes
 * are predictable regardless of the container width.
 *
 * Props
 * -----
 *   data:     [{ label, value, accent? }]
 *   height:   chart drawing area height in px (default 220)
 *   maxValue: optional override; defaults to max(value)
 */
export default function BarChart({ data = [], height = 220, maxValue }) {
  if (!data.length) return <p className="muted">No data to display.</p>;

  const SVG_W = 400;
  const SVG_H = height;
  const PADDING_TOP = 28;
  const PADDING_BOTTOM = 36;
  const PADDING_X = 12;
  const chartH = SVG_H - PADDING_TOP - PADDING_BOTTOM;

  const max = maxValue ?? Math.max(...data.map((d) => Number(d.value) || 0), 1);
  const n = data.length;
  const totalW = SVG_W - PADDING_X * 2;
  const barW = (totalW / n) * 0.55;
  const gap = totalW / n;

  return (
    <div style={{ width: "100%" }}>
      <svg
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ width: "100%", height: "auto", display: "block" }}
        role="img"
        aria-label="bar chart"
      >
        {/* Horizontal grid lines */}
        {[0.25, 0.5, 0.75, 1].map((frac) => {
          const y = PADDING_TOP + chartH * (1 - frac);
          return (
            <line
              key={frac}
              x1={PADDING_X}
              y1={y}
              x2={SVG_W - PADDING_X}
              y2={y}
              stroke="#e5e7eb"
              strokeWidth="0.8"
              strokeDasharray="4 3"
            />
          );
        })}

        {data.map((d, i) => {
          const v = Number(d.value) || 0;
          const barH = (v / max) * chartH;
          const cx = PADDING_X + gap * i + gap / 2;
          const x = cx - barW / 2;
          const y = PADDING_TOP + chartH - barH;

          return (
            <g key={i}>
              {/* Bar */}
              <rect
                x={x}
                y={y}
                width={barW}
                height={barH}
                rx="4"
                fill={d.accent || "var(--color-primary)"}
                opacity="0.9"
              />
              {/* Value label above bar */}
              <text
                x={cx}
                y={y - 6}
                fontSize="11"
                textAnchor="middle"
                fontWeight="600"
                fill="var(--color-text)"
              >
                {v}
              </text>
              {/* X-axis label */}
              <text
                x={cx}
                y={SVG_H - 10}
                fontSize="11"
                textAnchor="middle"
                fill="var(--color-text-muted)"
              >
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
