import os

DEBUG = False

SITE_NAME = "Stashboard"
SITE_AUTHOR = "Colonel Mustache"
SITE_URL = "http://stashbooard.appspot.com"
REPORT_URL = "mailto:help@stashboard.org"

# RSS Feed settings
RSS_NUM_EVENTS_TO_FETCH = 50

# OAuth Consumer Credentials
CONSUMER_KEY = 'anonymous'
CONSUMER_SECRET = 'anonymous'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
    )
