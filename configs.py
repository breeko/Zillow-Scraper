import numpy as np

# maximum number of consecutive failures in a scraping session
MAX_CONSECUTIVE_FAILURES = 3

# maximum number of failures in a scraping session
MAX_FAILURES = 100

# maximum number of timeouts in a scraping session
MAX_TIMEOUTS = 25

# seconds to sleep after scrape failure
SLEEP_AFTER_FAILURE = lambda: 60 * 60

# seconds to sleep after scrape success
SLEEP_BETWEEN_SCRAPE = lambda: min(3600, np.random.pareto(1) + 2)

# seconds to sleep after timeout
SLEEP_AFTER_TIMEOUT = lambda: 60