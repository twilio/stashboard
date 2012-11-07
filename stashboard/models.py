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

import os
import datetime
import logging
import urlparse
from datetime import timedelta
from datetime import date
from google.appengine.ext import db
from django.utils import simplejson as json
from time import mktime
from wsgiref.handlers import format_date_time


class InternalEvent(db.Model):
    """An event that happens internally that we need to track. If the event
    exists, that mean the event happened.

    Properties:
    name -- string: The name of this event
    """
    name = db.StringProperty(required=True)


class Image(db.Model):
    """A service to track

    Properties:
    slug -- stirng: URL friendly version of the name
    name -- string: The name of this service
    path -- stirng: The path to the image

    """
    slug = db.StringProperty(required=True)
    icon_set = db.StringProperty(required=True)
    path = db.StringProperty(required=True)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.all().filter('slug = ', slug).get()

    @classmethod
    def load_defaults(cls):
        path = os.path.join(os.path.dirname(__file__), "fixtures/images.json")
        images = json.load(open(path))
        for i in images:
            image = Image(slug=i["name"], icon_set=i["set"], path=i["url"])
            image.put()

    def absolute_url(self):
        return "/images/" + self.path

class List(db.Model):
    """A list to group service

    Properties:
    name        -- string: The name of this list
    description -- string: The description of the list
    slug        -- string: URL friendly version of the name

    """
    @staticmethod
    def get_by_slug(list_slug):
        return List.all().filter('slug = ', list_slug).get()

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)

    def url(self):
        return "/service-lists/%s" % self.slug

    def compare(self, other_status):
        return 0

    def sid(self):
        return unicode(self.key())

    def resource_url(self):
        return "/service-lists/" + self.slug

    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = unicode(self.name)
        m["id"] = unicode(self.slug)
        m["description"] = unicode(self.description)
        m["url"] = base_url + self.resource_url()

        return m



class Service(db.Model):
    """A service to track

    Properties:
    name        -- string: The name of this service
    description -- string: The function of the service
    slug        -- stirng: URL friendly version of the name

    """
    @staticmethod
    def get_by_slug(service_slug):
        return Service.all().filter('slug = ', service_slug).get()

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    list = db.ReferenceProperty(List)

    def current_event(self):
        event = self.events.order('-start').get()
        return event

    def url(self):
        return "/services/%s" % self.slug

    #Specialty function for front page
    def history(self, days, default, start=None):
        """ Return the past n days of activity AFTER the start date.

        Arguments:
        days    -- The number of days of activity to calculate
        default -- The status to use as the base status

        Keyword Arguments
        start   -- The day to look before (defaults to today)

        This funciton is currently only used on the front page
        """
        start = start or date.today()
        ago = start - timedelta(days=days)

        events = self.events.filter('start >=', ago) \
            .filter('start <', start).fetch(100)

        stats = {}

        for i in range(days):
            start = start - timedelta(days=1)
            stats[start.day] = {
                "image": default.image,
                "name": default.name,
                "day": start,
                "information": False,
            }

        for event in events:
            if event.status.slug != default.slug:
                stats[event.start.day]["image"] = "icons/fugue/information.png"
                stats[event.start.day]["information"] = True
                stats[event.start.day]["name"] = "information"

        history = stats.values()
        history.sort()
        history.reverse()

        return history


    def compare(self, other_status):
        return 0

    def sid(self):
        return unicode(self.key())

    def resource_url(self):
        return "/services/" + self.slug

    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = unicode(self.name)
        m["id"] = unicode(self.slug)
        m["description"] = unicode(self.description)
        m["url"] = base_url + self.resource_url()

        event = self.current_event()
        if event:
            m["current-event"] = event.rest(base_url)
        else:
            m["current-event"] = None

        if self.list:
            m["list"] = self.list.rest(base_url)
        else:
            m["list"] = None

        return m

class Status(db.Model):
    """A possible system status

    Properties:
    name        -- string: The friendly name of this status
    slug        -- stirng: The identifier for the status
    description -- string: The state this status represents
    image       -- string: Image in /images/status

    """
    @classmethod
    def get_by_slug(cls, status_slug):
        return cls.all().filter('slug = ', status_slug).get()

    @classmethod
    def get_default(cls):
        return cls.all().filter('default = ', True).get()

    @classmethod
    def load_defaults(cls):
        """
        Install the default statuses. xI am not sure where these should live just yet
        """
        if not cls.get_by_slug("down"):
            d = cls(name="Down", slug="down",
                    image="icons/fugue/cross-circle.png",
                    description="The service is currently down")
            d.put()

        if not cls.get_by_slug("up"):
            u = cls(name="Up", slug="up", default=True,
                    image="icons/fugue/tick-circle.png",
                    description="The service is up")
            u.put()

        if not cls.get_by_slug("warning"):
            w = cls(name="Warning", slug="warning",
                    image="icons/fugue/exclamation.png",
                    description="The service is experiencing intermittent problems")
            w.put()

    name = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    image = db.StringProperty(required=True)
    default = db.BooleanProperty(default=False)

    # Deprecated
    severity = db.IntegerProperty(default=10)

    def image_url(self):
        return "/images/" + unicode(self.image)

    def resource_url(self):
        return "/statuses/" + unicode(self.slug)

    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["default"] = self.default
        m["name"] = unicode(self.name)
        m["id"] = unicode(self.slug)
        m["description"] = unicode(self.description)
        m["url"] = base_url + self.resource_url()
        o = urlparse.urlparse(base_url)
        m["image"] = o.scheme + "://" +  o.netloc + self.image_url()

        # Maintain v1 requirement
        if self.severity == 30:
            m["level"] = "WARNING"
        elif self.severity == 40:
            m["level"] = "ERROR"
        elif self.severity == 50:
            m["level"] = "CRITICAL"
        else:
            m["level"] = "NORMAL"

        return m


class Event(db.Model):

    start = db.DateTimeProperty(required=True, auto_now_add=True)

    # We want this to be required, but it would break all current installs
    # Instead, we handle it in the rest method
    informational = db.BooleanProperty(default=False)
    status = db.ReferenceProperty(Status, required=True)
    message = db.TextProperty(required=True)
    service = db.ReferenceProperty(Service, required=True,
        collection_name="events")

    def duration(self):
        # calculate the difference between start and end
        # should evantually be stored
        pass

    def sid(self):
        return unicode(self.key())

    def resource_url(self):
        return self.service.resource_url() + "/events/" + self.sid()

    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["sid"] = self.sid()

        stamp = mktime(self.start.timetuple())
        m["timestamp"] = format_date_time(stamp)
        m["status"] = self.status.rest(base_url)
        m["message"] = unicode(self.message)
        m["url"] = base_url + self.resource_url()

        if self.informational:
            m["informational"] = self.informational
        else:
            m["informational"] = False

        return m

class Profile(db.Model):
    owner = db.UserProperty(required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)

