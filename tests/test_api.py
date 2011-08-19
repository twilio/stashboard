import oauth2 as oauth
import json
import urllib
import unittest
import requests
from google.appengine.ext import testbed
from stashboard.main import application
from webtest import TestApp
import oauth2 as oauth

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


class PublicServicesTest(StashboardTest):

    def test_get(self):
        response = self.get("/api/v1/services")
        self.assertEquals(response.status_code, 200)

    def test_post(self):
        response = self.post("/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        response = self.delete("/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        response = self.put("/api/v1/services")
        self.assertEquals(response.status_code, 405)


class ServicesTest(StashboardTest):

    def test_create_service_name(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API",
                                   "name": "Some Random Name"})
        self.assertEquals(response.status_code, 201)

    def test_missing_service_name(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API"})
        self.assertEquals(response.status_code, 400)

    def test_missing_service_description(self):
        """Services should 400 without a description"""
        response = self.post("/admin/api/v1/services",
                                  data={"name": "Some Random Name"})
        self.assertEquals(response.status_code, 400)

    def test_missing_service_data(self):
        """Creating a service should 400 without data"""
        response = self.post("/admin/api/v1/services")
        self.assertEquals(response.status_code, 400)

    def test_delete(self):
        "should return 405 Method Not Allowed"
        response = self.delete("/admin/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        """Should return 405 Content Length Required"""
        response = self.put("/admin/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_put_with_data(self):
        """should return 405 Method Not Allowed"""
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API"})
        self.assertEquals(response.status_code, 405)

if __name__ == '__main__':
    unittest.main()
