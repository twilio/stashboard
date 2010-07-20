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
