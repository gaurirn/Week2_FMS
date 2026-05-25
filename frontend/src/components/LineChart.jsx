/**
 * LineChart
 *
 * SVG line chart for the monthly timeline. Uses a fixed viewBox so
 * text is never distorted. Long period labels are rotated to avoid
 * overlap.
 *
 * Props
 * -----
 *   data:   [{ period, value }]
 *   height: chart drawing area height in px (default 260)
 */
export default function LineChart({ data = [], height = 260 }) {
  if (!data.length) return <p className="muted">No data to display.</p>;
  if (data.length === 1) {
    return (
      <p className="muted">
        Only one data point ({data[0].period}: {data[0].value}). Add more data
        to see a trend.
      </p>
    );
  }

  const SVG_W = 600;
  const SVG_H = height;
  const PAD_TOP = 28;
  const PAD_BOTTOM = 52; // extra room for rotated labels
  const PAD_LEFT = 36;
  const PAD_RIGHT = 16;

  const chartW = SVG_W - PAD_LEFT - PAD_RIGHT;
  const chartH = SVG_H - PAD_TOP - PAD_BOTTOM;

  const maxVal = Math.max(...data.map((d) => Number(d.value) || 0), 1);
  const stepX = chartW / (data.length - 1);

  const points = data.map((d, i) => {
    const v = Number(d.value) || 0;
    const x = PAD_LEFT + i * stepX;
    const y = PAD_TOP + chartH - (v / maxVal) * chartH;
    return { x, y, ...d, v };
  });

  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`)
    .join(" ");

  const areaPath = `${linePath} L${points[points.length - 1].x},${PAD_TOP + chartH} L${PAD_LEFT},${PAD_TOP + chartH} Z`;

  // Y-axis tick values
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((f) => ({
    frac: f,
    val: Math.round(maxVal * f),
    y: PAD_TOP + chartH - f * chartH,
  }));

  return (
    <div style={{ width: "100%" }}>
      <svg
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ width: "100%", height: "auto", display: "block" }}
        role="img"
        aria-label="monthly trend line chart"
      >
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.18" />
            <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {/* Grid lines + Y-axis labels */}
        {yTicks.map((t) => (
          <g key={t.frac}>
            <line
              x1={PAD_LEFT}
              y1={t.y}
              x2={SVG_W - PAD_RIGHT}
              y2={t.y}
              stroke="#e5e7eb"
              strokeWidth="0.8"
              strokeDasharray={t.frac === 0 ? "none" : "4 3"}
            />
            <text
              x={PAD_LEFT - 6}
              y={t.y + 4}
              fontSize="10"
              textAnchor="end"
              fill="var(--color-text-muted)"
            >
              {t.val}
            </text>
          </g>
        ))}

        {/* Area fill */}
        <path d={areaPath} fill="url(#areaGrad)" />

        {/* Line */}
        <path
          d={linePath}
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Data points + labels */}
        {points.map((p, i) => (
          <g key={i}>
            {/* Dot */}
            <circle
              cx={p.x}
              cy={p.y}
              r="3.5"
              fill="var(--color-surface, #fff)"
              stroke="var(--color-primary)"
              strokeWidth="2"
            />
            {/* Value above dot */}
            <text
              x={p.x}
              y={p.y - 9}
              fontSize="10"
              textAnchor="middle"
              fontWeight="600"
              fill="var(--color-text)"
            >
              {p.v}
            </text>
            {/* X-axis period label — rotated so they don't overlap */}
            <text
              x={p.x}
              y={PAD_TOP + chartH + 14}
              fontSize="10"
              textAnchor="end"
              fill="var(--color-text-muted)"
              transform={`rotate(-40, ${p.x}, ${PAD_TOP + chartH + 14})`}
            >
              {p.period}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
