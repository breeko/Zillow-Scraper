import re
import datetime as dt
from time import sleep

TIME_FORMAT = "%Y-%m-%d-%H:%M:%S"

def add_time(d, key="added"):
    with_time = {**d}
    with_time[key] = dt.datetime.now().strftime(TIME_FORMAT)
    return with_time

def clean_dict(d):
    return {k: v if type(v) is not str else clean_text(v) for k, v in d.items()}

def keep_digits(s):
    return re.sub(r"[^\d\\.]","", s)

def clean_text(s):
    cleaner = re.sub(r"\n+"," ", s)         # remove newlines and commas
    cleaner = re.sub(r",","", cleaner)      # remove commas
    cleaner = re.sub(r"^ ", "", cleaner)    # remove leading spaces
    cleaner = re.sub(r" $", "", cleaner)    # remove trailing spaces
    clean = re.sub(r" {2,}", " ", cleaner)  # remove multiple spaces
    return clean

def match_after(val, s, process=None):
    """ Matches text following some starting value """
    match = re.search(r"(?<=^{}).+".format(val), s)
    if match and process:
        return process(match.group(0))
    return match

def get_zpid_from_zillow_url(url, default=""):
    return regex_group_or_default(r"\d+(?=_zpid)", url, group=0, default=default)

def get_zip_from_zillow_url(url):
    try:
        zipcode = url.split("/")[4].split("-")[-1]
    except IndexError:
        zipcode = ""
    return zipcode

def regex_or_default(re_function, get_function, pattern, string, default):
    out = default
    match = re_function(pattern, string)
    if match:
        try:
            out = get_function(match)
        except IndexError:
            pass
    return out

def regex_group_or_default(pattern, string, group=0, default=""):
    return regex_or_default(re.search, lambda x: x.group(group), pattern, string, default)

def regex_match_or_default(pattern, string, match=0, default=""):
    return regex_or_default(re.findall, lambda x: x[match], pattern, string, default)

def remove_paren(s):
    return s.replace('"', "").replace("'", "")

def table_to_dict(browser, table_id):
    """ Converts a table in a browser into a dictionary """
    headers = [h.text for h in browser.find_elements_by_xpath("//thead//th")]
    outs = []
    for row in browser.find_elements_by_xpath('//*[@id="{}"]//tr'.format(table_id)):
        vals = [x.text for x in row.find_elements_by_tag_name("td")]
        out = {h: v for h, v in zip(headers, vals) if h != ""}
        if len(out) > 0:
            outs.append(out)
    return outs

def get_from_dict(d, keys):
    """ Returns a value from a dictionary based on a list of keys. If any key is not found, returns None """
    out = d
    for key in keys:
        if out is None:
            break
        out = out.get(key)
    return out

def sleep_verbose(message, sleep_time):
    for sleep_time_remaining in range(sleep_time, 0, -1):
            print("\r{} sleep: {:.0f}".format(message, sleep_time_remaining).ljust(40), end="")
            sleep(1)
