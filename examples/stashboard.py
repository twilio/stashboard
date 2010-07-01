import oauth2 as oauth
import json
import urllib
from random import choice

oauth_key = '1/PGS5Fvp5hmtUTlHnLyWDVHc8mPrev6IGwa7kicolTT8'
oauth_secret = 'MnqTu_kS47zCs0p0xr9w3H02'

# Create your consumer with the proper key/secret.
# If you register your application with google, these values won't be
# anonymous and anonymous. 
consumer = oauth.Consumer(key='anonymous', secret='anonymous')
token = oauth.Token(oauth_key, oauth_secret)

# Fill in your website
base_url = "https://ismywebservicedown.appspot.com/api/v1"

# Create our client.
client = oauth.Client(consumer, token=token)

data = urllib.urlencode({
    "name": "An Example Service",
    "description": "An example service, created using the StashBoard API",
})

# The OAuth Client request works just like httplib2 for the most part.

# POST to the Services Resource to create a new service. Save the response for
# later
resp, content = client.request(base_url + "/services", "POST", body=data)
service = json.loads(content)

# GET the list of possible status images
resp, content = client.request(base_url + "/status-images", "GET")
data = json.loads(content)
images = data["images"]

# Pick a random image for our status
image = choice(images)

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

print event
