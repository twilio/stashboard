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
from models import Status, Message
import config

class NotFoundHandler(restful.Controller):
    def get(self):
        logging.debug("NotFoundHandler#get")
        self.error(404)
        template_data = {}
        self.render(template_data, '404.html')

class UnauthorizedHandler(restful.Controller):
    def get(self):
        logging.debug("UnauthorizedHandler#get")
        self.error(403)
        template_data = {}
        self.render(template_data, 'unathorized.html')
        
class SlashHandler(restful.Controller):
    def get(self, url):
        self.redirect("%s/" % url)

class RootHandler(restful.Controller):
    def get(self):
        user = users.get_current_user()
        logging.debug("RootHandler#get")
        
        q = Message.all()
        q.order("-date")
        
        template_data = {
            "user": users.get_current_user(),
            "user_is_admin": users.is_current_user_admin(),
            "statuses": config.SITE["options"],
            "posts": q.fetch(10),
            "twitter": config.SITE["twitter"],
        }
        self.render(template_data, 'base.html')

    # @authorized.role("admin")
    # def post(self):
    #     logging.debug("RootHandler#post")
    #     message = cgi.escape(self.request.get('message'))
    #     status = cgi.escape(self.request.get('status'))
    #     
    #     if status and status in config.SITE["options"].keys():
    #         state = currentStatus()
    #         state.status = status
    #         state.put()
    #         
    #     if message:
    #         post = Message(text=message)
    #         post.put()
    #         
    #     self.redirect("/")
    #         
            
        