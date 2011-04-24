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

import datetime
import calendar
import cgi
import logging
import oauth2 as oauth
import os
import re
import string
import urllib
import urlparse

from datetime import date, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from models import Status, Service, Event, Profile, AuthRequest
from time import mktime
from utils import authorized
from wsgiref.handlers import format_date_time

def default_template_data():
    data = {
        "title": settings.SITE_NAME,
        "report_url": settings.REPORT_URL,
        }

    data["user"] = users.get_current_user()
    if data["user"]:
        data["logout_url"] = users.create_logout_url("/")

    return data

def get_past_days(num):
    date = datetime.date.today()
    dates = []

    for i in range(1, num+1):
        dates.append(date - datetime.timedelta(days=i))

    return dates


class BaseHandler(webapp.RequestHandler):

    def error(self, code):
        super(BaseHandler, self).error(code)
        self.render(default_template_data(), "404.html")

    def render(self, template_values, filename):
        self.response.out.write(render_to_string(filename, template_values))


class NotFoundHandler(BaseHandler):

    def get(self):
        self.error(404)


class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        self.error(403)


class RootHandler(BaseHandler):

    def get(self):
        q = Service.all()
        services = q.order("name").fetch(100)

        td = default_template_data()
        td["days"] = get_past_days(5)
        td["services"] = services
        td["services_json"] = json.dumps([ {"slug": s.slug} for s in services])
        td["statuses"] = Status.all().fetch(100)

        self.render(td, 'index.html')

class ServiceHandler(BaseHandler):

    @authorized.force_ssl(only_admin=True)
    def get(self, service_slug, year=None, month=None, day=None):
        user = users.get_current_user()
        logging.debug("ServiceHandler#get")

        service = Service.get_by_slug(service_slug)

        if not service:
            self.render({}, "404.html")
            return

        try:
            if day:
                start_date = date(int(year),int(month),int(day))
                end_date = start_date + timedelta(days=1)
            elif month:
                start_date = date(int(year),int(month),1)
                days = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = start_date + timedelta(days=days)
            elif year:
                start_date = date(int(year),1,1)
                end_date = start_date + timedelta(days=365)
            else:
                start_date = None
                end_date = None
        except ValueError:
            self.render({},'404.html')
            return

        td = default_template_data()
        td["service"] = service_slug

        if start_date and end_date:
            start_stamp = mktime(start_date.timetuple())
            end_stamp = mktime(end_date.timetuple())
            # Remove GMT from the string so that the date is
            # is parsed in user's time zone
            td["start_date"] = start_date
            td["end_date"] = end_date
            td["start_date_stamp"] = format_date_time(start_stamp)[:-4]
            td["end_date_stamp"] = format_date_time(end_stamp)[:-4]
        else:
            td["start_date"] = None
            td["end_date"] = None

        self.render(td, 'service.html')

class DebugHandler(BaseHandler):

    @authorized.force_ssl()
    def get(self):
        logging.debug("DebugHandler %s", self.request.scheme)
        td = default_template_data()
        self.render(td,'base.html')


class BasicRootHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        logging.debug("BasicRootHandler#get")

        q = Service.all()
        q.order("name")
        services = q.fetch(100)

        p = Status.all()
        p.order("severity")

        past = get_past_days(5)

        td = default_template_data()
        td["services"] = q.fetch(100)
        td["statuses"] = p.fetch(100)
        td["past"] = past
        td["default"] = Status.default()

        self.render(td, 'basic','index.html')

class BasicServiceHandler(BaseHandler):

    def get(self, service_slug, year=None, month=None, day=None):
        user = users.get_current_user()
        logging.debug("BasicServiceHandler#get")

        service = Service.get_by_slug(service_slug)


        if not service:
            self.render({}, "404.html")
            return

        events = service.events
        show_admin = False

        try:
            if day:
                start_date = date(int(year),int(month),int(day))
                end_date = start_date + timedelta(days=1)
            elif month:
                start_date = date(int(year),int(month),1)
                days = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = start_date + timedelta(days=days)
            elif year:
                start_date = date(int(year),1,1)
                end_date = start_date + timedelta(days=365)
            else:
                start_date = None
                end_date = None
                show_admin = True
        except ValueError:
            self.render({},'404.html')
            return

        if start_date and end_date:
            events.filter('start >= ', start_date).filter('start <', end_date)

        events.order("-start")

        td = default_template_data()
        td["service"] = service
        td["events"] = events.fetch(100)
        td["start_date"] = start_date
        td["end_date"] = end_date

        self.render(td, 'basic','service.html')

class DocumentationHandler(BaseHandler):

    def get(self, page):
        td = default_template_data()

        if page == "overview":
            td["overview_selected"] = True
            self.render(td, 'overview.html')
        elif page == "rest":
            td["rest_selected"] = True
            self.render(td, 'restapi.html')
        elif page == "examples":
            td["example_selected"] = True
            self.render(td, 'examples.html')
        else:
            self.render({},'404.html')



class VerifyAccessHandler(BaseHandler):

    @authorized.force_ssl()
    @authorized.role("admin")
    def get(self):
        oauth_token = self.request.get('oauth_token', default_value=None)
        oauth_verifier = self.request.get('oauth_verifier', default_value=None)
        user = users.get_current_user()
        authr = AuthRequest.all().filter('owner = ', user).get()

        if oauth_token and oauth_verifier and user and authr:

            host = self.request.headers.get('host', 'nohost')
            access_token_url = 'https://%s/_ah/OAuthGetAccessToken' % host

            consumer_key = 'anonymous'
            consumer_secret = 'anonymous'

            consumer = oauth.Consumer(consumer_key, consumer_secret)

            token = oauth.Token(oauth_token, authr.request_secret)
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)

            if "localhost" not in host:

                resp, content = client.request(access_token_url, "POST")

                if resp['status'] == '200':

                    access_token = dict(cgi.parse_qsl(content))

                    profile = Profile(owner=user,
                                      token=access_token['oauth_token'],
                                      secret=access_token['oauth_token_secret'])
                    profile.put()

        self.redirect("/documentation/credentials")


class ProfileHandler(BaseHandler):

    @authorized.force_ssl()
    def get(self):

        consumer_key = 'anonymous'
        consumer_secret = 'anonymous'

        td = default_template_data()
        td["logged_in"] = False
        td["credentials_selected"] = True
        td["consumer_key"] = consumer_key

        user = users.get_current_user()

        if user:

            td["logged_in"] = users.is_current_user_admin()
            profile = Profile.all().filter('owner = ', user).get()

            if profile:

                td["user_is_authorized"] = True
                td["profile"] = profile

            else:

                host = self.request.headers.get('host', 'nohost')

                callback = 'http://%s/documentation/verify' % host

                request_token_url = 'https://%s/_ah/OAuthGetRequestToken?oauth_callback=%s' % (host, callback)
                authorize_url = 'https://%s/_ah/OAuthAuthorizeToken' % host

                consumer = oauth.Consumer(consumer_key, consumer_secret)
                client = oauth.Client(consumer)

                # Step 1: Get a request token. This is a temporary token that is used for
                # having the user authorize an access token and to sign the request to obtain
                # said access token.

                td["user_is_authorized"] = False

                if "localhost" not in host:

                    resp, content = client.request(request_token_url, "GET")

                    if resp['status'] == '200':

                        request_token = dict(cgi.parse_qsl(content))

                        authr = AuthRequest.all().filter("owner =", user).get()

                        if authr:
                            authr.request_secret = request_token['oauth_token_secret']
                        else:
                            authr = AuthRequest(owner=user,
                                    request_secret=request_token['oauth_token_secret'])

                        authr.put()

                        td["oauth_url"] = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

        self.render(td, 'credentials.html')


