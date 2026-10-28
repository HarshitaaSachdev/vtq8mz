import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatDateTime, formatDay, formatMW } from '../format.js'

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div className="tooltip">
      <strong>{formatDateTime(point.time)}</strong>
      <div className="row actual">Actual: {point.actual != null ? formatMW(point.actual) : '–'}</div>
      {point.forecast != null && (
        <>
          <div className="row forecast">Forecast: {formatMW(point.forecast)}</div>
          <div className="muted">
            Published {formatDateTime(point.publish_time)} ({point.horizon_hours}h ahead)
          </div>
        </>
      )}
    </div>
  )
}

export default function ForecastChart({ points }) {
  if (!points) return <div className="chart-placeholder">Loading chart…</div>
  const data = points.map((p) => ({ ...p, ms: new Date(p.time).getTime() }))

  return (
    <ResponsiveContainer width="100%" height={360}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 8 }}>
        <CartesianGrid stroke="var(--grid)" vertical={false} />
        <XAxis
          dataKey="ms" type="number" scale="time" domain={['dataMin', 'dataMax']}
          tickFormatter={formatDay} stroke="var(--muted)" fontSize={12}
        />
        <YAxis
          domain={[0, (max) => Math.ceil(max / 5000) * 5000]} tickCount={6}
          tickFormatter={(mw) => `${mw / 1000} GW`} stroke="var(--muted)" fontSize={12} width={56}
        />
        <Tooltip content={<ChartTooltip />} />
        <Legend />
        <Line
          name="Actual" dataKey="actual" stroke="var(--actual)" strokeWidth={1.6}
          dot={false} isAnimationActive={false}
        />
        <Line
          name="Forecast" dataKey="forecast" stroke="var(--forecast)" strokeWidth={1.6}
          dot={false} connectNulls isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}