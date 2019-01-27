from selenium.webdriver.common.by import By
import re
from utils.utils import regex_group_or_default

class SearchValBy(By):
    REGEX = "regex"

class SearchValOr:
    def __init__(self, searchVals):
        self.searchVals = searchVals
    
    def get_attr(self, browser):
        for searchVal in self.searchVals:
            out = searchVal.get_attr(browser)
            if out:
                return out
        return ""

    def get_elems(self, browser):
        for searchVal in self.searchVals:
            out = searchVal.get_elems(browser)
            if out:
                return out


class SearchVal:
    def __init__(self, val, by=SearchValBy.XPATH, elem_id=0, get_content_bool=False, process=None, sep=";"):
        self.val = val
        self.by = by
        self.elem_id = elem_id
        self.get_content_bool = get_content_bool
        self.process = process
        self.sep = sep

    def copy(self, val=None, by=None, elem_id=None, get_content_bool=None, process=None):
        val = val or self.val
        by = by or self.by
        elem_id = elem_id or self.elem_id
        get_content_bool = get_content_bool or self.get_content_bool
        process = process or self.process
        return SearchVal(val=val, by=by, elem_id=elem_id, get_content_bool=get_content_bool, process=process)

    def get_elems(self, browser):
        try:
            vals = browser.find_elements(self.by, self.val)
            if self.elem_id is not None:
                vals = [vals[self.elem_id]]
        except:
            vals = []
        return vals

    def get_attr(self, browser):
        if self.by == SearchValBy.REGEX:
            out = self._get_attr_regex(browser)
        else:
            out =  self._get_attr_browser(browser)
        if self.process:
            return self.process(out)
        return out
    
    def _get_attr_regex(self, browser):
        inner_html = browser.execute_script("return document.body.innerHTML")
        match = re.search(self.val, inner_html, flags=re.MULTILINE)
        out = ""
        if match:
            try:
                out = match.group(self.elem_id)
            except IndexError:
                pass
        return out

    def _get_attr_browser(self, browser):
        try:
            elems = self.get_elems(browser)
            if self.get_content_bool:
                attr = self.sep.join([val.get_attribute("content") for val in elems])
            else:
                attr = self.sep.join([val.text for val in elems])
        except:
            attr = ""
        return attr
