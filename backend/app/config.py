"""Central settings for the app. Change dates or defaults here, nowhere else."""
from datetime import date, time
from zoneinfo import ZoneInfo

ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

# All market times are UK local time (GMT in winter, BST in summer).
UK_TZ = ZoneInfo("Europe/London")

# Purchase decisions made in January 2026 are for delivery on the following day,
# so the delivery days we analyse are 2 Jan 2026 .. 1 Feb 2026 (inclusive).
FIRST_DELIVERY_DAY = date(2026, 1, 2)
LAST_DELIVERY_DAY = date(2026, 2, 1)

# Default time on the day before delivery at which the buying decision is made.
# The GB day-ahead auctions close mid-morning, so 09:00 leaves a safety buffer.
DEFAULT_DECISION_TIME = time(9, 0)

# The longest forecast horizon we analyse (Elexon publishes ~2 days ahead).
MAX_HORIZON_HOURS = 48