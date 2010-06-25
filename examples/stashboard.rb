require 'rubygems'
require 'oauth'
require 'json'

@oauth_key = '1/PGS5Fvp5hmtUTlHnLyWDVHc8mPrev6IGwa7kicolTT8'
@oauth_secret = 'MnqTu_kS47zCs0p0xr9w3H02'

# Fill in your website
@base = "https://ismywebservicedown.appspot.com"

@consumer=OAuth::Consumer.new "anonymous", 
                              "anonymous",
                              {:site=>@base}
                              
@token = OAuth::ConsumerToken.new @consumer,@oauth_key, @oauth_secret

# The OAuth Client request works just like httplib2 for the most part.

# POST to the Services Resource to create a new service. Save the response for
# later
rsp = @consumer.request(:post, "/api/v1/services", @token, {
    :name => "An Example Service",
    :description => "An example service, created using the StashBoard API",
})

puts rsp.body