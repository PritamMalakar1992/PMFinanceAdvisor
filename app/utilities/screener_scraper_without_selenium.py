import time
import json
import logging
import urllib.parse
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from ..configs_constants.configs import Configs


LOGIN_URL = "https://www.screener.in/login/"
BASE_URL = "https://www.screener.in"
QUERY = """Promoter holding > 51 AND
Debtor days < 90 AND
Sales growth 5Years > 50 AND
Profit growth 5Years > 50"""

WAIT_TIME = 20


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver


def get_cookies(email, password):
    logging.info("Launching browser for login...")

    driver = setup_driver()
    driver.get(LOGIN_URL)

    time.sleep(3)

    driver.find_element(By.NAME, "username").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").submit()

    time.sleep(5)

    cookies = driver.get_cookies()
    driver.quit()

    cookie_dict = {c["name"]: c["value"] for c in cookies}

    logging.info(f"Cookies extracted: {list(cookie_dict.keys())}")

    return cookie_dict


def build_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"{BASE_URL}/screen/raw/?sort=&order=&source_id=&query={encoded_query}"



def fetch_page(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code}")

    return response.text


def parse_table(html):
    dfs = pd.read_html(html)

    if not dfs:
        raise ValueError("No tables found in HTML!")

    df = dfs[0]

    df = df[df.iloc[:, 0] != df.columns[0]]

    df.reset_index(drop=True, inplace=True)

    return df


def scrape_all_pages(session, base_url):
    all_dfs = []
    page = 1

    while True:
        logging.info(f"Fetching page {page}")

        url = base_url + f"&page={page}"
        html = fetch_page(session, url)

        try:
            df = parse_table(html)

            if df.empty:
                break

            all_dfs.append(df)

        except Exception as e:
            logging.warning(f"Stopping pagination: {e}")
            break

        page += 1

    if not all_dfs:
        raise ValueError("No data scraped!")

    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df


def scrape_without_selenium():
    cookies = get_cookies(Configs.SCREENER_USER, Configs.SCREENER_PSWD)

    session = requests.Session()
    session.cookies.update(cookies)

    url = build_url(QUERY)

    df = scrape_all_pages(session, url)

    logging.info(f"Total rows scraped: {len(df)}")

    return df