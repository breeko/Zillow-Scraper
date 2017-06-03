import pandas as pd
import os
from time import sleep
from random import random
import re

from selenium import webdriver
import selenium
import logging
import random
from collections import namedtuple

LOG_FILENAME = 'scraper_selenium.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

import config
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="file containing zillow sites to scrape")

parser.set_defaults(rentals=False)

args = parser.parse_args()


def setup_browser():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    browser = webdriver.Firefox(firefox_profile=firefox_profile)
    login_url = "http://www.zillow.com/user/acct/login"

    browser.get(login_url)
    sleep(5)
    
    login_by_email_buttons = browser.find_elements_by_xpath("//*[contains(@class, 'btn-email')]")
    if len(login_by_email_buttons) > 0:
        login_by_email_buttons[0].click()
        
    
    browser.find_element_by_id("reg-login-email").clear()
    browser.find_element_by_id("reg-login-email").send_keys("{}{}".format(config.email, webdriver.common.keys.Keys.TAB))
    browser.find_element_by_id("inputs-password").clear()
    browser.find_element_by_id("inputs-password").send_keys(config.password, webdriver.common.keys.Keys.RETURN)
    sleep(5)
    
    return browser

def get_zpid(url):
    return re.search('[0-9]+_zpid', url).group(0).split("_")[0]

def load_url(browser, url):
    """ Loads url in browser. URL can either be a direct link or the suffix of a zillow site """
    # url = "http://www.zillow.com/homedetails/2-W-Tecumseh-Ave-Strathmere-NJ-08248/2097281667_zpid/"
    if "zillow.com" not in url.lower():
        url = "http://www.zillow.com{}".format(url)
    browser.get(url=url)
    sleep(max(5, random.random() * 10))
    
    # toggle more facts/features/etc
    try:
        browser.find_element_by_xpath("//*[contains(@class,'moreless-toggle')]").click()
    except:
        return False
        
    try:
        # maximize price and tax history sections
        [maximize.click() for maximize in browser.find_elements_by_xpath("//*[@class='maximize']")]
    except:
        pass
    
    return True

def get_price_history(browser):
    # price history
    history = {}
    try:
        browser_price_history = browser.find_element_by_id("hdp-price-history")
        history_headers = [head.text for head in browser_price_history.find_elements_by_tag_name("th") if head.text != '']
        for row in browser_price_history.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr"):
            new_history = dict(list(zip(history_headers, [elem.text for elem in row.find_elements_by_tag_name("td")])))
            for k,v in new_history.items():
                history[k] = history.get(k, []) + [v]
        if len(history) > 0:
            history["zpid"] = get_zpid(browser.current_url)
    except selenium.common.exceptions.NoSuchElementException:
        # No price history
        pass
    return history
    

def get_tax_history(browser):
    history = {}
    try:
        browser_tax_history = browser.find_element_by_id("hdp-tax-history")
        tax_history_headers = [head.text for head in browser_tax_history.find_elements_by_tag_name("th") if head.text != '']
        
        for row in browser_tax_history.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr"):
            new_history = dict(list(zip(tax_history_headers, [elem.text for elem in row.find_elements_by_tag_name("td")])))
            for k,v in new_history.items():
                history[k] = history.get(k, []) + [v]
        if len(history) > 0:
            history["zpid"] = get_zpid(browser.current_url)
    except selenium.common.exceptions.NoSuchElementException:
        # No tax history
        pass
    return history

def get_attr(browser, xpath, elem_id, get_content_bool):
    try:
        vals = browser.find_elements_by_xpath(xpath)
        if elem_id < 0:
            if get_content_bool:
                return "|".join([val.get_attribute("content") for val in vals])
            return "|".join([val.text for val in vals])
        else:
            val = vals[elem_id]
            if get_content_bool:
                return val.get_attribute("content")
            return val.text
    except:
        return ""
            

def get_attrs(browser):

    Xpath_val = namedtuple("XPath_val", "xpath, elem_id get_content_bool")
    Xpath_val.__new__.__defaults__ = ("", 0, False)
    
    attrs_xpath_dict = {
        # attr: (element_number, get_content_bool, xpath)
        "state": Xpath_val("//*[@id='region-state']"),
        "city": Xpath_val("//*[@id='region-city']"),
        "zipcode": Xpath_val("//*[@id='region-zipcode']"),
        "description": Xpath_val("//*[contains(@class, 'content-item')]", elem_id=-1),
        "zestimate_median": Xpath_val("//*[contains(@class,'region-homevalues-zestimate')]//ancestor::h2"),
        "zestimate_market_temp": Xpath_val("//*[contains(@class,'market-temp')]//div[contains(@class,'h2')]"),
        "beds": Xpath_val("//*[@class='addr_bbs']"),
        "baths": Xpath_val("//*[@class='addr_bbs']", elem_id=1),
        "sqft": Xpath_val("//*[@class='addr_bbs']", elem_id=2),
        "school_1_name": Xpath_val("//div[contains(@class,'nearby-schools-name')]"),
        "school_1_grade": Xpath_val("//div[contains(@class,'nearby-schools-grades')]"),
        "school_1_distance": Xpath_val("//div[contains(@class,'nearby-schools-distance')]"),
        "school_1_rating": Xpath_val("//span[contains(@class, 'gs-rating-number')]"),
        "school_2_name": Xpath_val("//div[contains(@class,'nearby-schools-name')]", elem_id=1),
        "school_2_grade": Xpath_val("//div[contains(@class,'nearby-schools-grades')]", elem_id=1),
        "school_2_distance": Xpath_val("//div[contains(@class,'nearby-schools-distance')]", elem_id=1),
        "school_2_rating": Xpath_val("//span[contains(@class, 'gs-rating-number')]", elem_id=1),
        "school_3_name": Xpath_val("//div[contains(@class,'nearby-schools-name')]", elem_id=2),
        "school_3_grade": Xpath_val("//div[contains(@class,'nearby-schools-grades')]", elem_id=2),
        "school_3_distance": Xpath_val("//div[contains(@class,'nearby-schools-distance')]", elem_id=2),
        "school_3_rating": Xpath_val("//span[contains(@class, 'gs-rating-number')]", elem_id=2),
        "price": Xpath_val("//*[@property='product:price:amount']", get_content_bool=True),
        "longitude": Xpath_val("//*[@itemprop='longitude']", get_content_bool=True),
        "latitude": Xpath_val("//*[@itemprop='latitude']", get_content_bool=True),
        "facts": Xpath_val("//*[contains(@class, 'hdp-facts')]//ancestor::li", elem_id=-1),
        "zestimate": Xpath_val("//*[@class='zest-value']"),
        "zestimate_rent": Xpath_val("//*[@class='zest-value']", elem_id=1),
        "zestimate_median": Xpath_val("//*[@class='zest-value']", elem_id=2),
        "for_rent" : Xpath_val("//*[contains(@class, 'for-rent-row')]"),
        "for_sale" : Xpath_val("//*[contains(@class, 'for-sale-row')]"),
        
    }
    
    attrs = {k: [get_attr(browser, v.xpath, v.elem_id, v.get_content_bool)] for k,v in attrs_xpath_dict.items()}
    
    attrs["title"] = [browser.title.split("|")[0]]
    attrs["url"] = [browser.current_url]
    attrs["zpid"] = [get_zpid(browser.current_url)]

    return attrs

def run(filename, browser=None, output_filename="output.csv", tax_history_filename="tax_history.csv", price_history_filename="price_history.csv"):
    
    file = open(filename, 'r')
    data = file.readlines()
    data = [home.strip() for home in data]
    if browser is None:
        browser = setup_browser()
    
    if os.path.isfile(output_filename):
        df_attrs = pd.DataFrame.from_csv(output_filename)
    else:
        df_attrs = pd.DataFrame()
    
    if os.path.isfile(price_history_filename):
        df_price_history = pd.DataFrame.from_csv(price_history_filename)
    else:
        df_price_history = pd.DataFrame()
    
    if os.path.isfile(tax_history_filename):
        df_tax_history = pd.DataFrame.from_csv(tax_history_filename)
    else:
        df_tax_history = pd.DataFrame()
    
    for idx, home in enumerate(data):
        zpid = get_zpid(home)
        
        if zpid in df_attrs.index.astype(str):
            logging.debug("Skipping {}".format(home))    
            continue
        
        if not load_url(browser, home):
            # Failed to load site
            continue
        
        attrs = get_attrs(browser)
        price_history = get_price_history(browser)
        tax_history = get_tax_history(browser)
        
        new_df_attrs = pd.DataFrame.from_dict(attrs)
        if "zpid" in new_df_attrs:
            new_df_attrs = new_df_attrs.set_index(new_df_attrs.zpid).drop("zpid",axis=1)
        df_attrs = pd.concat([df_attrs, new_df_attrs])
        
        new_df_price_history = pd.DataFrame.from_dict(price_history)
        if "zpid" in new_df_price_history:
            new_df_price_history = new_df_price_history.set_index(new_df_price_history.zpid).drop("zpid",axis=1)
        df_price_history = pd.concat([df_price_history, new_df_price_history])
        
        new_df_tax_history = pd.DataFrame.from_dict(tax_history)
        if "zpid" in new_df_tax_history:
            new_df_tax_history = new_df_tax_history.set_index(new_df_tax_history.zpid).drop("zpid",axis=1)
        df_tax_history = pd.concat([df_tax_history, new_df_tax_history])
        
        df_attrs.to_csv(output_filename)
        df_price_history.to_csv(price_history_filename)
        df_tax_history.to_csv(tax_history_filename)
        
    return df_attrs, df_price_history, df_tax_history

if __name__ == "__main__":
    print("Scraping {}".format(args.filename))
    run(args.filename)

