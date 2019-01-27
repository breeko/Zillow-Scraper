from imp import reload

from utils.browser import setup_browser
from time import sleep
from attributes_from_elements import get_attrs_from_elements
from attributes_from_html import get_attrs_from_html
import get_history; reload(get_history)
from get_history import get_price_history, get_tax_history
import utils.csv_utils; reload(utils.csv_utils)
from utils.csv_utils import update_attrs_file, update_price_file, update_tax_file, get_csv_col, delete_dups
import utils; reload(utils)
from utils.utils import get_zpid_from_zillow_url
from selenium.common.exceptions import TimeoutException

import configs

import argparse
import logging

logging.basicConfig(filename='scrape.log',level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("urls", help="file containing zillow sites to scrape")
parser.add_argument("-o", "--out", default='data/db/out.csv',
                     help="destination of home attributes output file")
parser.add_argument("-p", "--prices", default='data/db/prices.csv',
                     help="destination of price history output file")
parser.add_argument("-t", "--taxes", default='data/db/taxes.csv',
                     help="destination of tax history output file")
parser.add_argument("-l", "--headless", dest='headless', action='store_true',
                     help="boolen to indicate whether to run as headless")

args = parser.parse_args()

def scrape_urls(browser, urls_path, out_path, price_history_path, tax_history_path):
    with open(urls_path, "r") as f:
        urls = f.readlines()

    attrs_reviewed = get_csv_col(out_path, "zpid")
    price_reviewed = get_csv_col(price_history_path, "zpid")
    tax_reviewed = get_csv_col(tax_history_path, "zpid")
    
    num_failures = 0
    num_consecutive_failures = 0

    num_urls = len(urls)
    for idx, url in enumerate(urls):
        print("\r{} / {} failures: {} consecutive failures: {}".format(
            idx + 1, num_urls, num_failures, num_consecutive_failures).ljust(100), end="")
        zpid = get_zpid_from_zillow_url(url)

        in_attrs = zpid in attrs_reviewed
        in_price = zpid in price_reviewed
        in_tax = zpid in tax_reviewed

        if in_attrs:
            # NOTE: ignore if review in attributes although may be missing price and tax history
            continue
        
        try:
            browser.get(url)
        except TimeoutException:
            logging.INFO("TIMEOUT {}".format(url))
            sleep(configs.SLEEP_AFTER_TIMEOUT)
            continue

        attrs = price_history = tax_history = None
        
        # attributes
        if not in_attrs:
            attrs = get_attrs_from_html(browser) or get_attrs_from_elements(browser)
            if attrs is not None:
                attrs["zpid"] = zpid
                attrs["url"] = browser.current_url
                update_attrs_file(out_path, attrs)
            else:
                logging.error("ATTRIBUTES {}".format(url))

        # price history
        if not in_price:
            price_history = get_price_history(browser)
            if price_history:
                update_price_file(price_history_path, price_history)
            else:
                logging.error("PRICE_HISTORY {}".format(url))

        # tax history
        if not in_tax:
            tax_history = get_tax_history(browser)
            if tax_history:
                update_tax_file(tax_history_path, tax_history)
            else:
                logging.error("TAX_HISTORY {}".format(url))
        
        if not attrs and not price_history and not tax_history:
            num_failures += 1
            num_consecutive_failures += 1
        else:
            num_consecutive_failures = 0
        
        if num_failures > configs.MAX_FAILURES or num_consecutive_failures > configs.MAX_CONSECUTIVE_FAILURES:
            break

        sleep_time = int(configs.SLEEP_BETWEEN_SCRAPE())
        for sleep_time_remaining in range(sleep_time, 0, -1):
            print("\r{} / {} failures: {} consecutive failures: {} sleep: {:.0f}".format(
                idx + 1, num_urls, num_failures, num_consecutive_failures, sleep_time_remaining)
                .ljust(100), end="")
            sleep(1)
    return True

if __name__ == "__main__":
    print("Setting up browser")
    browser = setup_browser(sign_in=False, headless=args.headless)
    print("Scraping {}".format(args.urls))
    try:
        scrape_urls(
            browser=browser,
            urls_path=args.urls,
            out_path=args.out,
            tax_history_path=args.taxes,
            price_history_path=args.prices)
    except Exception as e:
        print(e)
    browser.close()
