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
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))

import appengine_config # Make sure this happens

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from handlers import site, api, admin

API = [
    (r'/api/(.+)/levels', api.LevelListHandler), #DEPRECATED
    (r'/api/(.+)/services/(.+)/events/current', api.CurrentEventHandler),
    (r'/api/(.+)/services/(.+)/events', api.EventsListHandler),
    (r'/api/(.+)/services/(.+)/events/(.+)', api.EventInstanceHandler),
    (r'/api/(.+)/services/(.+)', api.ServiceInstanceHandler),
    (r'/api/(.+)/services', api.ServicesListHandler),
    (r'/api/(.+)/statuses/(.+)', api.StatusInstanceHandler),
    (r'/api/(.+)/statuses', api.StatusesListHandler),
    (r'/api/(.+)/service-lists/(.+)', api.ListInstanceHandler),
    (r'/api/(.+)/service-lists', api.ListsListHandler),
    (r'/api/(.+)/status-images', api.ImagesListHandler),
    (r'/api/.*', api.NotFoundHandler),
    ]

SITE = [
    (r'/*$', site.RootHandler),
    (r'/403.html', site.UnauthorizedHandler),
    (r'/404.html', site.NotFoundHandler),
    (r'/services/(.+)/(.+)/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)/(.+)', site.ServiceHandler),
    (r'/services/(.+)', site.ServiceHandler),
    (r'/service-lists/(.+)', site.ListHandler),
    (r'/service-lists', site.ListListHandler),
    (r'/summary', site.ListSummaryHandler),
    (r'/documentation/credentials', site.CredentialsRedirectHandler),
    (r'/documentation/(.+)', site.DocumentationHandler),
    (r'/documentation', site.BaseDocumentationHandler),
    (r'/rss', site.RSSHandler),
    ]

ADMIN = [
    #(r'/admin/api', admin.SetupHandler),
    (r'/admin/setup', admin.SetupHandler),
    (r'/admin/setup/skip', admin.SkipHandler),
    (r'/admin/services/create', admin.CreateServiceHandler),
    (r'/admin/services/(.*)/events/(.*)/delete', admin.DeleteEventHandler),
    (r'/admin/services/(.*)/note/create', admin.NoteHandler),
    (r'/admin/services/(.*)/events/create', admin.UpdateStatusHandler),
    (r'/admin/services/(.*)/delete', admin.DeleteServiceHandler),
    (r'/admin/services/(.*)/edit', admin.EditServiceHandler),
    (r'/admin/services/(.*)', admin.ServiceInstanceHandler),
    (r'/admin/services', admin.ServiceHandler),
    (r'/admin/statuses/(.*)/delete', admin.DeleteStatusHandler),
    (r'/admin/statuses/(.*)/edit', admin.EditStatusHandler),
    (r'/admin/statuses/create', admin.CreateStatusHandler),
    (r'/admin/statuses', admin.StatusHandler),
    (r'/admin/service-lists/(.*)/delete', admin.DeleteListHandler),
    (r'/admin/service-lists/(.*)/edit', admin.EditListHandler),
    (r'/admin/service-lists/create', admin.CreateListHandler),
    (r'/admin/service-lists', admin.ListHandler),
    (r'/admin/migrations/(.*)', admin.MigrationStarter),
    (r'/admin/migrations', admin.MigrationHandler),
    (r'/admin/credentials', admin.CredentialHandler),
    (r'/admin/oauth/authorize', admin.OAuthRequestHandler),
    (r'/admin/oauth/verify', admin.OAuthVerifyHandler),
    (r'/admin/tasks/invalidate-cache', admin.InvalidateCacheHandler),
    (r'/admin/tweet', admin.EventTweetHandler),
    (r'/admin', admin.RootHandler),
    ]

ROUTES = []
ROUTES.extend(SITE)
ROUTES.extend(ADMIN)
ROUTES.extend([ ("/admin" + a[0], a[1]) for a in API ])
ROUTES.extend([ (a[0], a[1].readonly()) for a in API ])
ROUTES.append((r'/.*$', site.NotFoundHandler))

def application():
    return webapp.WSGIApplication(ROUTES, debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()
