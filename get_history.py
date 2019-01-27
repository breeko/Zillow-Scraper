from utils.utils import table_to_dict, regex_group_or_default, get_zpid_from_zillow_url
import selenium.webdriver.support.ui as ui

# This file has the functions related to getting price and tax history
def get_history(browser, table):
    try:
        wait = ui.WebDriverWait(browser,10)
        price_and_tax_history_xpath = '//*[@id="price-and-tax-history" and contains(@class,"collapsed")]'
        buttons = browser.find_elements_by_xpath(price_and_tax_history_xpath)
        if len(buttons) > 0:
            buttons[0].click()
        table_xpath = '//a[@href="#{}"]'.format(table)
        wait.until(lambda browser: browser.find_elements_by_xpath(table_xpath))
        browser.find_element_by_xpath(table_xpath).click()
        rows = table_to_dict(browser, table)
        rows = [{k.lower(): v for k, v in row.items()} for row in rows]
        zpid = get_zpid_from_zillow_url(browser.current_url, default=browser.current_url)
        for row in rows:
            row["zpid"] = zpid
        return rows
    except:
        return []

def get_price_history(browser):
    return get_history(browser, "hdp-price-history")

def get_tax_history(browser):
    return get_history(browser, "hdp-tax-history")
