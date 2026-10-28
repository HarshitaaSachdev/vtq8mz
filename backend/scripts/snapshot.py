"""Downloads the January 2026 data from Elexon into data/*.json.

Run from the backend folder:  python -m scripts.snapshot
"""
import json

from app.data import ACTUALS_FILE, DATA_DIR, FORECASTS_FILE, fetch_raw_rows


def main() -> None:
    actual_rows, forecast_rows = fetch_raw_rows()
    DATA_DIR.mkdir(exist_ok=True)
    ACTUALS_FILE.write_text(json.dumps(actual_rows))
    FORECASTS_FILE.write_text(json.dumps(forecast_rows))
    print(f"Saved {len(actual_rows)} actual rows and {len(forecast_rows)} forecast rows to {DATA_DIR}")


if __name__ == "__main__":
    main()