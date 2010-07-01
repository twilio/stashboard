import os
import logging

# Stupid error
from google.appengine.dist import use_library
use_library('django', '1.1')

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

#Stashboard version
VERSION = "1.0.0"

# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
logging.info("Starting application in DEBUG mode: %s", DEBUG)

# Don't change default_blog or default_page to prevent conflicts when merging #  Bloog source code updates.
# Do change blog or page dictionaries at the bottom of this config module.

SITE = {
    "html_type": "text/html",
    "charset": "utf-8",
    "title": "Is My Webservice Down?",
    "author": "Kyle Conroy",
    # This must be the email address of a registered administrator for the 
    # application due to mail api restrictions.
    "email": "kyle.j.conroy@gmail.com",
    "description": "A RESTful Status Tracker on top of App Engine.",
    "root_url": "http://ismywebservicedown.appspot.com",
    "master_atom_url": "/feeds/atom.xml",
    "template_path": os.path.join(APP_ROOT_DIR, "views/default"),
    "rich_client": True, #If false, the website will go into a simplified read-only view
}
