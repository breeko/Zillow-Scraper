from imp import reload

import numpy as np
from browser import setup_browser
from time import sleep
from attributes_from_elements import get_attrs_from_elements
from attributes_from_html import get_attrs_from_html
import history; reload(history)
from history import get_price_history, get_tax_history
import csv_utils; reload(csv_utils)
from csv_utils import update_attrs_file, update_price_file, update_tax_file, get_csv_col, delete_dups
import utils; reload(utils)
from utils import get_zpid_from_zillow_url

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("urls", help="file containing zillow sites to scrape")
parser.add_argument("-o", "--out", default='data/out.csv',
                     help="destination of home attributes output file")
parser.add_argument("-p", "--prices", default='data/prices.csv',
                     help="destination of price history output file")
parser.add_argument("-t", "--taxes", default='data/taxes.csv',
                     help="destination of tax history output file")
parser.add_argument("-l", "--headless", dest='headless', action='store_true',
                     help="boolen to indicate whether to run as headless")

parser.set_defaults(rentals=False)

args = parser.parse_args()

with open("sales.txt", "r") as f:
    urls = f.readlines()

def scrape_urls(browser, urls_path, out_path, price_history_path, tax_history_path):
    attrs_reviewed = get_csv_col(out_path, "zpid")
    price_reviewed = get_csv_col(price_history_path, "zpid")
    tax_reviewed = get_csv_col(tax_history_path, "zpid")
    
    num_urls = len(urls)
    for idx, url in enumerate(urls):
        print("\r{} / {}".format(idx + 1, num_urls), end="")
        zpid = get_zpid_from_zillow_url(url)

        in_attrs = zpid in attrs_reviewed
        in_price = zpid in price_reviewed
        in_tax = zpid in tax_reviewed

        if in_attrs and in_price and in_tax:
            continue

        browser.get(url)

        # attributes
        if not in_attrs:
            attrs = get_attrs_from_html(browser) or get_attrs_from_elements(browser)
            update_attrs_file(out_path, attrs)

        # price history
        if not in_price:
            price_history = get_price_history(browser)
            update_price_file(price_history_path, price_history)

        # tax history
        if not in_tax:
            tax_history = get_tax_history(browser)
            update_tax_file(tax_history_path, tax_history)
        
        sleep_time = min(3600, np.random.pareto(0.5) + 2)
        print("\r{} / {} sleeping: {:.2f}".format(idx + 1, num_urls, sleep_time), end="")
        sleep(sleep_time)
    return True

if __name__ == "__main__":
    print("Setting up browser")
    browser = setup_browser(sign_in=False, headless=args.headless)
    print("Scraping {}".format(args.urls))
    # try:
    scrape_urls(
        browser=browser,
        urls_path=args.urls,
        out_path=args.out,
        tax_history_path=args.taxes,
        price_history_path=args.prices)
    # except Exception as e:
    #     print(e)
    browser.close()
    # delete_dups(filename, "{}_no_dups.".format(filename))

# delete_dups("data/out.csv", "data/out.csv")