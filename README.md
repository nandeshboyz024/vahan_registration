
# Vahan Registration Trends – Streamlit Dashboard

An investor-friendly dashboard that tracks vehicle registrations from the public **Vahan** dashboard with **YoY** and **QoQ** growth for:
- Total vehicles by category (2W/3W/4W)
- Each manufacturer

> ⚠️ The public analytics portal uses a CAPTCHA gate. Fully automated scraping is not possible without human-in-the-loop. This project supports Selenium-based scraping where you solve the CAPTCHA once per session, after which the app can read the on-page widgets or hit XHR endpoints that the page calls.

## Features
- Date range selection
- Filters by vehicle category and manufacturer
- Trend charts and % change metrics (YoY & QoQ)
- Streamlit UI with responsive layout

## Quick Start (Demo with Sample Data)
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Choose **"local (demo)"** in the sidebar to use the included `data/sample_registrations.csv`.

## Live Data (Selenium, Human-in-the-loop)
1. Install Google Chrome/Chromium and matching ChromeDriver.
2. `pip install selenium`
3. In the app sidebar, choose **"selenium (live)"**.
4. A browser will open. If a **CAPTCHA** appears, solve it manually. The app will then attempt to scrape the visible charts (e.g., *Top Makers by Registration*, *Vehicle Category Distribution*).

> DOM/XPath selectors may need to be adjusted to the live site's structure. See `vahan/data_ingestion.py` for a starting point.

## Data Model
The dashboard expects the following schema (monthly granularity):
```
date (YYYY-MM-01), category ∈ {2W, 3W, 4W}, manufacturer (str), registrations (int)
```
For manufacturer names, use the official display names (e.g., *Maruti Suzuki*, *Hyundai*, *Tata Motors*).

## SQL (Optional Caching / Warehouse)
A simple SQLite schema is provided in `sql/schema.sql`:
```sql
CREATE TABLE IF NOT EXISTS registrations (
  date TEXT NOT NULL,
  category TEXT NOT NULL,
  manufacturer TEXT NOT NULL,
  registrations INTEGER NOT NULL,
  PRIMARY KEY (date, category, manufacturer)
);

-- Typical queries

-- Monthly total by category
SELECT date, category, SUM(registrations) AS registrations
FROM registrations
WHERE date BETWEEN :start AND :end
GROUP BY date, category;

-- Manufacturer time series
SELECT date, manufacturer, category, SUM(registrations) AS registrations
FROM registrations
WHERE date BETWEEN :start AND :end
  AND (:category IS NULL OR category = :category)
GROUP BY date, manufacturer, category;
```

## Repo Structure
```
app.py                       # Streamlit app
vahan/
  data_ingestion.py          # Live scraping (Selenium) + local CSV loader
  data_processing.py         # Aggregations & growth calculations
sql/
  schema.sql
data/
  sample_registrations.csv   # Demo dataset
requirements.txt
```

## Requirements
- Python 3.9+
- Streamlit
- Pandas / NumPy
- (Optional) Selenium + ChromeDriver (for live data)

## Notes on YoY and QoQ
- **YoY** compares the same month vs the month 12 months earlier.
- **QoQ** compares the sum of the current quarter vs the previous quarter.

## Limitations
- Public site uses CAPTCHA, so unattended scraping is intentionally blocked.
- Manufacturer naming can vary; you may want to build a mapping table for consistency.
- State coverage can vary across RTOs and time; treat numbers as *registrations recorded in Vahan*.

## License
MIT
