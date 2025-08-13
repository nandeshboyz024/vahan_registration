# Vahan Registration Trends – Streamlit Dashboard
[Live Demo](https://nandeshboyz024-vahan-registration-app-zy87ds.streamlit.app/)


An investor-friendly dashboard that tracks vehicle registrations from the public **Vahan** dashboard with **YoY** and **QoQ** growth for:
- Total vehicles by category (2W/3W/4W)
- Each manufacturer

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

## Live Data (Selenium, Human-in-the-loop)
1. Install Google Chrome/Chromium and matching ChromeDriver.
2. `pip install selenium`
3. In the app sidebar, choose **"selenium (live)"**.
4. A browser will open. If a **CAPTCHA** appears, solve it manually. The app will then attempt to scrape the visible charts (e.g., *Top Makers by Registration*, *Vehicle Category Distribution*).

## Notes on YoY and QoQ
- **YoY** compares the same month vs the month 12 months earlier.
- **QoQ** compares the sum of the current quarter vs the previous quarter.
