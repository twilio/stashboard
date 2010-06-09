# The MIT License
# 
# Copyright (c) 2008 William T. Katz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.


__author__ = 'Kyle Conroy'

import config
import os
import sys

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'utils/external'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


import logging
import wsgiref.handlers
from firepython.middleware import FirePythonWSGI
from google.appengine.ext import webapp
from google.appengine.api import users

from handlers import site, api

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
    ('/*$', site.RootHandler),
    #('/*[^/]', site.) redirect pages without slashed to pages with slashes
    
    #API
    ('/403.html', site.UnauthorizedHandler),
    ('/404.html', site.NotFoundHandler),
    (r'/api/services', api.ServicesListHandler),
    (r'/api/services/(.*)/events', api.EventsListHandler),
    (r'/api/services/(.*)/events/current', api.CurrentEventHandler),
    (r'/api/services/(.*)/events/(.*)', api.EventInstanceHandler),
    (r'/api/services/(.*)', api.ServiceInstanceHandler),
    (r'/api/statuses', api.StatusesListHandler),
    (r'/api/statuses/(.*)', api.StatusInstanceHandler),
    (r'/api/.*', api.NotFoundHandler),
    
    #SITE
    (r'/services/(.*)/(.*)/(.*)/(.*)', site.ServiceHandler),
    (r'/services/(.*)/(.*)/(.*)', site.ServiceHandler),
    (r'/services/(.*)/(.*)', site.ServiceHandler),
    (r'/services/(.*)', site.ServiceHandler),
    (r'/documentation', site.DocumentationHandler),
    (r'/profile', site.ProfileHandler),
    (r'/profile/verify', site.VerifyAccessHandler),
    
    ('/.*$', site.NotFoundHandler),
    
    
]

def main():
    application = webapp.WSGIApplication(ROUTES, debug=config.DEBUG)
    if users.is_current_user_admin():
        application = FirePythonWSGI(application)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
