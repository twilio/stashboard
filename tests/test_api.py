import oauth2 as oauth
import urllib
import unittest
import requests
from google.appengine.ext import testbed
from main import application
from models import Service
from webtest import TestApp


class HTTPTest(unittest.TestCase):
    """Easily test HTTP requests against a URL"""
    base = "http://localhost"

    def request(self, method, url, **kwargs):
        url = self.base + url
        return requests.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("HEAD", url, **kwargs)


class WSGITest(HTTPTest):
    """Easily test HTTP requests against a URL"""

    def request(self, method, url, **kwargs):
        return self.app.request(method, url, **kwargs)


class StashboardTest(WSGITest):

    def setUp(self):
        self.app = TestApp(application())
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(auth_domain="testbed")
        self.authenticate("123", "a@b.c", admin=True)

        self.testbed.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def authenticate(self, name, email, admin=False):
        admin_value = "1" if admin else "0"
        self.testbed.setup_env(user_is_admin=admin_value, user_email=email,
                               user_id=name, overwrite=True)

    def tearDown(self):
        self.testbed.deactivate()
