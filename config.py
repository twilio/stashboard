import os
import logging

# Stupid error
# from google.appengine.dist import use_library
# use_library('django', '1.1')

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
logging.info("Starting application in DEBUG mode: %s", DEBUG)

# Don't change default_blog or default_page to prevent conflicts when merging #  Bloog source code updates.
# Do change blog or page dictionaries at the bottom of this config module.

SITE = {
    "key" : "statusKeyUnique",
    "default" : "up",
    "options" : {
        #status : message
        "up" : "All Good Captain",
        "down" : "I've made a huge mistake",
        "partial" : "Something is wrong",
        "rainbow" : "Taste The Rainbow"
    },
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
    "twitter": "twitter",

    # If you want to use legacy ID mapping for your former blog platform,
    # define it here and insert the necessary mapping code in the
    # legacy_id_mapping() function in ArticleHandler (blog.py).
    # Currently only "Drupal" is supported.
    #"legacy_blog_software": None,
    #"legacy_blog_software": "Drupal",
    #"legacy_blog_software": "Serendipity",
    
    # If you want imported legacy entries _not_ mapped in the file above to
    # redirect to their new permanent URL rather than responding on their
    # old URL, set this flag to True.
    #"legacy_entry_redirect": False,
}
