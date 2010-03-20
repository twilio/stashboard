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
            data.append(s.obj())
        
        self.json(data)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")
        
class ServiceInstanceHandler(restful.Controller):
    def get(self, service):
        logging.debug("ServiceInstanceHandler#get")
        
        query = Service.all()
        service = query.filter('name = ', service).get()
        
        if (service):
            self.json(service.obj())
        else:
            self.error(404)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")

class EventsListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("StatusesListHandler#get")
        
        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            query = Event.all()
            query.filter('service =', service)
        
            if (query):
                data = []
        
                for s in query:
                    data.append(s.obj())
        
                self.json(data) 
            else:
                self.error(404, "No events for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")

class CurrentEventHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("CurrentStatusHandler#get")

        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            query = Event.all()
            event = query.filter('service =', service).order('-start').get()
        
            if (event):
                self.json(event.obj()) 
            else:
                self.error(404, "No current event for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")
    
class EventInstanceHandler(restful.Controller):
    def get(self, service_name, sid):
        logging.debug("StatusInstanceHandler#get sid=%s" % sid)
        
        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            event = Event.get_by_key_name(sid)
            if (event):
                self.json(event.obj()) 
            else:
                self.error(404, "No event for Service %s with sid = %s" % (service_name,sid))
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")
        
class MessagesListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("MessagesListHandler#get")

        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            query = Message.all()
            query.filter('service =', service)
        
            if (query):
                data = []
        
                for s in query:
                    data.append(s.obj())
        
                self.json(data) 
            else:
                self.error(404, "No messages for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)


    @authorized.role("admin")
    def post(self):
        logging.debug("MessagesListHandler#post")
        self.redirect("/")
        
class MessageInstanceHandler(restful.Controller):
    def get(self, service_name, sid):
        logging.debug("MessageInstanceHandler#get sid=%s" % sid)
        
        
        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            event = Message.get_by_key_name(sid)
            if (event):
                self.json(event.obj()) 
            else:
                self.error(404, "No message for Service %s with sid = %s" % (service_name,sid))
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")
        
class StatusesListHandler(restful.Controller):
    def get(self, service_name):
        logging.debug("StatusesListHandler#get")

        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            query = Status.all()
            query.filter('service =', service)
        
            if (query):
                data = []
        
                for s in query:
                    data.append(s.obj())
        
                self.json(data) 
            else:
                self.error(404, "No statuses for Service %s" % service_name)
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")

class StatusInstanceHandler(restful.Controller):
    def get(self, service_name, status_name):
        logging.debug("CurrentStatusHandler#get")

        query = Service.all()
        service = query.filter('name = ', service_name).get()
        
        if (service):
            query = Message.all()
            status = query.filter('service =', service).filter('name =', status_name).get()
        
            if (status):
                self.json(status.obj()) 
            else:
                self.error(404, "No status %s for Service %s" % (status_name, service_name))
        else:
            self.error(404, "Service %s not found" % service_name)

    @authorized.role("admin")
    def post(self):
        self.redirect("/")
        
                


            
