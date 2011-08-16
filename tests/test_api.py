import oauth2 as oauth
import json
import urllib
import unittest
import requests
from google.appengine.ext import testbed
from stashboard.main import application
from webtest import TestApp

class HTTPTest(unittest.TestCase):
    """Easily test HTTP requests against a URL"""
    base = "http://localhost"

    def get(self, url, **kwargs):
        url = self.base + url
        return requests.get(url, **kwargs)

    def post(self, url, **kwargs):
        url = self.base + url
        return requests.post(url, **kwargs)

    def put(self, url, **kwargs):
        url = self.base + url
        return requests.put(url, **kwargs)

    def delete(self, url, **kwargs):
        url = self.base + url
        return requests.delete(url, **kwargs)

    def head(self, url, **kwargs):
        url = self.base + url
        return requests.head(url, **kwargs)


class WSGITest(unittest.TestCase):
    """Easily test HTTP requests against a URL"""

    def get(self, url, **kwargs):
        return self.app.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.app.post(url, **kwargs)

    def put(self, url, **kwargs):
        return self.app.put(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.app.delete(url, **kwargs)

    def head(self, url, **kwargs):
        return self.app.head(url, **kwargs)


class StashboardTest(WSGITest):

    def setUp(self):
        self.app = TestApp(application())
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

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
