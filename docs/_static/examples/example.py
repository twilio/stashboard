import oauth2 as oauth
import json
import urllib
import unittest
import random

# Stashboard application id
app_id = "stashboard-hrd"

# These keys can be found at /admin/credentials
consumer_key = 'anonymous'
consumer_secret = 'anonymous'
oauth_key = 'ACCESS_TOKEN'
oauth_secret = 'ACCESS_SECRET'

# Create your consumer with the proper key/secret.
# If you register your application with google, these values won't be
# anonymous and anonymous.
consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth.Token(oauth_key, oauth_secret)

# Create our client.
client = oauth.Client(consumer, token=token)

# Base url for all rest requests
base_url = "https://%s.appspot.com/admin/api/v1" % app_id


# CREATE a new service
data = urllib.urlencode({
        "name": "Generic Web Service",
        "description": "An example web service or REST API",
        })

resp, content = client.request(base_url + "/services",
                               "POST", body=data)
service = json.loads(content)

# GET the list of possible status images
resp, content = client.request(base_url + "/status-images", "GET")
data = json.loads(content)
images = data["images"]

# Pick a random image for our status
image = random.choice(images)

# POST to the Statuses Resources to create a new Status
data = urllib.urlencode({
    "name": "Maintenance",
    "description": "The web service is under-going maintenance",
    "image": image["name"],
    "level": "WARNING",
})

resp, content = client.request(base_url + "/statuses", "POST", body=data)
status = json.loads(content)

# Create a new event with the given status and given service
data = urllib.urlencode({
    "message": "Our first event! So exciting",
    "status": status["id"],
})

resp, content = client.request(service["url"] + "/events", "POST", body=data)
print json.loads(content)
