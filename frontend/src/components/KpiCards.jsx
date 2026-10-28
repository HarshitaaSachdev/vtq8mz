import { formatGW } from '../format.js'

export default function KpiCards({ metrics }) {
  if (!metrics) return <div className="kpis loading">Loading metrics…</div>

  const cards = [
    {
      label: 'Average error (MAE)',
      value: formatGW(metrics.mae),
      note: `${metrics.nmae_pct}% of average wind output (${formatGW(metrics.mean_actual)})`,
    },
    {
      label: 'P90 shortfall buffer',
      value: formatGW(metrics.p90_shortfall),
      note: 'In 90% of hours, wind was at most this far below forecast',
      highlight: true,
    },
    {
      label: 'Bias',
      value: `${metrics.bias > 0 ? '+' : ''}${formatGW(metrics.bias)}`,
      note: metrics.bias > 0 ? 'Forecasts were too optimistic on average' : 'Forecasts were too pessimistic on average',
    },
    {
      label: 'Worst hour shortfall',
      value: formatGW(metrics.max_shortfall),
      note: `RMSE ${formatGW(metrics.rmse)} across ${metrics.count} hours`,
    },
  ]

  return (
    <div className="kpis">
      {cards.map((card) => (
        <div key={card.label} className={`kpi ${card.highlight ? 'highlight' : ''}`}>
          <span className="kpi-label">{card.label}</span>
          <span className="kpi-value">{card.value}</span>
          <span className="kpi-note">{card.note}</span>
        </div>
      ))}
    </div>
  )
}