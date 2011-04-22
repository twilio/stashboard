import oauth2 as oauth
import json
import urllib
import unittest

oauth_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
oauth_secret = 'YYYYYYYYYYYYYYYYYYYYYYYY'

# Create your consumer with the proper key/secret.
# If you register your application with google, these values won't be
# anonymous and anonymous. 
consumer = oauth.Consumer(key='anonymous', secret='anonymous')
token = oauth.Token(oauth_key, oauth_secret)

# Fill in your website
base_url = "https://stashboard.appspot.com/api/v1"

# Create our client.
client = oauth.Client(consumer, token=token)

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

        resp, content = client.request(base_url + "/services", "POST", body=data)
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API")

        resp, content = client.request(base_url + "/services/" + service["id"], "GET")
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API")

        # Update service
        data = urllib.urlencode({
                "description": "An example service API woohoo",
                })

        resp, content = client.request(base_url + "/services/" + service["id"],
                                       "POST", body=data)
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API woohoo")

        # Delete service
        resp, content = client.request(base_url + "/services/" + service["id"],
                                       "DELETE")
        service = json.loads(content)

        self.assertEquals(resp.status, 200)
        self.assertEquals(service["name"], "What a service")
        self.assertEquals(service["description"], "An example service API woohoo")

if __name__ == '__main__':
    unittest.main()

# GET the list of possible status images
resp, content = client.request(base_url + "/status-images", "GET")
data = json.loads(content)
images = data["images"]

# Pick a random image for our status
image = images[0]

# POST to the Statuses Resources to create a new Status
data = urllib.urlencode({
    "name": "Example Status",
    "description": "An example status, means nothing",
    "severity": 10000,
    "image": image["name"],
})

resp, content = client.request(base_url + "/statuses", "POST", body=data)
status = json.loads(content)

# Create a new event with the given status and given service
data = urllib.urlencode({
    "message": "Our first event! So exciting",
    "status": status["id"],
})

resp, content = client.request(service["url"] + "/events", "POST", body=data)
event = json.loads(content)

