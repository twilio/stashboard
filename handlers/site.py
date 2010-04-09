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

"""A simple RESTful blog/homepage app for Google App Engine

This simple homepage application tries to follow the ideas put forth in the
book 'RESTful Web Services' by Leonard Richardson & Sam Ruby.  It follows a
Resource-Oriented Architecture where each URL specifies a resource that
accepts HTTP verbs.

Rather than create new URLs to handle web-based form submission of resources,
this app embeds form submissions through javascript.  The ability to send
HTTP verbs POST, PUT, and DELETE is delivered through javascript within the
GET responses.  In other words, a rich client gets transmitted with each GET.

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

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db

from handlers import restful
from utils import authorized
from utils import sanitizer
from models import Status, Service, Event
import config

def get_past_days(num):
    date = datetime.date.today()
    dates = []
    
    for i in range(1, num+1):
        dates.append(date - datetime.timedelta(days=i))
    
    return dates
    

class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        logging.debug("NotFoundHandler#get")
        self.error(404)
        #template_data = {}
        #self.render(template_data, '404.html')

class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        logging.debug("UnauthorizedHandler#get")
        self.error(403)
        #template_data = {}
        #self.render(template_data, 'unathorized.html')
        
class SlashHandler(restful.Controller):
    def get(self, url):
        self.redirect("/%s/" % url)

class RootHandler(restful.Controller):
    def get(self):
        user = users.get_current_user()
        logging.debug("RootHandler#get")
        
        q = Service.all()
        q.order("-name")
        
        template_data = {
            "user": users.get_current_user(),
            "user_is_admin": users.is_current_user_admin(),
            "services": q.fetch(10),
            "past": get_past_days(5),
            "default_status": Status.lowest_severity(),
            "recent_events": Event.all().order('-start').fetch(10),
            "twitter": config.SITE["twitter"],
        }
        self.render(template_data, 'index.html')
        
class ServiceHandler(restful.Controller):
    def get(self, service_slug):
        user = users.get_current_user()
        logging.debug("ServiceHandler#get")

        service = Service.get_by_slug(service_slug)
        
        if not service:
            self.render({}, '404.html')
            return
            
        events = service.events.order("-start")

        template_data = {
            "user": users.get_current_user(),
            "user_is_admin": users.is_current_user_admin(),
            "service": service,
            "past": get_past_days(5),
            "events": events,
            "statuses": Status.all().order('severity'),
            "twitter": config.SITE["twitter"],
        }
        self.render(template_data, 'service.html')

    # @authorized.role("admin")
    def post(self, service_slug):
        logging.debug("RootHandler#post")
        
        service = Service.get_by_slug(service_slug)
        
        if not service:
            self.render({},'404.html')
            return
        
        message = cgi.escape(self.request.get('message'))
        key = cgi.escape(self.request.get('severity'))
        
        if len(key) == 0:
            d = {"type":"error", "message": "Please provide a valid message"}
            self.redirect(self.request.path)
        
        status = db.get(db.Key(key))
                
        if status and len(message) > 0:
            e = Event(service=service,status=status,message=message)
            e.put()
            d = {"type":"success", "message": "Created a new event"}
        else:
            d = {"type":"error", "message": "Please provide a valid message"}
            pass
        
        self.redirect(self.request.path)
            
            
        