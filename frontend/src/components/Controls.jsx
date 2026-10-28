const DECISION_TIMES = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00']

export default function Controls({ settings, meta, onChange }) {
  const update = (changes) => onChange({ ...settings, ...changes })
  const minDay = meta?.first_delivery_day
  const maxDay = meta?.last_delivery_day

  return (
    <div className="controls">
      <div className="control">
        <label>View</label>
        <div className="segmented">
          <button
            className={settings.mode === 'decision' ? 'active' : ''}
            onClick={() => update({ mode: 'decision' })}
          >
            Day-ahead decision
          </button>
          <button
            className={settings.mode === 'horizon' ? 'active' : ''}
            onClick={() => update({ mode: 'horizon' })}
          >
            Fixed horizon
          </button>
        </div>
      </div>

      {settings.mode === 'decision' ? (
        <div className="control">
          <label htmlFor="decision-time">Decision time (day before)</label>
          <select
            id="decision-time"
            value={settings.decisionTime}
            onChange={(e) => update({ decisionTime: e.target.value })}
          >
            {DECISION_TIMES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      ) : (
        <div className="control slider">
          <label htmlFor="horizon">Forecast horizon: <strong>{settings.horizonHours}h</strong></label>
          <input
            id="horizon"
            type="range"
            min="0"
            max={meta?.max_horizon_hours ?? 48}
            value={settings.horizonHours}
            onChange={(e) => update({ horizonHours: Number(e.target.value) })}
          />
        </div>
      )}

      <div className="control">
        <label htmlFor="start">Delivery from</label>
        <input
          id="start" type="date" min={minDay} max={settings.end} value={settings.start}
          onChange={(e) => e.target.value && update({ start: e.target.value })}
        />
      </div>
      <div className="control">
        <label htmlFor="end">Delivery to</label>
        <input
          id="end" type="date" min={settings.start} max={maxDay} value={settings.end}
          onChange={(e) => e.target.value && update({ end: e.target.value })}
        />
      </div>
    </div>
  )
}