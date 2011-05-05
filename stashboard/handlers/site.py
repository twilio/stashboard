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

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

from datetime import date, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson as json
from models import Status, Service, Event, Profile, AuthRequest
from time import mktime
from utils import authorized
from wsgiref.handlers import format_date_time


def default_template_data():
    data = {
        "title": settings.SITE_NAME,
        "report_url": settings.REPORT_URL,
        }

    user = users.get_current_user()
    if user is not None:
        data["user"] = user
        data["logout_url"] = users.create_logout_url("/")
        data["admin"] = users.is_current_user_admin()

    return data


def get_past_days(num):
    date = datetime.date.today()
    dates = []

    for i in range(1, num + 1):
        dates.append(date - datetime.timedelta(days=i))

    return dates


class BaseHandler(webapp.RequestHandler):

    def render(self, template_values, filename):
        self.response.out.write(render_to_string(filename, template_values))

    def retrieve(self, key):
        """ Helper for loading data from memcache """
        item = memcache.get(key)
        if item is not None:
            return item
        else:
            item = self.data()
            if not memcache.add(key, item):
                logging.error("Memcache set failed on %s" % key)
        return item

    def not_found(self):
        self.error(404)
        self.render(default_template_data(), "404.html")


class NotFoundHandler(BaseHandler):

    def get(self):
        self.error(404)
        self.render(default_template_data(), "404.html")


class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        self.error(403)
        self.render(default_template_data(), "404.html")


class RootHandler(BaseHandler):

    def data(self):
        services = []
        default_status = Status.get_default()

        for service in Service.all().order("name").fetch(100):
            event = service.current_event()
            if event is not None:
                status = event.status
            else:
                status = default_status

            today = date.today() + timedelta(days=1)
            current, = service.history(1, default_status, start=today)
            logging.error(current)
            has_issues = current["information"] and status != default_status

            service_dict = {
                "slug": service.slug,
                "name": service.name,
                "url": service.url(),
                "status": status,
                "has_issues": has_issues,
                "history": service.history(5, default_status),
                }
            services.append(service_dict)

        return {
            "days": get_past_days(5),
            "statuses": Status.all().fetch(100),
            "services": services,
            }

    def get(self):
        td = default_template_data()
        #td.update(self.retrieve("frontpage"))
        td.update(self.data())
        self.render(td, 'index.html')


class ServiceHandler(BaseHandler):

    def get(self, service_slug, year=None, month=None, day=None):
        service = Service.get_by_slug(service_slug)

        if not service:
            self.not_found()
            return

        try:
            if day:
                start_date = date(int(year), int(month), int(day))
                end_date = start_date + timedelta(days=1)
            elif month:
                start_date = date(int(year), int(month), 1)
                days = calendar.monthrange(start_date.year,
                                           start_date.month)[1]
                end_date = start_date + timedelta(days=days)
            elif year:
                start_date = date(int(year), 1, 1)
                end_date = start_date + timedelta(days=365)
            else:
                start_date = None
                end_date = None
        except ValueError:
            self.not_found(404)
            return

        events = service.events

        if start_date and end_date:
            events.filter('start >= ', start_date).filter('start <', end_date)

        td = default_template_data()
        td["service"] = service
        td["events"] = events.order("-start").fetch(500)

        self.render(td, 'service.html')


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
            self.render({}, '404.html')


class VerifyAccessHandler(BaseHandler):

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

                    profile = Profile(
                        owner=user,
                        token=access_token['oauth_token'],
                        secret=access_token['oauth_token_secret']
                        )
                    profile.put()

        self.redirect("/documentation/credentials")


class ProfileHandler(BaseHandler):

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

                request_token_url = ('https://%s/_ah/OAuthGetRequestToken?'
                                     'oauth_callback=%s' % (host, callback))
                authorize_url = 'https://%s/_ah/OAuthAuthorizeToken' % host

                consumer = oauth.Consumer(consumer_key, consumer_secret)
                client = oauth.Client(consumer)

                # Step 1: Get a request token. This is a temporary token
                # that is used for having the user authorize an access token
                # and to sign the request to obtain said access token.

                td["user_is_authorized"] = False

                if "localhost" not in host:

                    resp, content = client.request(request_token_url, "GET")

                    if resp['status'] == '200':

                        request_token = dict(cgi.parse_qsl(content))

                        authr = AuthRequest.all().filter("owner =", user).get()
                        token_secret = request_token['oauth_token_secret']

                        if authr:
                            authr.request_secret = token_secret
                        else:
                            authr = AuthRequest(owner=user,
                                                request_secret=token_secret)

                        authr.put()

                        td["oauth_url"] = "%s?oauth_token=%s" % \
                            (authorize_url, request_token['oauth_token'])

        self.render(td, 'credentials.html')
