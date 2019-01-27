import urllib.request
import re
import os
from time import sleep
from random import random
from utils.browser import setup_browser
from selenium.common.exceptions import StaleElementReferenceException
import argparse
from utils.csv_utils import delete_dups

from utils.utils import get_zip_from_zillow_url

parser = argparse.ArgumentParser()
parser.add_argument("zipcodes", help="file containing zipcodes to scrape")
parser.add_argument("-r", "--rentals", dest='rentals', action='store_false',
                     help="boolen to indicate whether to scrape rentals")
parser.add_argument("-l", "--headless", dest='headless', action='store_true',
                     help="boolen to indicate whether to run as headless")
parser.add_argument("-o", "--out", dest='out', default="urls.txt",
                     help="output file to save the urls")

parser.set_defaults(rentals=False)

args = parser.parse_args()

def scrape(driver, zipcodes, filename, rentals=False):
    if rentals:
        base_url = "https://www.zillow.com/homes/for_rent/"
    else:
        base_url = "https://www.zillow.com/homes/for_sale/"
        # next: /homes/New-Jersey_rb/2_p/
    
    f = open(filename, 'a')
    
    urls_added = set(open(filename).read().split())
    zipcodes_added = set([get_zip_from_zillow_url(url) for url in urls_added])
    
    zipcodes = open(zipcodes).read().split()

    for zipcode in zipcodes:
        if zipcode in zipcodes_added:
            continue
        url = base_url + zipcode + "_rb/"
        
        html = None

        current_page = 1
        current_url = url
        num_stale_elements_attempts = 5

        while True:
            home_links = [] # used if stale elements prevent getting home links and need to move on
            
            try:
                driver.get(current_url)
                sleep(2)
                html = driver.page_source
            except KeyboardInterrupt:
                break
            except:
                print("Something went wrong...")
                sleep(5)
                continue

            try:
                num_results = int(re.search('"totalResultCount":[0-9]+', html).group(0).split(":")[-1])
            except:
                print("No results for zipcode {}".format(zipcode))

            for _ in range(num_stale_elements_attempts):
                try:
                    links = [elem.get_attribute("href") for elem in driver.find_elements_by_tag_name("a")]
                    home_links = set([l for l in links if l and l.endswith("zpid/")])
                    break
                except StaleElementReferenceException:
                    "stale element..."
                    sleep(1)
            
            if len(home_links) == 0 or num_results == 0 or home_links.issubset(urls_added):
                break
            
            f.write('\n'.join(home_links))
            f.write('\n')
            
            print(current_url + "\tItems added: " + str(len(home_links)))
            
            current_page += 1
            current_url = url + str(current_page) + "_p/"

            urls_added = urls_added.union(home_links)
            sleep(random() * 5)

        zipcodes_added.add(zipcode)

    f.close()
    return filename

if __name__ == "__main__":
    print("Setting up browser")
    driver = setup_browser(sign_in=False, headless=args.headless)
    
    print("Scraping {}".format(args.zipcodes))
    try:
        filename = scrape(driver=driver, zipcodes=args.zipcodes, filename=args.out, rentals=args.rentals)
    except Exception as e:
        print(e)
    driver.close()
    delete_dups(filename, "{}_no_dups.".format(filename))
    
