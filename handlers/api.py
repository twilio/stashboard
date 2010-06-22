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
import status_images

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
    def get(self, version):
        logging.debug("ServicesListHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            
            query = Service.all().order('name')
            data = []

            for s in query:
                data.append(s.rest(self.base_url(host, version)))

            data = { "services": data }

            self.json(data)
            
        else:
            self.error(404, "API Version %s not supported" % version)


    @authorized.api("admin")
    def post(self, version):
        logging.debug("ServicesListHandler#post")
        host = self.request.headers.get('host', 'nohost')
        
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
                    self.json(existing_s.rest(self.base_url(host, version)))
                # Create new service
                else:
                    s = Service(name=name, slug=slug, description=description)
                    s.put()
                    self.json(s.rest(self.base_url(host, version)))
            else:
                self.error(400, "Bad Data")
        else:
            self.error(404, "API Version %s not supported" % version)

            
class ServiceInstanceHandler(restful.Controller):
    def get(self, version, service):
        logging.debug("ServiceInstanceHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service)

            if (service):
                self.json(service.rest(self.base_url(host, version)))
            else:
                self.error(404, "Service %s does not exist" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        


    @authorized.api("admin")
    def post(self, version, service_slug):
        logging.debug("ServiceInstanceHandler#post")
        host = self.request.headers.get('host', 'nohost')
        description = self.request.get('description')
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if service:
                service.description = description
                service.put()
                self.json(service.rest(self.base_url(host, version)))   
            else:
                self.error(404, "Service %s does not exist" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

            
    @authorized.api("admin")
    def delete(self, version, service_slug):
        logging.debug("ServiceInstanceHandler#delete slug=%s" % service_slug)
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            
            service = Service.get_by_slug(service_slug)
            
            if service:
                service.delete()
                self.json(service.rest(self.base_url(host, version)))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)





class EventsListHandler(restful.Controller):
    def get(self, version, service_slug):
        logging.debug("StatusesListHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if service:
                after = self.request.get('after', default_value=None)
                before = self.request.get('before', default_value=None)
                
                query = Event.all()
                query.filter('service =', service).order('-start')
                
                if after:
                    try:
                        aft = datetime.datetime.strptime(after, "%Y-%m-%d")
                        query.filter("start > ", aft)
                    except:
                        self.error(400, "Invalid Date: %s" % after)
                        pass
                
                if before:
                    try:
                        bef = datetime.datetime.strptime(before, "%Y-%m-%d")
                        query.filter("start <", bef)
                    except:
                        self.error(400, "Invalid Date: %s" % before)
                        return
                        
                if query:
                    data = []

                    for s in query:
                        data.append(s.rest(self.base_url(host, version)))

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
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            status_slug = self.request.get("status", default_value=None)
            message = self.request.get("message", default_value=None)

            if status_slug and message:
                service = Service.get_by_slug(service_slug)
                if service:
                    status = Status.get_by_slug(status_slug)
                    if status:
                        e = Event(status=status, service=service, message=message)
                        e.put()
                        self.json(e.rest(self.base_url(host, version)))
                    else:
                        self.error(404, "Status %s not found" % status_slug)
                else:
                    self.error(404, "Service %s not found" % service_slug)
            else:
                self.error(400, "Event status is required")
        else:
            self.error(404, "API Version %s not supported" % version)
        

        
class CurrentEventHandler(restful.Controller):
    def get(self, version, service_slug):
        logging.debug("CurrentStatusHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
        
            service = Service.get_by_slug(service_slug)
        
            if (service):
                event = Event.current(service)
        
                if (event):
                    self.json(event.rest(self.base_url(host, version))) 
                else:
                    self.error(404, "No current event for Service %s" % service_slug)
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "Version %s not supported" % version)
    
class EventInstanceHandler(restful.Controller):
    def get(self, version, service_slug, sid):
        logging.debug("EventInstanceHandler#get sid=%s" % sid)
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if (service):
                event = Event.get(db.Key(sid))
                if (event and service.key() == event.service.key()):
                    self.json(event.rest(self.base_url(host, version))) 
                else:
                    self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        

            
    @authorized.api("admin")
    def delete(self, version, service_slug, sid):
        logging.debug("EventInstanceHandler#delete sid=%s" % sid)
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            service = Service.get_by_slug(service_slug)

            if (service):
                event = Event.get(db.Key(sid))
                if (event and service.key() == event.service.key()):
                    event.delete()
                    self.success(event.rest(self.base_url(host, version)))
                else:
                    self.error(404, "No event for Service %s with sid = %s" % (service_slug,sid))
            else:
                self.error(404, "Service %s not found" % service_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        


class StatusesListHandler(restful.Controller):
    def get(self, version):
        logging.debug("StatusesListHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            query = Status.all()

            if (query):
                data = []

                for s in query:
                    data.append(s.rest(self.base_url(host, version)))

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
            severity = int(self.request.get('severity', default_value=None))
            image = self.request.get('image', default_value=None)
            host = self.request.headers.get('host', 'nohost')

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
                    self.json(status.rest(self.base_url(host, version)))
                # Create new service
                else:
                    status = Status(name=name, slug=slug, description=description, 
                        severity=severity, image=image)
                    status.put()
                    self.json(status.rest(self.base_url(host, version)))
            else:
                self.error(400, "Bad Data")
        else:
            self.error(404, "API Version %s not supported" % version)
        


class StatusInstanceHandler(restful.Controller):
    def get(self, version, status_slug):
        logging.debug("CurrentStatusHandler#get")
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            status = Status.get_by_slug(status_slug)

            if (status):
                self.json(status.rest(self.base_url(host, version))) 
            else:
                self.error(404, "No status %s for Service %s" % status_slug)
        else:
            self.error(404, "API Version %s not supported" % version)
        



    @authorized.api("admin")
    def post(self, version, status_slug):
        description = self.request.get('description', default_value=None)
        host = self.request.headers.get('host', 'nohost')
        
        if (self.valid_version(version)):
            if description:
                status = Status.get_by_slug(status_slug)
                if status:
                    status.description = description
                    status.put()
                    self.json(status.rest(self.base_url(host, version)))
                else:
                    self.error(404, "Status %s not found" % status_slug)
            else:
                self.error(400, "Description is required" % service_slug)
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

