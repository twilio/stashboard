# Copyright (c) 2010 Twilio Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import logging

from google.appengine.dist import use_library
use_library('django', '1.1')

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

#Stashboard version
VERSION = "1.1.6"

# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
logging.info("Starting application in DEBUG mode: %s", DEBUG)

SITE = {
    "html_type": "text/html",
    "charset": "utf-8",
    "title": "Stashboard",
    "author": "Kyle Conroy",
    # This must be the email address of a registered administrator for the 
    # application due to mail api restrictions.
    "email": "kyle.j.conroy@gmail.com",
    "description": "A RESTful Status Tracker on top of App Engine.",
    "root_url": "http://stashboard.appspot.com",
    "template_path": os.path.join(APP_ROOT_DIR, "views/default"),
    "rich_client": True, #If false, the website will go into a simplified read-only view
}
