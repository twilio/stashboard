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
import logging
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
from time import mktime
from models import List, Status, Service, Event, Profile
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
            else:
                all_pages = memcache.get("__all_pages__")
                if all_pages is not None:
                    all_pages[key] = 1
                else:
                    all_pages = {key: 1}
                if not memcache.set("__all_pages__", all_pages):
                    logging.error("Memcache set failed on __all_pages__")
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

        for service in Service.all().order("list").order("name").fetch(100):
            event = service.current_event()
            if event is not None:
                status = event.status
            else:
                status = default_status

            today = date.today() + timedelta(days=1)
            current, = service.history(1, default_status, start=today)
            has_issues = (current["information"] and
                          status.key() == default_status.key())

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
        td.update(self.retrieve("frontpage"))
        #td.update(self.data())
        self.render(td, 'index.html')

class ListHandler(BaseHandler):

    list = None

    def data(self):
        services = []
        default_status = Status.get_default()

        for service in Service.all().filter("list =", self.list).order("name").fetch(100):
            event = service.current_event()
            if event is not None:
                status = event.status
            else:
                status = default_status

            today = date.today() + timedelta(days=1)
            current, = service.history(1, default_status, start=today)
            has_issues = (current["information"] and
                          status.key() == default_status.key())

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

    def get(self, list_slug):
        self.list = List.get_by_slug(list_slug)

        if self.list is None:
            self.not_found()
            return

        td = default_template_data()
        td.update(self.retrieve("list"+list_slug))
        #td.update(self.data())
        self.render(td, 'index.html')

class ListListHandler(BaseHandler):

    lists = []
    statuses = []

    def data(self):
        services = []
        default_status = Status.get_default()

        lists = []
        for list in self.lists:
            l = List.get_by_slug(list)
            if l is not None:
                lists.append(l)

        for service in Service.all().filter("list IN", lists).order("name").fetch(100):
            event = service.current_event()
            if event is not None:
                status = event.status
            else:
                status = default_status

            if len(self.statuses) and not status.slug in self.statuses: continue

            today = date.today() + timedelta(days=1)
            current, = service.history(1, default_status, start=today)
            has_issues = (current["information"] and
                          status.key() == default_status.key())

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
        self.lists = self.request.get_all('filter')
        self.lists.sort()

        self.statuses = self.request.get_all('status')
        self.statuses.sort()

        td = default_template_data()
        td.update(self.retrieve("list"+"_".join(self.statuses)+"_".join(self.lists)))
        #td.update(self.data())
        self.render(td, 'index.html')

class ListSummaryHandler(BaseHandler):

    def data(self):
        lists = {}
        default_status = Status.get_default()

        for service in Service.all().order("list").fetch(100):
            event = service.current_event()
            if event is not None:
                status = event.status
            else:
                status = default_status

            if service.list and not lists.has_key(service.list.slug) or \
                lists[service.list.slug]["status"].severity < status.severity:
                lists[service.list.slug] = {"list": service.list, "status": status}

        return { "lists": lists.items() }

    def get(self):
        td = default_template_data()
        td.update(self.retrieve("summary"))
        #td.update(self.data())
        self.render(td, 'summary.html')


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

class CredentialsRedirectHandler(BaseHandler):

    def get(self):
        self.redirect("/admin/credentials")
