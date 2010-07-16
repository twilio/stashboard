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
import urlparse
from wsgiref.handlers import format_date_time
from time import mktime

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

import oauth2 as oauth
from handlers import restful
from utils import authorized
from models import Status, Service, Event, Profile, AuthRequest

import config

def default_template_data():
    user = users.get_current_user()
    
    if user:
        greeting = users.create_logout_url("/")
    else:
        greeting = users.create_login_url("/")
        
    
        
    status_images = [
        [
            "tick-circle",
            "cross-circle",
            "exclamation",
            "wrench",
            "flag",
        ],
        [
            "clock",
            "heart",
            "hard-hat",
            "information",
            "lock",
        ],
        [
            "plug",
            "question",
            "traffic-cone",
            "bug",
            "broom",
        ],
    ]
    
    data = {
        "user": user,
        "user_is_admin": users.is_current_user_admin(),
        "login_link": greeting, 
        'common_statuses': status_images,
    }
    
    return data

def get_past_days(num):
    date = datetime.date.today()
    dates = []
    
    for i in range(1, num+1):
        dates.append(date - datetime.timedelta(days=i))
    
    return dates
    

class NotFoundHandler(restful.Controller):
    def get(self):
        logging.debug("NotFoundHandler#get")
        template_data = {}
        self.render(template_data, '404.html')

class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        logging.debug("UnauthorizedHandler#get")
        self.error(403)
        #template_data = {}
        #self.render(template_data, 'unathorized.html')

class RootHandler(restful.Controller):
    
    @authorized.force_ssl(only_admin=True)
    def get(self):
        user = users.get_current_user()
        logging.debug("RootHandler#get")
        
        q = Service.all()
        q.order("name")
        
        td = default_template_data()
        td["past"] = get_past_days(5)

        self.render(td, 'index.html')
        
class ServiceHandler(restful.Controller):
        
    @authorized.force_ssl(only_admin=True)
    def get(self, service_slug, year=None, month=None, day=None):
        user = users.get_current_user()
        logging.debug("ServiceHandler#get")
        
        service = Service.get_by_slug(service_slug)
        
        if not service:
            self.render({}, "404.html")
            return
        
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
        except ValueError:
            self.render({},'404.html')
            return
            
        td = default_template_data()
        td["service"] = service_slug
        
        if start_date and end_date:
            start_stamp = mktime(start_date.timetuple())
            end_stamp = mktime(end_date.timetuple())
            # Remove GMT from the string so that the date is
            # is parsed in user's time zone
            td["start_date"] = format_date_time(start_stamp)[:-4]
            td["end_date"] = format_date_time(end_stamp)[:-4]
        else:
            td["start_date"] = None
            td["end_date"] = None

        self.render(td, 'service.html')
        
class DebugHandler(restful.Controller):
    
    @authorized.force_ssl()
    def get(self):
        logging.debug("DebugHandler %s", self.request.scheme)
        td = default_template_data()
        self.render(td,'base.html')

        
class BasicRootHandler(restful.Controller):
    def get(self):
        user = users.get_current_user()
        logging.debug("BasicRootHandler#get")

        q = Service.all()
        q.order("name")
        services = q.fetch(100)
        
        p = Status.all()
        p.order("severity")
        
        past = get_past_days(5)
        
        for service in services:
            events = service.events.filter('start <=', past[0]).filter('start >=', past[4]).fetch(100)

        td = default_template_data()
        td["services"] = q.fetch(100)
        td["statuses"] = p.fetch(100)
        td["past"] = past

        self.render(td, 'basic','index.html')

class BasicServiceHandler(restful.Controller):

    def get(self, service_slug, year=None, month=None, day=None):
        user = users.get_current_user()
        logging.debug("BasicServiceHandler#get")

        service = Service.get_by_slug(service_slug)
        

        if not service:
            self.render({}, "404.html")
            return

        events = service.events
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
            events.filter('start > ', start_date).filter('start <', end_date)

        td = default_template_data()
        td["service"] = service
        td["events"] = events.fetch(100)
        td["start_date"] = start_date
        td["end_date"] = end_date

        self.render(td, 'basic','service.html')
        
class DocumentationHandler(restful.Controller):
    
    def get(self, page):
        td = default_template_data()
        
        if page == "overview":
            td["overview_selected"] = True
            self.render(td, 'overview.html')
        elif page == "rest":
            td["rest_selected"] = True
            self.render(td, 'restapi.html')
        elif page == "examples":
            td["example_selected"] = True
            self.render(td, 'examples.html')
        else:
            self.render({},'404.html')
            
        
            
class VerifyAccessHandler(restful.Controller):
    
    @authorized.force_ssl()
    @authorized.role("admin")
    def get(self):
        oauth_token = self.request.get('oauth_token', default_value=None)
        oauth_verifier = self.request.get('oauth_verifier', default_value=None)
        user = users.get_current_user()
        authr = AuthRequest.all().filter('owner = ', user).get()

        if oauth_token and oauth_verifier and user and authr:
            
            host = self.request.headers.get('host', 'nohost')
            access_token_url = 'https://%s/_ah/OAuthGetAccessToken' % host
            
            consumer_key = 'anonymous'
            consumer_secret = 'anonymous'

            consumer = oauth.Consumer(consumer_key, consumer_secret)
            
            token = oauth.Token(oauth_token, authr.request_secret)
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)
            
            if "localhost" not in host:
                
                resp, content = client.request(access_token_url, "POST")
                
                if resp['status'] == '200':
                
                    access_token = dict(cgi.parse_qsl(content))
                
                    profile = Profile(owner=user,
                                      token=access_token['oauth_token'],
                                      secret=access_token['oauth_token_secret'])
                    profile.put()
                
        self.redirect("/documentation/credentials")
        
        


        
            
class ProfileHandler(restful.Controller):
    
    @authorized.force_ssl()
    def get(self):
        
        consumer_key = 'anonymous'
        consumer_secret = 'anonymous'
        
        td = default_template_data()
        td["logged_in"] = False
        td["credentials_selected"] = True
        td["consumer_key"] = consumer_key
        
        user = users.get_current_user()
        
        if user: 
            
            td["logged_in"] = users.is_current_user_admin()
            profile = Profile.all().filter('owner = ', user).get()
                
            if profile:
            
                td["user_is_authorized"] = True
                td["profile"] = profile
            
            else:
            
                host = self.request.headers.get('host', 'nohost')
            
                callback = 'http://%s/documentation/verify' % host

                request_token_url = 'https://%s/_ah/OAuthGetRequestToken?oauth_callback=%s' % (host, callback)
                authorize_url = 'https://%s/_ah/OAuthAuthorizeToken' % host

                consumer = oauth.Consumer(consumer_key, consumer_secret)
                client = oauth.Client(consumer)

                # Step 1: Get a request token. This is a temporary token that is used for 
                # having the user authorize an access token and to sign the request to obtain 
                # said access token.
            
                td["user_is_authorized"] = False
            
                if "localhost" not in host:
                
                    resp, content = client.request(request_token_url, "GET")
            
                    if resp['status'] == '200':

                        request_token = dict(cgi.parse_qsl(content))
                    
                        authr = AuthRequest.all().filter("owner =", user).get()
                    
                        if authr:
                            authr.request_secret = request_token['oauth_token_secret']
                        else:
                            authr = AuthRequest(owner=user,
                                    request_secret=request_token['oauth_token_secret'])
                                
                        authr.put()
                
                        td["oauth_url"] = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
                
        self.render(td, 'credentials.html')

        
