__author__ = 'Kyle Conroy'

import config
import os
import sys
import logging
import wsgiref.handlers

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'utils/external'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.api import users
from handlers import restful


html = """
<!DOCTYPE html>
<html>
<head>
	<title>QUnit Test Suite</title>
	<link rel="stylesheet" href="/tests/qunit/qunit.css" type="text/css" media="screen">
	<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
	<script type="text/javascript" src="/tests/qunit/qunit.js"></script>
	<script type="text/javascript" src="/tests/tests/services.js"></script>
</head>
<body>
	<h1 id="qunit-header">QUnit Test Suite</h1>
	<h2 id="qunit-banner"></h2>
	<div id="qunit-testrunner-toolbar"></div>
	<h2 id="qunit-userAgent"></h2>
	<ol id="qunit-tests"></ol>
</body>
</html>
"""

class TestHandler(restful.Controller):
    def get(self):
        logging.debug("TestHandler#get")
        self.response.headers["Content-Type"] = "text/html"
        self.response.out.write(html)        

ROUTES = [
    ('/.*$', TestHandler),
]

def main():
    application = webapp.WSGIApplication(ROUTES, debug=config.DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
