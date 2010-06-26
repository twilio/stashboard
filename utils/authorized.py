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
# THE SOFTWARE IS PROVIDED "AS IS",     WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

"""
authorized.py

Created by William Katz on 2008-05-04.
Copyright (c) 2008 Publishare LLC.  Distributed under MIT License.
"""
__author__ = 'William T. Katz'

from google.appengine.api import users
from google.appengine.api import oauth

import logging
import os

def force_ssl(only_admin = False):
    """
    A decorator to enforce the use of SSL when accessing certain resources
    """
    def wrapper(handler_method):
        def check_ssl(self, *args, **kwargs):
            
            user = users.get_current_user()
            admin = users.is_current_user_admin()
            
            if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
                
                handler_method(self, *args, **kwargs)
                
            elif self.request.scheme == "https":
                
                handler_method(self, *args, **kwargs)
                
            elif only_admin and not admin:

                handler_method(self, *args, **kwargs) 
                
            else:
                
                url = self.request.url.replace("http", "https", 1)
                logging.info("Redirecting to SSL version: %s" % url)
                self.redirect(url)
                
        return check_ssl
    return wrapper

def api(role):
    """
    A decorator to enforce user roles in context of the API
    """
    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            host = self.request.headers.get('host', 'nohost')
            
            if self.request.scheme != "https":
                if not os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
                    self.error(403, "SSL is required for POST / PUT / DELETE requests")
                    return

            try:
                user = oauth.get_current_user()
                admin = oauth.is_current_user_admin()
            except oauth.OAuthRequestError, e:
                admin = False
                
            if not admin:
                user = users.get_current_user()
                admin = users.is_current_user_admin()
                
            if not user:
                logging.error("Unauthorized API access attempt")
                self.error(403, "Authorization Failure")
            elif role == "admin" and admin:
                logging.info("Role is %s so will allow handler", role)
                handler_method(self, *args, **kwargs)
            elif user:
                logging.error("User not in admin role")
                self.error(403, "User not in admin role: %s" % role)
            else:
                logging.error("Unknown api role: %s", role)
                self.error(403, "Unknown api role: %s" % role)

        return check_login
    return wrapper

def role(role):
    """
    A decorator to enforce user roles, currently 'user' (logged in) 
    and 'admin'.

    To use it, decorate your handler methods like this:

    import authorized
    @authorized.role("admin")
    def get(self):
      user = users.GetCurrentUser(self)
      self.response.out.write('Hello, ' + user.nickname())

    If this decorator is applied to a GET handler, we check if the 
    user is logged in and redirect her to the create_login_url() if not.

    For HTTP verbs other than GET, we cannot do redirects to the login 
    url because the return redirects are done as GETs (not the original 
    HTTP verb for the handler).  So if the user is not logged in, we 
    return an error.
    """
    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            
            user = users.get_current_user()
            
            if not user:
                if self.request.method != 'GET':
                    logging.debug("Not user - aborting")
                    self.error(403)
                else:
                    logging.debug("User not logged in -- force login")
                    self.redirect(users.create_login_url(self.request.uri))
            elif role == "user" or (role == "admin" and     
                                    users.is_current_user_admin()):
                logging.debug("Role is %s so will allow handler", role)
                handler_method(self, *args, **kwargs)
            else:
                if self.request.method == 'GET':
                    logging.debug("Unknown role (%s) on GET", role)
                    self.redirect("/403.html")
                else:
                    logging.debug("Unknown role: %s", role)
                    self.error(403) # User didn't meet role.  
                                    # TODO: Give better feedback/status code.
        return check_login
    return wrapper


