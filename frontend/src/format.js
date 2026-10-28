// Formatting helpers. Market users think in UK local time and in GW/MW.

const ukDateTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/London', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
})
const ukDay = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/London', day: 'numeric', month: 'short' })

export const formatDateTime = (iso) => ukDateTime.format(new Date(iso))
export const formatDay = (ms) => ukDay.format(new Date(ms))
export const formatMW = (mw) => `${Math.round(mw).toLocaleString('en-GB')} MW`
export const formatGW = (mw) => `${(mw / 1000).toFixed(1)} GW`