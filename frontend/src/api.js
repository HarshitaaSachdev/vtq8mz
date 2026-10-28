// All calls to the Python backend live here, so components never build URLs themselves.

async function getJson(path, params, signal) {
  const query = new URLSearchParams(params).toString()
  const response = await fetch(`/api/${path}${query ? `?${query}` : ''}`, { signal })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ? JSON.stringify(body.detail) : `Request failed (${response.status})`)
  }
  return response.json()
}

export const fetchMeta = (signal) => getJson('meta', {}, signal)

export function fetchSeries({ mode, decisionTime, horizonHours, start, end }, signal) {
  const params = { mode, start, end }
  if (mode === 'decision') params.decision_time = decisionTime
  else params.horizon_hours = horizonHours
  return getJson('series', params, signal)
}

export const fetchAccuracyByHorizon = ({ start, end }, signal) =>
  getJson('accuracy/by-horizon', { start, end }, signal)