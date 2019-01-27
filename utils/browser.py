from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from time import sleep
import credentials

def setup_browser(sign_in=False,headless=False):
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    options = Options()
    if headless:
        options.add_argument('--headless')

    browser = webdriver.Firefox(firefox_profile=firefox_profile, options=options)

    if sign_in:
        login_url = "http://www.zillow.com/user/acct/login"
        browser.get(login_url)
        sleep(5)

        login_by_email_buttons = browser.find_elements_by_xpath("//*[contains(@class, 'btn-email')]")
        if len(login_by_email_buttons) > 0:
            login_by_email_buttons[0].click()
            
        browser.find_element_by_id("reg-login-email").clear()
        browser.find_element_by_id("reg-login-email").send_keys("{}{}".format(credentials.email, webdriver.common.keys.Keys.TAB))
        browser.find_element_by_id("inputs-password").clear()
        browser.find_element_by_id("inputs-password").send_keys(credentials.password, webdriver.common.keys.Keys.RETURN)
        sleep(5)
    
    return browser

