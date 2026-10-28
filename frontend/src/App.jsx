import { useEffect, useState } from 'react'
import { fetchAccuracyByHorizon, fetchMeta, fetchSeries } from './api.js'
import Controls from './components/Controls.jsx'
import KpiCards from './components/KpiCards.jsx'
import ForecastChart from './components/ForecastChart.jsx'
import HorizonChart from './components/HorizonChart.jsx'
import ErrorHistogram from './components/ErrorHistogram.jsx'

const DEFAULT_SETTINGS = {
  mode: 'decision',
  decisionTime: '09:00',
  horizonHours: 24,
  start: '2026-01-02',
  end: '2026-02-01',
}

export default function App() {
  const [meta, setMeta] = useState(null)
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [series, setSeries] = useState(null)
  const [byHorizon, setByHorizon] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    fetchMeta(controller.signal).then(setMeta).catch(handleError)
    return () => controller.abort()
  }, [])

  // Re-fetch whenever a setting changes. Aborting the previous request means a
  // slow, outdated response can never overwrite a newer one.
  useEffect(() => {
    const controller = new AbortController()
    setError(null)
    fetchSeries(settings, controller.signal).then(setSeries).catch(handleError)
    return () => controller.abort()
  }, [settings])

  useEffect(() => {
    const controller = new AbortController()
    fetchAccuracyByHorizon(settings, controller.signal).then(setByHorizon).catch(handleError)
    return () => controller.abort()
  }, [settings.start, settings.end])

  function handleError(err) {
    if (err.name !== 'AbortError') setError(err.message)
  }

  const viewLabel = settings.mode === 'decision'
    ? `Latest forecast published by ${settings.decisionTime} UK time on the day before delivery`
    : `Latest forecast published at least ${settings.horizonHours}h before each period`

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Wind Forecast Monitor</h1>
          <p className="subtitle">
            GB national wind generation: forecast vs actual, for day-ahead purchases made in January 2026
          </p>
        </div>
        <span className="source">Data: Elexon BMRS (FUELHH, WINDFOR)</span>
      </header>

      <Controls settings={settings} meta={meta} onChange={setSettings} />

      {error && <div className="error">Could not load data: {error}</div>}

      <KpiCards metrics={series?.metrics} />

      <section className="card">
        <div className="card-head">
          <h2>Actual vs forecast wind generation</h2>
          <p>{viewLabel}</p>
        </div>
        <ForecastChart points={series?.points} />
      </section>

      <div className="grid-2">
        <section className="card">
          <div className="card-head">
            <h2>How error grows with forecast horizon</h2>
            <p>Shaded band: horizons a day-ahead buyer actually works with (about 16–40h)</p>
          </div>
          <HorizonChart rows={byHorizon} />
        </section>
        <section className="card">
          <div className="card-head">
            <h2>Distribution of forecast error</h2>
            <p>Forecast minus actual, per hour. Right of zero = less wind than forecast (buyer is short)</p>
          </div>
          <ErrorHistogram points={series?.points} />
        </section>
      </div>

      <footer className="footer">
        Forecasts are hourly and actuals half-hourly, so errors are measured on the hour only.
        Forecasts published after their target time are excluded. All times shown in UK local time.
      </footer>
    </div>
  )
}