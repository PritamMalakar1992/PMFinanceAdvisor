import time
import logging
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from ..configs_constants.configs import Configs
from ..configs_constants import constants as C


LOGIN_URL = "https://www.screener.in/login/"
RAW_URL = "https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Promoter+holding++%3E+51+AND%0D%0ADebtor+days++%3C+90+AND%0D%0ASales+growth+5Years+%3E+50+AND%0D%0AProfit+growth+5Years+%3E+50"

WAIT_TIME = 20
MAX_RETRIES = 3


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def setup_driver(headless=False):
    
    options = Options()
    options.add_argument("--start-maximized")
    
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")\

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def login(driver, email, password):
    logging.info("Logging in...")
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").submit()

    time.sleep(5)


def open_raw(driver):
    logging.info("Opening RAW page...")
    driver.get(RAW_URL)

    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table"))
    )


def extract_table(driver):
    table = driver.find_element(By.CSS_SELECTOR, "table.data-table")

    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

    headers = None
    data = []

    for tr in rows:

        ths = tr.find_elements(By.TAG_NAME, "th")
        if ths and headers is None:
            headers = [th.text.strip() for th in ths]
            continue

        if tr.get_attribute("data-row-company-id"):
            tds = tr.find_elements(By.TAG_NAME, "td")
            row = [td.text.strip() for td in tds]

            if headers and len(row) == len(headers):
                data.append(row)

    if not headers:
        raise ValueError("Headers not found!")

    if not data:
        raise ValueError("No data rows found!")

    return headers, data


def extract_all_pages(driver):
    all_data = []
    headers = None
    page = 1

    while True:
        logging.info(f"Scraping page {page}")

        h, rows = extract_table(driver)

        if headers is None:
            headers = h

        all_data.extend(rows)

        try:
            next_btn = driver.find_element(By.LINK_TEXT, "Next")

            if "disabled" in next_btn.get_attribute("class").lower():
                break

            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            page += 1

        except:
            break

    return pd.DataFrame(all_data, columns=headers)


def scrape():
    for attempt in range(1, MAX_RETRIES + 1):
        logging.info(f"Attempt {attempt}")

        driver = setup_driver(C.RUN_HEADLESS)

        try:
            login(driver, Configs.SCREENER_USER, Configs.SCREENER_PSWD)
            open_raw(driver)

            df = extract_all_pages(driver)

            logging.info(f"Total rows: {len(df)}")
            return df

        except Exception as e:
            logging.error(f"Failed attempt {attempt}: {e}")

            if attempt == MAX_RETRIES:
                raise

            time.sleep(3)

        finally:
            driver.quit()