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
import string
import re
import os
import cgi
import urllib
import logging
import jsonpickle

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db

from handlers import restful
from utils import authorized
from utils import sanitizer
from utils import slugify
from models import Status, Event, Service
import config

class NotFoundHandler(restful.Controller):
    def get(self):
        logging.debug("NotFoundAPIHandler#get")
        self.error(404, "Can't find resouce")

class ServicesListHandler(restful.Controller):
    def get(self):
        logging.debug("ServicesListHandler#get")
        
        query = Service.all()
        data = []
        
        for s in query:
            data.append(s.rest())
            
        data = { "data": data }
        
        self.json(data)

    @authorized.api("admin")
    def post(self):
        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        
        if name and description:
            slug = slugify.slugify(name)
            existing_s = Service.get_by_slug(slug)
            
            # Update existing resource
            if existing_s:
                existing_s.description = description
                existing_s.put()
                self.json(existing_s.rest())
            # Create new service
            else:
                s = Service(name=name, slug=slug, description=description)
                s.put()
                self.json(s.rest())
        else:
            self.error(400, "Bad Data")
            
class ServiceInstanceHandler(restful.Controller):
    def get(self, service):
        logging.debug("ServiceInstanceHandler#get")
        
        service = Service.get_by_slug(service)
        
        if (service):
            self.json(service.rest())
        else:
            self.error(404, "Service %s does not exist" % service_slug)

    @authorized.api("admin")
    def post(self, service_slug):
        logging.debug("ServiceInstanceHandler#post")
        description = self.request.get('description')
        
        service = Service.get_by_slug(service_slug)
        
        if service:
            service.description = description
            service.put()
            self.json(service.rest())   
        else:
            self.error(404, "Service %s does not exist" % service_slug)
            
    @authorized.api("admin")
    def delete(self, service_slug):
        logging.debug("ServiceInstanceHandler#delete slug=%s" % service_slug)

        service = Service.get_by_slug(service_slug)

        if service:
            service.delete()
            self.json(service.rest())
        else:
            self.error(404, "Service %s not found" % service_slug)

class EventsListHandler(restful.Controller):
    def get(self, service_slug):
        logging.debug("StatusesListHandler#get")
        
        service = Service.get_by_slug(service_slug)
        
        if service:
            query = Event.all()
            query.filter('service =', service).order('-start')
        
            if query:
                data = []
        
                for s in query:
                    data.append(s.rest())
                    
                data = { "data": data }
        
                self.json(data) 
            else:
                self.error(404, "No events for Service %s" % service_slug)
        else:
            self.error(404, "Service %s not found" % service_slug)

    @authorized.api("admin")
    def post(self, service_slug):
        logging.debug("EventsListHandler#post")
        
        status_name = self.request.get("status", default_value=None)
        message = self.request.get("message", default_value=None)
        
        if status_name and message:
            service = Service.get_by_slug(service_slug)
            if service:
                status = Status.get_by_name(status_name)
                if status:
                    e = Event(status=status, service=service, message=message)
                    e.put()
                    self.json(e.rest())
                else:
                    self.error(404, "Status %s not found" % status_name)
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(400, "Event status is required")
        
class CurrentEventHandler(restful.Controller):
    def get(self, service_slug):
        logging.debug("CurrentStatusHandler#get")

        service = Service.get_by_slug(service_slug)
        
        if (service):
            event = Event.current(service)
        
            if (event):
                self.json(event.rest()) 
            else:
                self.error(404, "No current event for Service %s" % service_slug)
        else:
            self.error(404, "Service %s not found" % service_slug)
    
class EventInstanceHandler(restful.Controller):
    def get(self, service_slug, sid):
        logging.debug("EventInstanceHandler#get sid=%s" % sid)
        
        service = Service.get_by_slug(service_slug)
        
        if (service):
            event = Event.get(db.Key(sid))
            if (event and service.key() == event.service.key()):
                self.json(event.rest()) 
            else:
                self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
        else:
            self.error(404, "Service %s not found" % service_slug)
            
    @authorized.api("admin")
    def delete(self, service_slug, sid):
        logging.debug("EventInstanceHandler#delete sid=%s" % sid)
        
        service = Service.get_by_slug(service_slug)
        
        if (service):
            event = Event.get(db.Key(sid))
            if (event and service.key() == event.service.key()):
                event.delete()
                self.success("Deleted Event %s from service %s" % (sid, service_slug))
            else:
                self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
        else:
            self.error(404, "Service %s not found" % service_slug)

class StatusesListHandler(restful.Controller):
    def get(self):
        logging.debug("StatusesListHandler#get")
        
        query = Status.all()
        
        if (query):
            data = []
        
            for s in query:
                data.append(s.rest())
        
            self.json(data) 
        else:
            self.error(404, "No statuses")

    @authorized.api("admin")
    def post(self):
        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        severity = self.request.get('severity', default_value=None)
        image = self.request.get('image', default_value=None)
        
        if name and description and severity and image:
            status = Status.get_by_name(name)
            severity = int(severity)
            
            # Update existing resource
            if status:
                status.description = description
                status.severity = severity
                status.image = image
                status.put()
                self.json(status.rest())
            # Create new service
            else:
                status = Status(name=name, description=description, 
                    severity=severity, image=image)
                status.put()
                self.json(status.rest())
        else:
            self.error(400, "Bad Data")

class StatusInstanceHandler(restful.Controller):
    def get(self, status_name):
        logging.debug("CurrentStatusHandler#get")

        
        status = Status.get_by_name(status_name)
        
        if (status):
            self.json(status.rest()) 
        else:
            self.error(404, "No status %s for Service %s" % status_name)


    @authorized.api("admin")
    def post(self, status_name):
        description = self.request.get('description', default_value=None)
        
        if description:
            status = Status.get_by_name(status_name)
            if status:
                status.description = description
                status.put()
                self.json(status.rest())
            else:
                self.error(404, "Status %s not found" % status_name)
        else:
            self.error(400, "Description is required" % service_slug)

