from imp import reload

import attributes_from_html; reload(attributes_from_html)
from attributes_from_html import get_attrs_from_html

# import attributes_from_elements; reload(attributes_from_elements)
from attributes_from_elements import get_attrs_from_elements

import save_utils; reload(save_utils)
from save_utils import update_attrs_file, update_price_file, update_tax_file

import history; reload(history)
from history import get_price_history, get_tax_history

from browser import setup_browser

browser = setup_browser()
# for sale only one school
browser.get("https://www.zillow.com/homedetails/10-W-66th-St-APT-4F-New-York-NY-10023/244830422_zpid/")

# for sale lots of new lines
browser.get("https://www.zillow.com/homes/for_sale/2088482280_zpid/40.764893,-73.967578,40.755661,-73.995044_rect/14_zm/1_fr/")

# for sale w/ unit number
browser.get("https://www.zillow.com/homes/for_sale/2117077958_zpid/40.768955,-73.967579,40.751597,-73.995045_rect/14_zm/1_fr/")

# rental, get_attrs_from_html won't work
browser.get("https://www.zillow.com/homes/for_sale/2086213875_zpid/40.807118,-73.924342,40.737697,-74.034205_rect/12_zm/1_fr/")


### Scraping the site

# attributes
attrs = get_attrs_from_html(browser) or get_attrs_from_elements(browser)
update_attrs_file("data/out.csv", attrs)

# price history
price_history = get_price_history(browser)
update_price_file("data/prices.csv", price_history)

# tax history
tax_history = get_tax_history(browser)
update_tax_file("data/taxes.csv", tax_history)
