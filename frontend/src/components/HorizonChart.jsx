import {
  CartesianGrid, Legend, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { formatMW } from '../format.js'

export default function HorizonChart({ rows }) {
  if (!rows) return <div className="chart-placeholder">Loading chart…</div>
  const data = rows
    .filter((r) => r.metrics)
    .map((r) => ({ horizon: r.horizon_hours, mae: r.metrics.mae, p90: r.metrics.p90_shortfall }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 16, left: 8 }}>
        <CartesianGrid stroke="var(--grid)" vertical={false} />
        <ReferenceArea x1={16} x2={40} fill="var(--band)" />
        <XAxis
          dataKey="horizon" type="number" domain={[0, 48]} ticks={[0, 6, 12, 18, 24, 30, 36, 42, 48]}
          stroke="var(--muted)" fontSize={12}
          label={{ value: 'Hours ahead', position: 'insideBottom', offset: -8, fontSize: 12, fill: 'var(--muted)' }}
        />
        <YAxis tickFormatter={(mw) => `${(mw / 1000).toFixed(1)} GW`} stroke="var(--muted)" fontSize={12} width={60} />
        <Tooltip formatter={(value) => formatMW(value)} labelFormatter={(h) => `${h}h ahead`} />
        <Legend verticalAlign="top" height={28} />
        <Line name="Average error (MAE)" dataKey="mae" stroke="var(--actual)" strokeWidth={2} isAnimationActive={false} />
        <Line name="P90 shortfall" dataKey="p90" stroke="var(--short)" strokeWidth={2} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}