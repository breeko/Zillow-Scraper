from imp import reload
import search_val; reload(search_val)
from utils.search_val import SearchVal, SearchValOr, SearchValBy, regex_group_or_default 
from utils.utils import keep_digits, clean_dict, clean_text, match_after, add_time

# alternative to parsing SEO information from html
# this searches props from the rendered site

beds_class = SearchVal("//*[@class='addr_bbs']", process=keep_digits)
baths_class = beds_class.copy(elem_id=1)
sqft_class = beds_class.copy(elem_id=2)

beds_regex = SearchVal(
    val="//h3[contains(@class, 'edit-facts-light')]",
    process=lambda x: regex_group_or_default(r"[\d]+(?= beds?)", x))

baths_regex = beds_regex.copy(process=lambda x: regex_group_or_default(r"[\d]+(?= baths?)", x))
sqft_regex = beds_regex.copy(process=lambda x: regex_group_or_default(r"[\d]+(?= sqft?)", x))

# Buttons that need to be clicked
BUTTONS = [
    SearchVal("More", SearchValBy.LINK_TEXT),                           # show facts and figures
    SearchVal("See More Facts and Features", SearchValBy.LINK_TEXT),    # expand description
    SearchVal("//section[@id='nearbySchools' and contains(@class, 'collapsed')]//ancestor::h2") # expand schools
]

# Attribute mappings
ATTRIBUTES = {
    "city": SearchValOr([
        SearchVal("//*[@id='region-city']"),
        SearchVal("//*[@class='zsg-h2']", process=lambda s: regex_group_or_default(r"[^,]+", s))
    ]),
    "state": SearchValOr([
        SearchVal("//*[@id='region-state']"),
        SearchVal("//*[@class='zsg-h2']", process=lambda s: regex_group_or_default(r"(?<=, )[^ ]+", s))
    ]),
    "zipcode": SearchValOr([
        SearchVal("//*[@id='region-zipcode']"),
        SearchVal("//*[@class='zsg-h2']", process=lambda s: regex_group_or_default(r"[^ ]+$", s))
    ]),
    "zpid": SearchVal(r"(?<=zpid=)[\d]+", SearchValBy.REGEX),
    "url:": browser.current_url,
    "address": SearchVal("//*[contains(@class, 'addr')]"),
    "description": SearchVal("//*[@id='home-description-container']", process=clean_text),
    "beds": SearchValOr(searchVals=[beds_class, beds_regex]),
    "baths": SearchValOr(searchVals=[baths_class, baths_regex]),
    "sqft": SearchValOr(searchVals=[sqft_class, sqft_regex]),
    "home_type": SearchValOr([
        SearchVal("//*[contains(@class, 'hdp-fact-ataglance-value')]"),
        SearchVal("//*[contains(@class, 'fact-value')]")
    ]),
    "school_1_name": SearchVal("//a[@class='school-name notranslate']"),
    "school_1_grades": SearchVal("//div[contains(@class,'nearby-schools-grades')]"),
    "school_1_distance": SearchVal("//div[contains(@class,'nearby-schools-distance')]", process=keep_digits),
    "school_1_rating": SearchVal("//span[contains(@class, 'gs-rating-number')]"),
    "school_2_name": SearchVal("//a[@class='school-name notranslate']", elem_id=1),
    "school_2_grades": SearchVal("//div[contains(@class,'nearby-schools-grades')]", elem_id=1),
    "school_2_distance": SearchVal("//div[contains(@class,'nearby-schools-distance')]", elem_id=1),
    "school_2_rating": SearchVal("//span[contains(@class, 'gs-rating-number')]", elem_id=1),
    "school_3_name": SearchVal("//a[@class='school-name notranslate']", elem_id=2),
    "school_3_grades": SearchVal("//div[contains(@class,'nearby-schools-grades')]", elem_id=2),
    "school_3_distance": SearchVal("//div[contains(@class,'nearby-schools-distance')]", elem_id=2),
    "school_3_rating": SearchVal("//span[contains(@class, 'gs-rating-number')]", elem_id=2),
    "price": SearchValOr([
        SearchVal("//*[contains(@class,'home-summary-row')]", elem_id=1, process=keep_digits),
        SearchVal("//*[@class='price']", process=keep_digits)
    ]),
    "longitude": SearchVal("//*[@itemprop='longitude']", get_content_bool=True),
    "latitude": SearchVal("//*[@itemprop='latitude']", get_content_bool=True),
    "facts": SearchVal("//*[@class='fact-label'] | //*[@class='fact-value']", elem_id=None, process=clean_text),
    "zestimate": SearchValOr([
        SearchVal("//*[@class='zest-value']", process=lambda s: match_after("Zestimate", s, process=keep_digits)),
        SearchVal("//*[@class='zestimate']", process=lambda s: match_after("Zestimate", s, process=keep_digits))
    ]),
    "rent_zestimate": SearchValOr([
        SearchVal("//*[@class='zest-value']", process=lambda s: match_after("Rent Zestimate", s, process=keep_digits)),
        SearchVal("//*[@class='home-summary-row']", process=lambda s: match_after("Rent Zestimate", s, process=keep_digits))
    ]),
    "home_status": SearchValOr([
        SearchVal("//*[@class='status']"),
        SearchVal("//*[contains(@class, 'for-rent-row')]"),
        SearchVal("//*[contains(@class, 'for-sale-row')]")]
    )
}

def click_buttons(browser):
    for buttons in BUTTONS:
        match_buttons = buttons.get_elems(browser)
        for button in match_buttons:
            button_id = button.get_attribute("id")
            if button_id:
                script = "{}.click();".format(button_id)
                browser.execute_script(script)

def get_attrs_from_elements(browser):
    click_buttons(browser)
    attrs = {k: v.get_attr(browser) for k, v in ATTRIBUTES.items()}
    attrs = add_time(attrs)
    return clean_dict(attrs)

