require 'rubygems'
require 'oauth'
require 'json'

oauth_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
oauth_secret = 'YYYYYYYYYYYYYYYYYYYYYYYY'

# Fill in your website
base = "https://stashboard.appspot.com"

@consumer=OAuth::Consumer.new "anonymous", 
                              "anonymous",
                              {:site=>base}
                              
@token = OAuth::AccessToken.new(@consumer, oauth_key, oauth_secret)

# POST to the Services Resource to create a new service. Save the response for
# later
@response = @token.post("/api/v1/services", {
    :name => "An Example Service",
    :description => "An example service, created using the StashBoard API",
})
srvice = JSON.parse(@response.body)

# GET the list of possible status images
@response = @token.get("/api/v1/status-images")
data = JSON.parse(@response.body)
images = data['images']

# Pick a random image for our status
image = images[rand(images.length)]


# POST to the Statuses Resources to create a new Status
@response = @token.post("/api/v1/statuses", {
    :name => "Example Status",
    :description => "An example status, means nothing",
    :severity => 10000,
    :image => image["name"],
})

status = JSON.parse(@response.body)

@response = @token.post("/api/v1/services/" + srvice["id"] + "/events", {
    :message => "Our first event! So exciting",
    :status => status["id"],
})
event = JSON.parse(@response.body)

puts event