from imp import reload

from utils.browser import setup_browser
from attributes_from_elements import get_attrs_from_elements
from attributes_from_html import get_attrs_from_html
import get_history; reload(get_history)
from get_history import get_price_history, get_tax_history
import utils.csv_utils; reload(utils.csv_utils)
from utils.csv_utils import update_attrs_file, update_price_file, update_tax_file, get_csv_col, delete_dups
import utils; reload(utils)
from utils.utils import get_zpid_from_zillow_url, sleep_verbose
from selenium.common.exceptions import TimeoutException

import configs

import argparse
import logging

logging.basicConfig(filename='scrape.log', format='%(asctime)s -  %(levelname)s - %(message)s', level=logging.INFO)

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

def scrape_urls(urls_path, out_path, price_history_path, tax_history_path, headless):
    with open(urls_path, "r") as f:
        urls = f.readlines()

    attrs_reviewed = get_csv_col(out_path, "zpid")
    price_reviewed = get_csv_col(price_history_path, "zpid")
    tax_reviewed = get_csv_col(tax_history_path, "zpid")
    
    num_failures = 0
    num_consecutive_failures = 0
    num_timeouts = 0
    num_captcha = 0

    browser = setup_browser(sign_in=False, headless=headless)

    num_urls = len(urls)
    try:
        for idx, url in enumerate(urls):

            if num_failures > configs.MAX_FAILURES or \
                num_consecutive_failures > configs.MAX_CONSECUTIVE_FAILURES or \
                num_timeouts > configs.MAX_TIMEOUTS or \
                num_captcha > configs.MAX_CAPTCHA:
                break
            
            sleep_verbose("{} / {} failures: {} consecutive failures: {} timeouts: {} captchas: {}".format(
                idx + 1, num_urls, num_failures, num_consecutive_failures, num_timeouts, num_captcha), 0)
            zpid = get_zpid_from_zillow_url(url)

            in_attrs = zpid in attrs_reviewed
            in_price = zpid in price_reviewed
            in_tax = zpid in tax_reviewed

            if in_attrs:
                # NOTE: ignore if review in attributes although may be missing price and tax history
                continue
            
            if (idx + 1) % configs.RESET_BROWSER == 0:
                browser.close()
                browser = setup_browser(sign_in=False, headless=headless)
            
            if "captcha" in browser.current_url.lower():
                num_captcha += 1
                browser.close()
                browser = setup_browser(sign_in=False, headless=headless)

            try:
                browser.get(url)
            except TimeoutException:
                browser.close()
                browser = setup_browser(sign_in=False, headless=headless)
                logging.info("TIMEOUT {}".format(url))
                num_timeouts += 1
                sleep_time = configs.SLEEP_AFTER_TIMEOUT()
                sleep_verbose("Timeout.", sleep_time)
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
            
            sleep_time = int(configs.SLEEP_BETWEEN_SCRAPE())
            sleep_verbose("{} / {} failures: {} consecutive failures: {} timeouts: {} captchas: {}".format(
                idx + 1, num_urls, num_failures, num_consecutive_failures, num_timeouts, num_captcha), sleep_time)
    except KeyboardInterrupt:
        browser.close()

    return True

if __name__ == "__main__":
    print("Scraping {}".format(args.urls))
    scrape_urls(
        urls_path=args.urls,
        out_path=args.out,
        tax_history_path=args.taxes,
        price_history_path=args.prices,
        headless=args.headless)
    