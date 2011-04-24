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

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))

import logging
import wsgiref.handlers
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.api import users
from handlers import site, api, admin
from models import Status, Setting

ROUTES = [
    #('/*[^/]', site.) redirect pages without slashed to pages with slashes

    #API
    (r'/api/(.+)/services/(.+)/events/current', api.CurrentEventHandler),
    (r'/api/(.+)/services/(.+)/events', api.EventsListHandler),
    (r'/api/(.+)/services/(.+)/events/(.+)', api.EventInstanceHandler),
    (r'/api/(.+)/services/(.+)', api.ServiceInstanceHandler),
    (r'/api/(.+)/services', api.ServicesListHandler),
    (r'/api/(.+)/statuses/(.+)', api.StatusInstanceHandler),
    (r'/api/(.+)/statuses', api.StatusesListHandler),
    (r'/api/(.+)/status-images', api.ImagesListHandler),
    (r'/api/(.+)/levels', api.LevelsListHandler),
    (r'/api/.*', api.NotFoundHandler),

    #SITE
    (r'/*$', site.RootHandler),
    (r'/403.html', site.UnauthorizedHandler),
    (r'/404.html', site.NotFoundHandler),
    (r'/services/(.+)/(.+)/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)', site.ServiceHandler),
    (r'/documentation/credentials', site.ProfileHandler),
    (r'/documentation/verify', site.VerifyAccessHandler),
    (r'/documentation/(.+)', site.DocumentationHandler),

    #ADMIN
    (r'/admin/api', admin.SiteHandler),
    (r'/admin/site/setup', admin.SetupHandler),
    (r'/admin/site', admin.SiteHandler),
    (r'/admin', admin.RootHandler),

    (r'/.*$', site.NotFoundHandler),
    ]

def application():
    return webapp.WSGIApplication(ROUTES, debug=True)

def main():
    # Check if defaults have been installed
    # installed_defaults = memcache.get("installed_defaults")
    # if installed_defaults is None:
    #     installed_defaults = Setting.all().filter('name = ', 'installed_defaults').get()
    #     if installed_defaults is None:
    #         logging.info("Installing default statuses")
    #         Status.install_defaults()
    #     if not memcache.add("installed_defaults", True):
    #         logging.error("Memcache set failed.")
    wsgiref.handlers.CGIHandler().run(application())

if __name__ == "__main__":
    main()
