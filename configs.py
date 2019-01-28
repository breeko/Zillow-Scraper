import numpy as np

# number of scrapes before browser is reset
RESET_BROWSER = 10

# maximum number of consecutive failures in a scraping session
MAX_CONSECUTIVE_FAILURES = 3

# maximum number of failures in a scraping session
MAX_FAILURES = 100

# maximum number of timeouts in a scraping session
MAX_TIMEOUTS = 25

# maximum number of captchas in a scraping session
MAX_CAPTCHA = 10

# seconds to sleep after scrape failure
SLEEP_AFTER_FAILURE = lambda: 60 * 60

# seconds to sleep after scrape success
SLEEP_BETWEEN_SCRAPE = lambda: min(3600, np.random.pareto(1) + 2)

# seconds to sleep after timeout
SLEEP_AFTER_TIMEOUT = lambda: 60