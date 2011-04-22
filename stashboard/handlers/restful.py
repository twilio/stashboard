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

"""
RESTful Controller

We want our RESTful controllers to simply throw up their hands if they get
an unhandled HTTP verb.  This is better for rich clients and server load
than throwing back lots of useless HTML.

These inherited methods should be overridden if there's a chance a human
browser is involved.

TODO: Return more information HTTP status codes that won't autotrip 
browser login forms.  For example, return status 405 (Method not allowed) 
with an Allow header containing the list of valid methods.
"""
__author__ = 'William T. Katz'

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import jsonpickle
import logging
import os
import config
import cgi

# Some useful module methods
def send_successful_response(handler, response):
    # Response is probably just a URL.
    logging.debug("Sending successful response: %s", response)
    handler.response.out.write(response)

def get_sent_properties(request_func, propname_list):
    """
    This maps request strings to values in a hash, optionally run through 
    a function with previous request values as parameters to the func.
    1) key -> just read in the corresponding request value
    2) tuple (key, func) -> Read the request value for the string key
        and pass it through func
    3) tuple (key, func, additional keys...) -> Get the request
        values for the additional keys and pass them through func
        before setting the key's value with the output.
    If a key is not present in the request, then we do not insert a key
    with None or empty string.  The key is simply absent, therefore allowing
    you to use the returned hash to initial a Model instance.
    """
    prop_hash = {}
    for item in propname_list:
        if isinstance(item, basestring):
            key = item
            value = request_func(item)
        elif isinstance(item, tuple):
            key = item[0]
            prop_func = item[1]
            if len(item) <= 2:
                value = prop_func(request_func(key))
            else:
                try:
                    addl_keys = map(prop_hash.get, item[2:])
                    value = prop_func(*addl_keys)
                except:
                    return None
        if value:
            prop_hash[key] = value
    return prop_hash

def methods_via_query_allowed(handler_method):
    """
    A decorator to automatically re-route overloaded POSTs
    that specify the real HTTP method in a _method query string.

    To use it, decorate your post method like this:

    import restful
    ...
    @restful.methods_via_query_allowed
    def post(self):
      pass

    The decorator will check for a _method query string or POST argument,
    and if present, will redirect to delete(), put(), etc.
    """
    def redirect_if_needed(self, *args, **kwargs):
        real_verb = self.request.get('_method', None)
        if not real_verb and 'X-HTTP-Method-Override' in self.request.environ:
            real_verb = self.request.environ['X-HTTP-Method-Override']
        if real_verb:
            logging.debug("Redirected from POST. Detected method override = %s", real_verb)
            method = real_verb.upper()
            if method == 'HEAD':
                self.head(*args, **kwargs)
            elif method == 'PUT':
                self.put(*args, **kwargs)
            elif method == 'DELETE':
                self.delete(*args, **kwargs)
            elif method == 'TRACE':
                self.trace(*args, **kwargs)
            elif method == 'OPTIONS':
                self.head(*args, **kwargs)
            # POST and GET included for completeness
            elif method == 'POST':
                self.post(*args, **kwargs)
            elif method == 'GET':
                self.get(*args, **kwargs)
            else:
                self.error(405)
        else:
            handler_method(self, *args, **kwargs)
    return redirect_if_needed
    
class Controller(webapp.RequestHandler):
    """Responsible for handling all API requests"""

    def base_url(self, version):
        "Returns the base url for the given host and version"
        host = self.request.headers.get('host', 'nohost')
        return self.request.scheme + "://" + host + "/api/" + version
        
    def valid_version(self, version):
        return version == "v1"
    
    def error(self, code, message=None):
        "Returns the JSON representation of an error message"
        self.response.set_status(code)
        
        error = { "error": True, "code": code}
        if (message):
            error["message"] = message
            
        self.json(error)
        
    def success(self, message=None):
        "Returns the JSON representation of a success message"
        self.response.set_status(200)
        
        success = { "error": False, "code": 200}
        if (message):
            success["message"] = message
            
        self.json(success)
        
    
    def get(self, *params):
        self.redirect("/.html")

    def head(self, *params):
        pass
        
    def render(self, templateparams, *args):
        "Writes templateparams to a given template"
        path = config.SITE["template_path"]

        for p in args:
            path = os.path.join(path, p)
            
        self.response.out.write(template.render(path, templateparams))
        
    def json(self, data):
        """
        Renders the given data as json. 
        If callback is valid, renders data as jsonp
        """
        callback = self.request.get('callback', default_value=None)
        
        data = cgi.escape(jsonpickle.encode(data))
        
        if callback:
            self.response.headers.add_header("Content-Type", "application/javascript")
            data = callback + "(" + data + ");"
        else:
            self.response.headers.add_header("Content-Type", "application/json")
        
        self.response.out.write(data)
        
    def text(self, data):
        "Renders the given data as text/plain"
        self.response.headers.add_header("Content-Type", "text/plain")
        self.response.out.write(data)
        
    def xml(self, data):
        """
        Renders the given data as XML
        Currently unsupported
        """
        pass
