import oauth2 as oauth
import json
import urllib
import unittest

class ServicesTest(unittest.TestCase):

    def testMissingServiceName(self):
        "should return 400 Bad Data"
        data = urllib.urlencode({
                "description": "An example service API",
                })

        resp, content = client.request(base_url + "/services",
                                       "POST", body=data)

        self.assertEquals(resp.status, 400)

    def testMissingServiceDescription(self):
        "should return 400 Bad Data"
        data = urllib.urlencode({
                "name": "Some Random Name",
                })

        resp, content = client.request(base_url + "/services",
                                       "POST", body=data)

        self.assertEquals(resp.status, 400)

    def testMissingServiceData(self):
        "should return 400 Bad Data"
        resp, content = client.request(base_url + "/services", "POST")
        self.assertEquals(resp.status, 400)

    def testDelete(self):
        "should return 405 Method Not Allowed"
        resp, content = client.request(base_url + "/services", "DELETE")
        self.assertEquals(resp.status, 405)

    def testPut(self):
        "should return 411 Content Length Required"
        resp, content = client.request(base_url + "/services", "PUT")
        self.assertEquals(resp.status, 411)

    def testPutWithData(self):
        "should return 405 Method Not Allowed"
        data = urllib.urlencode({
                "name": "Some Random Name",
                })
        resp, content = client.request(base_url + "/services",
                                       "PUT", body=data)
        self.assertEquals(resp.status, 405)

    def testServiceLifeCycle(self):
        "should return 200 and a newly created status"
        data = urllib.urlencode({
                "name": "What a service",
                "description": "An example service API",
                })

        resp, content = client.request(base_url + "/services",
                                       "POST", body=data)
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API")

        service_url = base_url + "/services/" + service["id"]
        resp, content = client.request(service_url, "GET")
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API")

        # Update service
        data = urllib.urlencode({
                "description": "An example service API woohoo",
                })

        resp, content = client.request(service_url, "POST", body=data)
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"],
                          "An example service API woohoo")

        # Delete service
        resp, content = client.request(service_url, "DELETE")
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"],
                          "An example service API woohoo")

if __name__ == '__main__':
    unittest.main()
