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
import xml.etree.ElementTree as et
from utils import authorized
from wsgiref.handlers import format_date_time


def default_template_data():
    data = {
        "title": settings.SITE_NAME,
        "report_url": settings.REPORT_URL,
        "twitter_handle": settings.TWITTER_HANDLE,
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
        all_pages = memcache.get("__all_pages__")
        if all_pages is None:
            all_pages = {}

        item = memcache.get(key) if all_pages.has_key(key) else None

        if item is not None:
            return item
        else:
            item = self.data()
            if not memcache.set(key, item):
                logging.error("Memcache set failed on %s" % key)
            else:
                all_pages[key] = 1
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

        query = Service.all().filter("list =", self.list).order("name")

        for service in query.fetch(100):
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
                lists[service.list.slug]["status"].name < status.name:
                lists[service.list.slug] = {"list": service.list, "status": status}

        return {
            "lists": lists.items(),
            "statuses": Status.all().fetch(100),
            }

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
        td["statuses"] = Status.all().fetch(100)
        td["service"] = service
        td["events"] = events.order("-start").fetch(500)

        self.render(td, 'service.html')

class BaseDocumentationHandler(BaseHandler):

    def get(self):
        td = default_template_data()
        td["selected"] = "overview"
        self.render(td, 'publicdoc/index.html')


class DocumentationHandler(BaseHandler):

    pages = [
        "events",
        "services",
        "service-lists",
        "status-images",
        "statuses",
        "status-images",
    ]

    def get(self, page):
        td = default_template_data()

        if page not in self.pages:
            self.render({}, '404.html')
            return

        td["selected"] = page
        self.render(td, "publicdoc/%s.html" % page)

class CredentialsRedirectHandler(BaseHandler):

    def get(self):
        self.redirect("/admin/credentials")

class RSSHandler(BaseHandler):
    """ Feed of the last settings.RSS_NUM_EVENTS_TO_FETCH events """

    def get(self):
        self.response.headers['Content-Type'] = "application/rss+xml; charset=utf-8"

        host = self.request.headers.get('host', 'nohost')
        base_url = self.request.scheme + "://" + host

        events = []
        query = Event.all().order("-start")

        # Filter query by requested services, if specified in the 'service' URL parameter.
        service_list = []
        for service_arg in self.request.get_all('services'):
            service_list.extend(service_arg.split(','))
        service_list = map(lambda serv_slug: Service.get_by_slug(serv_slug), service_list)
        # filter out any non-existent services
        service_list = filter(lambda service: not service is None, service_list)

        service_string = 'all services'
        if len(service_list) > 0:
            query.filter('service IN', service_list)
            if len(service_list) == 1:
                service_string = 'the %s service' % service_list[0].name
            elif len(service_list) == 2:
                service_string = 'the %s and %s services' % (service_list[0].name, service_list[1].name)
            else:
                service_string = 'the %s, and %s services' % (', '.join([service.name for service in service_list[:-1]]), service_list[-1].name)

        # Create the root 'rss' element
        rss_xml = et.Element('rss')
        rss_xml.set('version', '2.0')

        # Create the channel element and its metadata elements
        channel = et.SubElement(rss_xml, 'channel')
        title = et.SubElement(channel, 'title')
        title.text = '%s Service Events' % settings.SITE_NAME
        description = et.SubElement(channel, 'description')
        description.text = 'This feed shows the last %d events on %s on %s.' % (settings.RSS_NUM_EVENTS_TO_FETCH, service_string, settings.SITE_NAME)
        link = et.SubElement(channel, 'link')
        link.text = base_url

        # Create each of the feed events.
        item_subelements = {
            'title': lambda(event): '[%s - %s] %s' % (event.service.name, event.status.name, unicode(event.message)),
            'description': lambda(event): '%s' % unicode(event.message),
            'link': lambda(event): '%s/services/%s' % (base_url, event.service.slug),
            'category': lambda(event): event.service.name,
            'pubDate': lambda(event): format_date_time(mktime(event.start.timetuple())),
            'guid': lambda(event): '%s/api/v1/services/%s/events/%s' % (base_url, event.service.slug, unicode(event.key()))
        }

        for event in query.fetch(settings.RSS_NUM_EVENTS_TO_FETCH):
            item = et.SubElement(channel, 'item')
            for tag, text_func in item_subelements.iteritems():
                subelement = et.SubElement(item, tag)
                subelement.text = text_func(event)

        self.response.out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.response.out.write(et.tostring(rss_xml))

