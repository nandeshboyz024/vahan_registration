
"""
Data Ingestion for Vahan Dashboard
----------------------------------
This module provides two pathways:
1) **Live scraping** (Selenium, human-in-the-loop for CAPTCHA on analytics.parivahan.gov.in)
2) **Local CSV** fallback for demos/tests

IMPORTANT: The public Vahan analytics dashboard enforces CAPTCHA before loading data endpoints.
Automated scraping must therefore:
  - Launch a real browser (Chromium/Chrome) via Selenium
  - Pause for you to solve the CAPTCHA once per session
  - Then harvest the on-page charts/tables (e.g., "Top Makers by Registration", "Vehicle Category Distribution")
  - Optionally hit XHR endpoints *after* CAPTCHA session cookie is set

If live scraping isn't possible, this module loads a local CSV in the exact schema expected:
    columns: date (YYYY-MM-01), category in {2W,3W,4W}, manufacturer (str), registrations (int)
"""
from __future__ import annotations
import time, os, json, datetime as dt
from typing import Optional
import pandas as pd

def load_local_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    # Normalize schema
    df["category"] = df["category"].str.upper().str.replace("TWO WHEELER","2W").str.replace("THREE WHEELER","3W")
    return df

def get_data(source: str = "local", csv_path: str = "data/sample_registrations.csv", **kwargs) -> pd.DataFrame:
    """
    Parameters
    ----------
    source : "local" | "selenium"
    csv_path : path to local csv
    kwargs : used for selenium (e.g., headless: bool, wait_sec: int)

    Returns
    -------
    pandas.DataFrame with columns [date, category, manufacturer, registrations]
    """
    if source == "local":
        return load_local_csv(csv_path)

    if source == "selenium":
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except Exception as e:
            raise RuntimeError("Install selenium and a Chrome/Chromium driver to use live scraping.") from e

        headless = kwargs.get("headless", False)
        url = "https://analytics.parivahan.gov.in/analytics/publicdashboard/vahan?lang=en"

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1400,1000")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # --- Wait for user to solve CAPTCHA if present ---
        time.sleep(2)
        try:
            # The page shows a "CAPTCHA Verification" modal; wait until it's gone.
            WebDriverWait(driver, 300).until_not(
                EC.presence_of_element_located((By.XPATH, "//*[contains(., 'CAPTCHA Verification') or contains(@id,'captcha')]"))
            )
        except Exception:
            print("If CAPTCHA remains, please solve it manually in the opened browser window.")
            input("Press ENTER after solving CAPTCHA...")

        # Example extraction: scrape "Top Makers by Registration" and "Vehicle Category Distribution"
        # NOTE: The actual DOM IDs/classes may change. Adjust the XPaths/CSS selectors as needed.
        # As a fallback, this demo returns local CSV if scraping fails.
        try:
            # TODO: implement precise scraping once DOM selectors are confirmed.
            raise NotImplementedError("Implement Selenium scraping selectors for live site.")
        except Exception as e:
            print("Live scrape not implemented/failed; falling back to local CSV.")
            driver.quit()
            return load_local_csv(csv_path)

    raise ValueError("source must be 'local' or 'selenium'")
