import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const BIN_MW = 1000

// Groups hourly errors (forecast - actual) into 1 GW buckets.
function buildBins(points) {
  const counts = new Map()
  for (const p of points) {
    if (p.forecast == null || p.actual == null) continue
    const bin = Math.floor((p.forecast - p.actual) / BIN_MW) * BIN_MW
    counts.set(bin, (counts.get(bin) ?? 0) + 1)
  }
  return [...counts.entries()]
    .sort(([a], [b]) => a - b)
    .map(([from, hours]) => ({ from, hours, label: `${from / 1000} to ${(from + BIN_MW) / 1000} GW` }))
}

export default function ErrorHistogram({ points }) {
  if (!points) return <div className="chart-placeholder">Loading chart…</div>
  const bins = buildBins(points)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={bins} margin={{ top: 8, right: 16, bottom: 16, left: 8 }}>
        <CartesianGrid stroke="var(--grid)" vertical={false} />
        <XAxis
          dataKey="from" tickFormatter={(mw) => `${mw / 1000}`} stroke="var(--muted)" fontSize={12}
          label={{ value: 'Forecast − actual (GW)', position: 'insideBottom', offset: -8, fontSize: 12, fill: 'var(--muted)' }}
        />
        <YAxis
          domain={[0, (max) => Math.ceil(max / 50) * 50]} tickCount={6}
          stroke="var(--muted)" fontSize={12} width={40}
        />
        <Tooltip formatter={(hours) => [`${hours} hours`, 'Count']} labelFormatter={(_, p) => p?.[0]?.payload.label} />
        <Bar dataKey="hours" isAnimationActive={false}>
          {bins.map((b) => <Cell key={b.from} fill={b.from >= 0 ? 'var(--short)' : 'var(--actual)'} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}