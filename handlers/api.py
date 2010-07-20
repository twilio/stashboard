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

import datetime
from datetime import timedelta
from datetime import date
from datetime import datetime
from datetime import time
from dateutil.parser import parse
import string
import re
import os
import cgi
import urllib
import logging
import jsonpickle
import status_images

from wsgiref.handlers import format_date_time
from time import mktime

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db

from handlers import restful
from utils import authorized
from utils import slugify
from models import Status, Event, Service, Level
import config

def aware_to_naive(d):
    """Convert an aware date to an naive date, in UTC"""
    offset = d.utcoffset()
    if offset:
        d = d.replace(tzinfo=None)
        d = d - offset
    return d

class NotFoundHandler(restful.Controller):
    def get(self):
        logging.debug("NotFoundAPIHandler#get")
        self.error(404, "Can't find resouce")

class ServicesListHandler(restful.Controller):
    def get(self, version):
        logging.debug("ServicesListHandler#get")
        if (self.valid_version(version)):
            
            query = Service.all().order('name')
            data = []


            for s in query:
                data.append(s.rest(self.base_url(version)))

            data = { "services": data }

            self.json(data)
            
        else:
            self.error(404, "API Version %s not supported" % version)
            
    @authorized.api("admin")
    def post(self, version):
        logging.debug("ServicesListHandler#post")

        if (self.valid_version(version)):
            
            name = self.request.get('name', default_value=None)
            description = self.request.get('description', default_value=None)
            
            if name and description:
                slug = slugify.slugify(name)
                existing_s = Service.get_by_slug(slug)

                # Update existing resource
                if existing_s:
                    existing_s.description = description
                    existing_s.put()
                    self.json(existing_s.rest(self.base_url(version)))
                # Create new service
                else:
                    s = Service(name=name, slug=slug, description=description)
                    s.put()
                    self.json(s.rest(self.base_url(version)))
            else:
                self.error(400, "Bad Data: Name: %s, Description: %s" % (name, description))
        else:
            self.error(404, "API Version %s not supported" % version)

            
class ServiceInstanceHandler(restful.Controller):
    def get(self, version, service_slug):
        logging.debug("ServiceInstanceHandler#get")
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if (service):
                self.json(service.rest(self.base_url(version)))
            else:
                self.error(404, "Service %s does not exist" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

    @authorized.api("admin")
    def post(self, version, service_slug):
        logging.debug("ServiceInstanceHandler#post")
        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)
            if service:
                if description:
                    service.description = description
                
                if name:
                    service.name = name
                
                if name or description:
                    service.put()
                    
                self.json(service.rest(self.base_url(version)))   
            else:
                self.error(404, "Service %s does not exist" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        
    @authorized.api("admin")
    def delete(self, version, service_slug):
        logging.debug("ServiceInstanceHandler#delete slug=%s" % service_slug)
        
        if (self.valid_version(version)):
            
            service = Service.get_by_slug(service_slug)
            
            if service:
                query = Event.all()
                query.filter('service =', service)
                if query:
                    for e in query:
                        e.delete()

                service.delete()
                self.json(service.rest(self.base_url(version)))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)





class EventsListHandler(restful.Controller):
    def get(self, version, service_slug):
        logging.debug("StatusesListHandler#get")
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if service:
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
                        _end  = aware_to_naive(parse(end))
                        query.filter("start <=", _end)
                    except:
                        self.error(400, "Invalid Date: %s" % end)
                        return
                        
                query.order('-start')
                        
                if query:
                    data = []

                    for s in query:
                        data.append(s.rest(self.base_url(version)))

                    data = { "events": data }

                    self.json(data) 
                else:
                    self.error(404, "No events for Service %s" % service_slug)
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

    @authorized.api("admin")
    def post(self, version, service_slug):
        logging.debug("EventsListHandler#post")
        
        if (self.valid_version(version)):
            status_slug = self.request.get("status", default_value=None)
            message = self.request.get("message", default_value=None)
            informational = self.request.get("informational", default_value=None)
            
            if message:
                service = Service.get_by_slug(service_slug)
                if service:
                    
                    if not status_slug:
                        event = service.current_event()
                        if event:
                            status = event.status
                        else:
                            status = Status.default()
                    else:
                        status = Status.get_by_slug(status_slug)

                    if status:
                        e = Event(status=status, service=service,
                                message=message)

                        e.informational = informational and informational == "true"

                        e.put()
                        self.json(e.rest(self.base_url(version)))
                    else:
                        self.error(404, "Status %s not found" % status_slug)
                else:
                    self.error(404, "Service %s not found" % service_slug)
            else:
                self.error(400, "Event message is required")
        else:
            self.error(404, "API Version %s not supported" % version)
        

        
class CurrentEventHandler(restful.Controller):
    def get(self, version, service_slug):
        logging.debug("CurrentStatusHandler#get")
        
        if (self.valid_version(version)):
        
            service = Service.get_by_slug(service_slug)
        
            if (service):
                event = service.current_event()
        
                if (event):
                    self.json(event.rest(self.base_url(version))) 
                else:
                    self.error(404, "No current event for Service %s" % service_slug)
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "Version %s not supported" % version)
    
class EventInstanceHandler(restful.Controller):
    def get(self, version, service_slug, sid):
        logging.debug("EventInstanceHandler#get sid=%s" % sid)
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if (service):
                event = Event.get(db.Key(sid))
                if (event and service.key() == event.service.key()):
                    self.json(event.rest(self.base_url(version))) 
                else:
                    self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

    @authorized.api("admin")
    def delete(self, version, service_slug, sid):
        logging.debug("EventInstanceHandler#delete sid=%s" % sid)
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if (service):
                event = Event.get(db.Key(sid))
                if (event and service.key() == event.service.key()):
                    event.delete()
                    self.success(event.rest(self.base_url(version)))
                else:
                    self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        


class StatusesListHandler(restful.Controller):
    def get(self, version):
        logging.debug("StatusesListHandler#get")
        
        if (self.valid_version(version)):
            query = Status.all().order('severity')

            if (query):
                data = []

                for s in query:
                    data.append(s.rest(self.base_url(version)))

                self.json({"statuses": data}) 
            else:
                self.error(404, "No statuses")
        else:
            self.error(404, "API Version %s not supported" % version)
        

    @authorized.api("admin")
    def post(self, version):
        
        if (self.valid_version(version)):
            name = self.request.get('name', default_value=None)
            description = self.request.get('description', default_value=None)
            image = self.request.get('image', default_value=None)
            level = self.request.get('level', default_value=None)
            severity = Level.get_severity(level)

            if name and description and severity and image:
                slug = slugify.slugify(name)
                status = Status.get_by_slug(slug)

                # Update existing resource
                if status:
                    status.description = description
                    status.severity = severity
                    status.image = image
                    status.name = name
                    status.put()
                    self.json(status.rest(self.base_url(version)))
                # Create new service
                else:
                    status = Status(name=name, slug=slug, description=description, 
                        severity=severity, image=image)
                    status.put()
                    self.json(status.rest(self.base_url(version)))
            else:
                self.error(400, "Bad Data")
        else:
            self.error(404, "API Version %s not supported" % version)
        


class StatusInstanceHandler(restful.Controller):
    def get(self, version, status_slug):
        logging.debug("CurrentStatusHandler#get")
        
        if (self.valid_version(version)):
            status = Status.get_by_slug(status_slug)

            if (status):
                self.json(status.rest(self.base_url(version))) 
            else:
                self.error(404, "No status %s for Service %s" % status_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

    @authorized.api("admin")
    def post(self, version, status_slug):

        
        if (self.valid_version(version)):
            status = Status.get_by_slug(status_slug)
            if status:
                name = self.request.get('name', default_value=None)
                image = self.request.get('image', default_value=None)
                description = self.request.get('description', default_value=None)
                level = self.request.get('level', default_value=None)
                severity = Level.get_severity(level)
                
                if description:
                    status.description = description
                    
                if image:
                    status.image = image
                    
                if name:
                    status.name = name
                    
                if severity:
                    status.severity = severity
                
                if description or name or image or severity:
                    status.put()
                    
                self.json(status.rest(self.base_url(version)))
            else:
                self.error(404, "Status %s not found" % status_slug)
        else:
            self.error(404, "API Version %s not supported" % version)

    @authorized.api("admin")
    def delete(self, version, status_slug):
        logging.debug("StatusInstanceHandler#delete slug=%s" % status_slug)
        
        if (self.valid_version(version)):

            status = Status.get_by_slug(status_slug)            

            if status:
                # We may want to think more about this
                events = Event.all().filter('status =', status).fetch(1000)
                for event in events:
                    event.delete()
                status.delete()
                self.json(status.rest(self.base_url(version)))
            else:
                self.error(404, "Status %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)

            

            
class ImagesListHandler(restful.Controller):
    def get(self, version):
        logging.debug("ImagesListHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
        
            query = status_images.images
        
            for img in query:
                img["url"] = "http://" + host + img["url"]

            if (query):
                self.json({"images": query}) 
            else:
                self.error(404, "No images")
        else:
            self.error(404, "API Version %s not supported" % version)
            
class LevelsListHandler(restful.Controller):
    def get(self, version):
        logging.debug("LevelsListHandler#get")
        
        if (self.valid_version(version)):
            
            self.json({"levels": Level.all()})
            
        else:
            
            self.error(404, "API Version %s not supported" % version)

