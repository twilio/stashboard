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
from models import Status, Message, Event, Service
import config

class ServicesListHandler(restful.Controller):
    def get(self):
        logging.debug("ServicesListHandler#get")
        
        query = Service.all()
        data = []
        
        for s in query:
            data.append(s.rest())
        
        self.json(data)

    #@authorized.role("admin")
    def post(self):
        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        
        if name and description:
            existing_s = Service.get_by_name(name)
            
            # Update existing resource
            if existing_s:
                existing_s.description = description
                existing_s.put()
                self.json(s.rest())
            # Create new service
            else:
                s = Service(name=name, description=description)
                s.put()
                self.json(s.rest())
        else:
            self.error(400, "Bad Data")
            
class ServiceInstanceHandler(restful.Controller):
    def get(self, service):
        logging.debug("ServiceInstanceHandler#get")
        
        service = Service.get_by_name(service)
        
        if (service):
            self.json(service.rest())
        else:
            self.error(404, "Service %s does not exist" % service_name)

    #@authorized.role("admin")
    def post(self, service_name):
        logging.debug("ServiceInstanceHandler#post")
        description = self.request.get('description')
        
        service = Service.get_by_name(service_name)
        
        if service:
            service.description = description
            service.put()
            self.json(service.rest())
        else:
            self.error(404, "Service %s does not exist" % service_name)

class EventsListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("StatusesListHandler#get")
        
        service = Service.get_by_name(service_name)
        
        if (service):
            query = Event.all()
            query.filter('service =', service).order('-start')
        
            if (query):
                data = []
        
                for s in query:
                    data.append(s.rest())
        
                self.json(data) 
            else:
                self.error(404, "No events for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)

    #@authorized.role("admin")
    def post(self, service_name):
        logging.debug("EventsListHandler#post")
        
        status_name = self.request.get("status", default_value=None)
        
        if status_name:
            service = Service.get_by_name(service_name)
            if service:
                status = Status.get_by_name(status_name, service)
                if status:
                    e = Event(status=status, service=service)
                    e.put()
                    self.json(e.rest())
                else:
                    self.error(404, "Status %s not found" % status_name)
            else:
                self.error(404, "Service %s not found" % service_name)
        else:
            self.error(400, "Event status is required")
        
class CurrentEventHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("CurrentStatusHandler#get")

        service = Service.get_by_name(service_name)
        
        if (service):
            event = Event.current(service)
        
            if (event):
                self.json(event.rest()) 
            else:
                self.error(404, "No current event for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)
    
class EventInstanceHandler(restful.Controller):
    def get(self, service_name, sid):
        logging.debug("StatusInstanceHandler#get sid=%s" % sid)
        
        service = Service.get_by_name(service_name)
        
        if (service):
            event = Event.get_by_key_name(sid)
            if (event):
                self.json(event.rest()) 
            else:
                self.error(404, "No event for Service %s with sid = %s" % (service_name,sid))
        else:
            self.error(404, "Service %s not found" % service_name)

    #@authorized.role("admin")
    #def post(self):
    #    self.redirect("/")
        
class MessagesListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("MessagesListHandler#get")

        service = Service.get_by_name(service_name)
                
        if not service:
            self.error(404, "Service %s not found" % service_name)
            return
        
        query = Message.all()
        query.filter('service =', service)
        
        if not query:
            self.error(404, "No messages for Service %s" % service_name)
            return
            
        data = []

        for s in query:
            data.append(s.rest())

        self.json(data) 
            


    #@authorized.role("admin")
    def post(self, service_name):
        logging.debug("MessagesListHandler#post")
        
        text = self.request.get('text', default_value=None)
        if not text:
            self.error(400, "No message text")
            return
        
        service = Service.get_by_name(service_name)
        if not service:
            self.error(404, "No messages for Service %s" % service_name)
            return
        
        event = Event.current(service)
        if not event:
            self.error(404, "No current event for Service %s" % service_name)
            return
        
        message = Message(service=service,event=event,text=text)
        message.put()
        self.json(message.rest())
        
class MessageInstanceHandler(restful.Controller):
    def get(self, service_name, sid):
        logging.debug("MessageInstanceHandler#get sid=%s" % sid)
        
        service = Service.get_by_name(service_name)

        if not service: 
            self.error(404, "Service %s not found" % service_name)
            return
        
        event = Message.get_by_sid(sid)
        
        if not event:
            self.error(404, "No message for Service %s with sid = %s" % (service_name,sid))
            return
        
        self.json(event.rest()) 

    #@authorized.role("admin")
    def post(self, service_name, sid):
        logging.debug("MessageInstanceHandler#post sid=%s" % sid)
        
        text = self.request.get('text', default_value=None)
        
        if not text:
            self.error(400, "Parameter 'text' required")
            return
        
        service = Service.get_by_name(service_name)
        
        if not service: 
            self.error(404, "Service %s not found" % service_name)
            return
        
        msg = Message.get_by_sid(sid)
        
        if not msg:
            self.error(404, "No message for Service %s with sid = %s" % (service_name,sid))
            return
            
        msg.text = text
        msg.put()
        self.json(msg.rest())
        
    def delete(self, service_name, sid):
        logging.debug("MessageInstanceHandler#delete sid=%s" % sid)
        
        service = Service.get_by_name(service_name)
        
        if not service: 
            self.error(404, "Service %s not found" % service_name)
            return
        
        msg = Message.get_by_sid(sid)
        
        if not msg:
            self.error(404, "No message for Service %s with sid = %s" % (service_name,sid))
            return
        
        self.json(msg.rest())
        msg.delete()
        
        
class StatusesListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("StatusesListHandler#get")

        service = Service.get_by_name(service_name)
        
        if (service):
            query = Status.all().filter('service =', service)
        
            if (query):
                data = []
        
                for s in query:
                    data.append(s.rest())
        
                self.json(data) 
            else:
                self.error(404, "No statuses for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)

    #@authorized.role("admin")
    def post(self, service_name):
        name = self.request.get('name', default_value=None)
        description = self.request.get('description', default_value=None)
        service = Service.get_by_name(service_name)
        
        if name and description and service:
            status = Status.get_by_name(name, service)
            
            # Update existing resource
            if status:
                status.description = description
                status.put()
                self.json(status.rest())
            # Create new service
            else:
                status = Status(name=name, description=description, service=service)
                status.put()
                self.json(status.rest())
        else:
            self.error(400, "Bad Data")

class StatusInstanceHandler(restful.Controller):
    def get(self, service_name, status_name):
        logging.debug("CurrentStatusHandler#get")

        service = Service.get_by_name(service_name)
        
        if (service):
            status = Status.get_by_name(status_name, service)
        
            if (status):
                self.json(status.rest()) 
            else:
                self.error(404, "No status %s for Service %s" % (status_name, service_name))
        else:
            self.error(404, "Service %s not found" % service_name)

    #@authorized.role("admin")
    def post(self, service_name, status_name):
        service = Service.get_by_name(service_name)
        description = self.request.get('description', default_value=None)
        
        if service and description:
            status = Status.get_by_name(status_name, service)
            if status:
                status.description = description
                status.put()
                self.json(status.rest())
            else:
                self.error(404, "Status %s not found for %s" % 
                    (status_name, service_name))
        else:
            self.error(404, "Service %s not found" % service_name)

