"""
automation.py
Optional Selenium-based automation to pull a job description's text
directly from a job-posting URL, so the user doesn't have to copy/paste.

Note: selectors here are generic fallbacks (page <body> text). Real-world
job boards vary widely and many disallow scraping in their ToS — always
check a site's terms before pointing this at it, and prefer official APIs
where available.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1024")
    return webdriver.Chrome(options=options)


def fetch_job_description_from_url(url: str, timeout: int = 15) -> str:
    """
    Loads a job posting URL in a headless Chrome instance and returns
    the visible text content of the page body. Intended as a convenience
    starting point — the user should still review/clean the extracted text.
    """
    driver = _build_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text.strip()
        return text
    finally:
        driver.quit()
