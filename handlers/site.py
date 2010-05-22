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
from datetime import date, timedelta
import calendar
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

def default_template_data():
    user = users.get_current_user()
    
    if user:
        greeting = users.create_logout_url("/")
    else:
        greeting = users.create_login_url("/")
    
    data = {
        "user": user,
        "user_is_admin": users.is_current_user_admin(),
        "login_link": greeting, 
    }
    
    return data

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
        q.order("name")
        
        td = default_template_data()
        td["services"] = q.fetch(10)
        td["past"] = get_past_days(5)
        td["all_statuses"] = Status.all().order('severity')
        td["default_status"] = Status.lowest_severity()
        td["info_status"] = Status.get_info()
        td["recent_events"] = Event.all().order('-start').fetch(10)

        self.render(td, 'index.html')
        
class ServiceHandler(restful.Controller):
        
    def get(self, service_slug, year=None, month=None, day=None):
        user = users.get_current_user()
        logging.debug("ServiceHandler#get")
        
        service = Service.get_by_slug(service_slug)
        
        if not service:
            self.render({}, '404.html')
            return
            
        show_admin = False
            
        try: 
            if day:
                start_date = date(int(year),int(month),int(day))
                end_date = start_date + timedelta(days=1)
            elif month:
                start_date = date(int(year),int(month),1)
                days = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = start_date + timedelta(days=days)
            elif year:
                start_date = date(int(year),1,1)
                end_date = start_date + timedelta(days=365)
            else:
                start_date = None
                end_date = None
                show_admin = True
        except ValueError:
            self.render({},'404.html')
            return
            
        if start_date and end_date:
            events = service.events.filter("start > ", start_date) \
                .filter("start <", end_date).order("-start")
        else:
            events = service.events.order("-start")
            
        td = default_template_data()
        td["service"] = service
        td["past"] = get_past_days(5)
        td["events"] = events
        td["start_date"] = start_date
        td["end_date"] = end_date
        td["statuses"] = Status.all().order('severity')

        self.render(td, 'service.html')

        