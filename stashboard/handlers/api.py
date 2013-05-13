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

"""A simple RESTful status framework on Google App Engine

This app's API should be reasonably clean and easily targeted by other
clients, like a Flex app or a desktop program.
"""

__author__ = 'Kyle Conroy'

import string
import re
import os
import cgi
import logging

from datetime import timedelta
from datetime import date
from datetime import datetime
from datetime import time
from dateutil.parser import parse
from google.appengine.api import memcache
from google.appengine.api import datastore_errors
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from handlers import restful
from time import mktime
from utils import authorized
from utils import slugify
from models import List, Status, Event, Service, Image
from wsgiref.handlers import format_date_time


def invalidate_cache():
    all_pages = memcache.get("__all_pages__")
    if all_pages is not None:
        for page,d in all_pages.items():
            if not memcache.delete(page):
                logging.error("Memcache delete failed on %s", page)
    if not memcache.delete("__all_pages__"):
        logging.error("Memcache delete failed on __all_pages__")
    taskqueue.add(url='/', method="GET")


def aware_to_naive(d):
    """Convert an aware date to an naive date, in UTC"""
    offset = d.utcoffset()
    if offset:
        d = d.replace(tzinfo=None)
        d = d - offset
    return d


class NotFoundHandler(restful.Controller):
    def get(self):
        self.error(404, "Can't find resource")

class ListsListHandler(restful.Controller):

    def get(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        query = List.all().order('name')
        data = [s.rest(self.base_url(version)) for s in query]
        data = {"lists": data}
        self.json(data)

    @authorized.api("admin")
    def post(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)

        if not name or not description:
            self.error(400, "Bad Data: Name: %s, Description: %s" \
                           % (name, description))
            return

        slug = slugify.slugify(name)
        existing_s = List.get_by_slug(slug)

        if existing_s:
            self.error(404, "A list with this name already exists")
            return

        l = List(name=name, slug=slug, description=description)
        l.put()

        invalidate_cache()

        self.response.set_status(201)
        self.json(l.rest(self.base_url(version)))


class ListInstanceHandler(restful.Controller):

    def get(self, version, list_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        list = List.get_by_slug(list_slug)

        if not list:
            self.error(404, "List %s does not exist" % list_slug)
            return

        self.json(list.rest(self.base_url(version)))

    @authorized.api("admin")
    def post(self, version, list_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        list = List.get_by_slug(list_slug)

        if not list:
            self.error(404, "Service %s does not exist" % list_slug)
            return

        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)

        if description:
            list.description = description

        if name:
            list.name = name

        if name or description:
            invalidate_cache()
            list.put()

        self.json(list.rest(self.base_url(version)))

    @authorized.api("admin")
    def delete(self, version, list_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        list = List.get_by_slug(list_slug)

        if not list:
            self.error(404, "List %s not found" % list_slug)
            return

        query = Service.all()
        query.filter('list =', list)
        if query:
            for s in query:
                s.list = None
                s.put()

        invalidate_cache()
        list.delete()
        self.json(list.rest(self.base_url(version)))


class ServicesListHandler(restful.Controller):

    def get(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        query = Service.all().order('name')
        data = [s.rest(self.base_url(version)) for s in query]
        data = {"services": data}
        self.json(data)

    @authorized.api("admin")
    def post(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        slist = self.request.get('list', default_value=None)
        l = None

        if slist:
            l = List.all().filter("slug =", slist).get()

        if not name:
            self.error(400, "Bad name: %s" % name)
            return

        if not description:
            self.error(400, "Bad description: %s" % description)
            return

        if slist and not l:
            self.error(400, "Bad list slug: %s" % slist)
            return

        slug = slugify.slugify(name)
        existing_s = Service.get_by_slug(slug)

        if existing_s:
            self.error(404, "A sevice with this name already exists")
            return

        s = Service(name=name, slug=slug, description=description, list=l)
        s.put()

        invalidate_cache()

        self.response.set_status(201)
        self.json(s.rest(self.base_url(version)))


class ServiceInstanceHandler(restful.Controller):

    def get(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s does not exist" % service_slug)
            return

        self.json(service.rest(self.base_url(version)))

    @authorized.api("admin")
    def post(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)
        if not service:
            self.error(404, "Service %s does not exist" % service_slug)
            return

        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        list = self.request.get('list', default_value=None)

        if description:
            service.description = description

        if name:
            service.name = name

        if list:
            l = List.all().filter("slug = ", list).get()

            if l is None:
                self.error(400, "Can't find list with slug %s" % list)
                return

            service.list = l

        if "" == list:
            service.list = None
            list = "removed"


        if name or description or list:
            invalidate_cache()
            service.put()

        self.json(service.rest(self.base_url(version)))

    @authorized.api("admin")
    def delete(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return

        query = Event.all()
        query.filter('service =', service)
        if query:
            for e in query:
                e.delete()

        invalidate_cache()
        service.delete()
        self.json(service.rest(self.base_url(version)))


class EventsListHandler(restful.Controller):
    def get(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return

        start = self.request.get('start', default_value=None)
        end = self.request.get('end', default_value=None)

        query = Event.all()
        query.filter('service =', service)

        if start:
            try:
                _start = aware_to_naive(parse(start))
                query.filter("start >= ", _start)
            except:
                self.error(400, "Invalid Date: %s" % start)
                return

        if end:
            try:
                _end = aware_to_naive(parse(end))
                query.filter("start <=", _end)
            except:
                self.error(400, "Invalid Date: %s" % end)
                return

        query.order('-start')

        data = [s.rest(self.base_url(version)) for s in query]
        self.json({"events": data})

    @authorized.api("admin")
    def post(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        status_slug = self.request.get("status", default_value=None)
        message = self.request.get("message", default_value=None)
        informational = self.request.get("informational", default_value=None)

        if not message:
            self.error(400, "Event message is required")
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return

        if not status_slug:
            event = service.current_event()
            if event:
                status = event.status
            else:
                status = Status.get_default()
        else:
            status = Status.get_by_slug(status_slug)

        if not status:
            self.error(404, "Status %s not found" % status_slug)
            return

        e = Event(status=status, service=service, message=message)
        e.informational = informational and informational == "true"
        e.put()

        # Queue up a task that calls the Twitter API to make a tweet.
        if self.request.get('tweet'):
            logging.info('Attempting to post a tweet for the latest event via async GAE task queue.')
            taskqueue.add(url='/admin/tweet', params={'service_name': service.name, 'status_name': status.name, 'message': message})

        invalidate_cache()
        self.json(e.rest(self.base_url(version)))


class CurrentEventHandler(restful.Controller):
    def get(self, version, service_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return

        event = service.current_event()

        if not event:
            self.error(404, "No current event for Service %s" % service_slug)
            return

        self.json(event.rest(self.base_url(version)))


class EventInstanceHandler(restful.Controller):
    def get(self, version, service_slug, sid):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return

        try:
            event = Event.get(db.Key(sid))
        except datastore_errors.BadKeyError:
            self.error(404, "Event %s not found" % sid)
            return

        if not event or service.key() != event.service.key():
            self.error(404, "No event for Service %s with sid = %s" \
                           % (service_slug, sid))
            return

        self.json(event.rest(self.base_url(version)))

    @authorized.api("admin")
    def delete(self, version, service_slug, sid):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        service = Service.get_by_slug(service_slug)

        if not service:
            self.error(404, "Service %s not found" % service_slug)
            return


        try:
            event = Event.get(db.Key(sid))
        except datastore_errors.BadKeyError:
            self.error(404, "Event %s not found" % sid)
            return

        if not event or service.key() != event.service.key():
            self.error(404, "No event for Service %s with sid = %s" \
                           % (service_slug, sid))
            return

        event.delete()
        invalidate_cache()

        # Why not JSON?
        self.success(event.rest(self.base_url(version)))


class StatusesListHandler(restful.Controller):
    def get(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        query = Status.all().order('name')

        data = [s.rest(self.base_url(version)) for s in query]
        self.json({"statuses": data})

    @authorized.api("admin")
    def post(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        image_slug = self.request.get('image', default_value=None)
        default = self.request.get('default', default_value="false")

        if default not in ["true", "false"]:
            self.error(400, "Default must be true or false")
            return

        if not name or not description or not image_slug:
            self.error(400, "Bad Data")
            return

        slug = slugify.slugify(name)
        status = Status.get_by_slug(slug)
        image = Image.get_by_slug(image_slug)

        if status is not None:
            self.error(400, "A Status with the slug %s already exists" % slug)
            return

        if image is None:
            msg = "An Image with the slug %s doesn't exist" % image_slug
            self.error(400, msg)
            return

        # Reset default status
        if default == "true":
            for stat in Status.all().filter("default", True):
                stat.default = False
                stat.put()

        default = default == "true"
        status = Status(name=name, slug=slug, description=description,
                        image=image.path, default=default)
        status.put()
        invalidate_cache()

        self.response.set_status(201)
        self.json(status.rest(self.base_url(version)))


class StatusInstanceHandler(restful.Controller):
    def get(self, version, status_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        status = Status.get_by_slug(status_slug)

        if not status:
            self.error(404, "No status with the slug %s found" % status_slug)
            return

        self.json(status.rest(self.base_url(version)))

    @authorized.api("admin")
    def post(self, version, status_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        status = Status.get_by_slug(status_slug)

        if not status:
            self.error(404, "No status with the slug %s found" % status_slug)
            return

        name = self.request.get('name', default_value=None)
        image_slug = self.request.get('image', default_value=None)
        image = None
        default = self.request.get('default', default_value=None)
        description = self.request.get('description', default_value=None)

        if image_slug is not None:
            image = Image.get_by_slug(image_slug)

            if image is None:
                self.error(400, "An Image with the "
                           "slug %s doesn't exist" % image_slug)
                return

            status.image = image.path

        if description is not None:
            status.description = description

        if default is not None and default in ["false", "true"]:

            # Reset default status
            if default == "true":
                for stat in Status.all().filter("default", True):
                    stat.default = False
                    stat.put()

            status.default = default == "true"

        if name is not None:
            status.name = name

        if description or name or image or default:
            status.put()
            invalidate_cache()

        self.json(status.rest(self.base_url(version)))

    @authorized.api("admin")
    def delete(self, version, status_slug):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        status = Status.get_by_slug(status_slug)

        if not status:
            self.error(404, "Status %s not found" % status_slug)
            return

        # We may want to think more about this
        events = Event.all().filter('status =', status).fetch(1000)
        for event in events:
            event.delete()

        status.delete()
        self.json(status.rest(self.base_url(version)))


class LevelListHandler(restful.Controller):

    def get(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        self.json({"levels": ["NORMAL", "WARNING", "ERROR", "CRITICAL"]})


class ImagesListHandler(restful.Controller):
    def get(self, version):
        if not self.valid_version(version):
            self.error(404, "API Version %s not supported" % version)
            return

        host = self.request.headers.get('host', 'nohost')
        images = []

        for img in Image.all().fetch(1000):
            image = {
                "url": "http://" + host + "/images/" + img.path,
                "icon_set": img.icon_set,
                "name": img.slug,
                }
            images.append(image)

        self.json({"images": images})
