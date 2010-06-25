## Examples

The following examples will use the StashBoard REST API to create a service, create a status, and then create an event with the new status for the new service. Sample code is provided for Python, Ruby, and PHP. 

If you haven't already, head over to the [API Credentials section](/documentation/credentials) to obtain your API key. Please note that you must be an administrator to make changes via the REST API.

### Python

This example uses the great [python-oauth2](http://github.com/simplegeo/python-oauth2) library by Leah Culver.

    import oauth2 as oauth
    import json
    import urllib
    from random import choice
    
    oauth_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    oauth_secret = 'YYYYYYYYYYYYYYYYYYYYYYYY'

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





### Ruby

Before you can run this example, make sure to install the [oauth Ruby Gem](http://github.com/pelle/oauth).
    
    require 'rubygems'
    require 'oauth'
    require 'json'

    oauth_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    oauth_secret = 'YYYYYYYYYYYYYYYYYYYYYYYY'

    # Fill in your website
    base = "https://ismywebservicedown.appspot.com"

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


### PHP

This example uses Andy Smith's great [basic OAuth library](http://oauth.googlecode.com/svn/code/php/) for URL signing. You must also have the cURL extension enabled for this code to run.

    <?php

      require_once('OAuth.php');
  
      $consumer_key = 'anonymous';
      $consumer_secret = 'anonymous';
      $oauth_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
      $oauth_secret = 'YYYYYYYYYYYYYYYYYYYYYYYY'
  
      $consumer = new OAuthConsumer($consumer_key, $consumer_secret);
      $token = new OAuthToken($oauth_key, $oauth_secret);
  
  
      // Set up a request function  
      function request($consumer, $token, $url, $method = "GET", $data = null){
    
        $sign = new OAuthSignatureMethod_HMAC_SHA1();
        $request = OAuthRequest::from_consumer_and_token(
          $consumer, $token, $method, $url, $data);
        $request->sign_request($sign, $consumer, $token);

        $ch = curl_init($request->get_normalized_http_url());
    
        if ($method == "POST") {
          curl_setopt($ch, CURLOPT_POST ,1);
          curl_setopt($ch, CURLOPT_POSTFIELDS , $request->to_postdata());
        }
    
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION ,1);
        curl_setopt($ch, CURLOPT_HEADER ,0);  // DO NOT RETURN HTTP HEADERS
    
        return curl_exec($ch);
      }
  
      // Fill in your website
      $base_url = "https://ismywebservicedown.appspot.com/api/v1";
  
      $data = array(
          "name" => "An Example Service",
          "description" => "An example service, created using the StashBoard API",
      );
  
      $r = request($consumer, $token, $base_url . "/services", "POST", $data);
      $service = json_decode($r);
  
      // GET the list of possible status images
      $r = request($consumer, $token, $base_url . "/status-images", "GET");
      $data = json_decode($r);
      $images = $data->images;
  


      // Pick a the first image
      $image = $images[0];
  
      // POST to the Statuses Resources to create a new Status
      $data = array(
         "name" => "Example Status",
         "description" => "An example status, means nothing",
         "severity" => 10000,
         "image" => $image->name,
      );
  
      $r = request($consumer, $token, $base_url . "/statuses", "POST", $data);
      $status = json_decode($r);
  
      // Create a new event with the given status and given service
      $data = array(
         "message" => "Our first event! So exciting",
         "status" => $status->id,
      );
  
      $r = request($consumer, $token, $service->url . "/events", "POST", $data);
      $event = json_decode($r);
  
      print_r($event);
   
    ?>