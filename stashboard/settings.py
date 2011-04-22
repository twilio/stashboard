import os
import logging

DEBUG = False

SITE_NAME = "Stashboard"
SITE_URL = "http://stashbooard.appspot.com"
SITE_AUTHOR = "Colonel Mustache"
PUBSUBHUBBUB_URL = "http://pubsub.example.com"

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), "templates"))

logging.error(TEMPLATE_DIRS)
