## REST API Basics

The REST API always returns a JSON object. A list resource is represented as a object with a "resource-name" attribute

    {
        "resource-name": ["List", "of", "objects"]
    }
    
### Authentication
    
No authentication is needed to access resources via HTTP GET; however, all other methods require authentication. Authentication via OAuth is covered in the ["Authentication section"](/documentation/authentication)
    
### Base URL

All URLs referenced in this document, including sample API return objects, have the following base URL:

    http[s]://status.your.domain.com
    
## Services List Resource

The Services List resource represents all web services currently tracked via StashBoard. The resources also allows for the creation of new, trackable web services.

### Resource URL

> /api/v1/services

### Resource Properties

-------------------------------------------------------------

Property       Description
---------       ---------------------------------------------
id              The unique identifier by which to identify 
                the service
                
name            The name of the service, defined by the user

description     The description of the web service

current-event   The current event for the service

url             The URL of the specific service resource
-------------------------------------------------------------
Table: Service resource properties

### HTTP Methods

#### GET

Returns a list of all current services tracked by StashBoard

##### Example

> GET /api/v1/services HTTP/1.1

    {
        "services": [
            {
                "name": "Example Foo",
                "id": "example-foo",
                "description": "An explanation of this service"
                "url": "/api/v1/services/example-foo",
                "current-event": {
                    'message': 'What an event!',
                    'sid': 'ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M',
                    'status': {
                        'description': 'Hey, dude',
                        'id': 'up',
                        'image': '/images/status/tick-circle.png',
                        'level': 'NORMAL',
                        'name': 'Up',
                        'url': '/statuses/up'
            },
                    'timestamp': 'Mon, 28 Jun 2010 22:17:06 GMT',
                    'url': '/services/twilio/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M'},

            },
            {
                "name": "Example Bar",
                "id": "example-bar",
                "description": "An explanation of this service"
                "url": "/api/v1/services/example-bar",
                "current-event": null,
            }
        ]
    }
    
#### POST

Creates a new service (or updates an existing service) and returns the new service object. 

-------------------------------------------------------------

Param          Optional    Description
-----           ---------   --------------------------------
name            Required    Name of the service

description     Required    Description of service
------------------------------------------------------------
Table: Services List POST parameters

##### Example

> POST /api/v1/services HTTP/1.1
name=New%20Service&description=A%20great%20service

    {
        "name": "New Service",
        "id": "new-service",
        "description": "A great service"
        "url": "/api/v1/services/new-service",
        "current-event": null,
    }

## Service Instance Resource

The Service Instance resources represents an individual web service tracked by StashBoard

### Resource Url

> /api/v1/services/{service}

### HTTP Methods

#### GET

Returns a service object

##### Example

> GET /api/v1/services/{service} HTTP/1.1

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "An explanation of what this service represents"
        "url": "/api/v1/services/example-service",
        "current-event": null,
    }
    
#### POST

Updates a service's description and returns the updated service object.

-------------------------------------------------------------

Param          Optional    Description
-----           ---------   --------------------------------
name            Optional    Name of the service

description     Optional    Description of service
-------------------------------------------------------------
Table: Service Instance POST parameters

##### Example

> POST /api/v1/services/{service} description=System%20is%20now%20operational

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System is now operational",
        "url": "/api/v1/services/example-service",
        "current-event": null,
    }

### DELETE

Deletes a service and returns the deleted service object

#### Example

> DELETE /api/v1/services/{service} HTTP/1.1

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System is now operational",
        "url": "/api/v1/services/example-service",
        "current-event": null,
    }


## Events List Resource

The Events List resource represents all event associated with a given service

### Resource URL

> /api/v1/services/{service}/events

### Properties

-------------------------------------------------------------

Property       Description
---------       ---------------------------------------------
sid             The unique identifier by which to identify 
                the event
                
message         The message associated with this event

timestamp       The time at which this event occurred, given
                in RFC 1132 format.

url             The URL of the specific event resource

status          The status of this event, as described by the 
                Statuses resource
-------------------------------------------------------------
Table: Event resource properties

### HTTP Methods

#### GET

Returns all events associated with a given service in reverse chronological order. 

##### Example

> GET /api/v1/services/{service}/events HTTP/1.1

    {
        "events": [
            {
                "timestamp": "Mon, 28 Jun 2010 22:17:06 GMT",
                "message": "Problem fixed", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM",
                "url": "/api/v1/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd2",
                "status": {
                    "id": "down",
                    "name": "Down",
                    "description": "An explanation of what this status represents",
                    "level": "ERROR",
                    "image": "/static/images/status/cross-circle.png",
                    "url": "/api/v1/statuses/down",
                },
            }, 
            {
                "timestamp": "Mon, 28 Jun 2010 22:18:06 GMT",
                "message": "Might be up", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
                "url": "/api/v1/services/example-service/events/ahJpc215d2Vic..."
                "status": {
                    "id": "down",
                    "name": "Down",
                    "description": "An explanation of what this status represents",
                    "level": "ERROR",
                    "image": "/static/images/status/cross-circle.png",
                    "url": "/api/v1/statuses/down",
                },
            }
        ]
    }



#### POST

Creates a new event for the given service and returns the newly created event object

-------------------------------------------------------------

Param      Optional    Description
-----       ---------   --------------------------------
status      Required    The system status for the event.
                        This must be a valid system 
                        status identifier found in the 
                        Statuses List resource

message     Required    The message for the event
-------------------------------------------------------------
Table: Events List POST parameters

##### Example

> POST /api/v1/services/{service}/events  HTTP/1.1 status=AVAILABLE&message=System%20is%20now%20operational

    {
        "timestamp": "Mon, 28 Jun 2010 22:18:06 GMT"
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/api/v1/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "id": "down",
            "name": "Down",
            "description": "An explanation of what this status represents",
            "level": "ERROR",
            "image": "/static/images/status/cross-circle.png",
            "url": "/api/v1/statuses/down",
        },
    }
    
#### PUT

Not supported

#### DELETE

Not supported

### URL Filtering
    
The Events List resource also supports filtering events via dates. To filter events, place on of the following options into the query string for a GET request

While the format of these parameters is very flexible, we suggested either the RFC 2822 or RFC 1123 format due to their support for encoding timezone information.

-------------------------------------------------------------

Option     Description
-----       --------------------------------
start	    Only show events which started after
            this date, inclusive.
            
end         Only show events which started before
	    this date, inclusive. 

-------------------------------------------------------------
Table: Events List URL Filtering Options

##### Example

> GET /api/v1/services/{service}/events?start=2010-06-10 HTTP/1.1

would return all events starting after June 6, 2010. 

Similarly, both "start" and "end" can be used to create date ranges

> GET /api/v1/services/{service}/events?end=2010-06-17&start=2010-06-01 HTTP/1.1

would return all events between June 6, 2010 and June 17, 2010  
  
## Current Service Event

The Current Service Event resource simply returns the current event for a given service.

### Resource Url

> /api/v1/services/{service}/events/current

### GET

Returns the current event for a given service.

#### Example

> GET /api/v1/services/{service}/events/current HTTP/1.1

    {
        "timestamp": "Mon, 28 Jun 2010 22:17:06 GMT",
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/api/v1/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "id": "down",
            "name": "Down",
            "description": "An explanation of what this status represents",
            "level": "ERROR",
            "image": "/static/images/status/cross-circle.png",
            "url": "/api/v1/statuses/down",
        },
    }

### POST / PUT

Not supported

### DELETE

Not supported

## Event Instance Resource

The Event Instance resource represents an individual event for a given service.

### Resource URL

> /services/{service}/events/{sid}

### HTTP Methods

#### GET

Returns a service event with the given event sid. The event's status object is also returned as well.

##### Example

> GET /api/v1/services/{service}/events/{sid} HTTP/1.1

    {
        "timestamp": "Mon, 28 Jun 2010 22:17:06 GMT",
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/api/v1/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "id": "down",
            "name": "Down",
            "description": "An explanation of what this status represents",
            "level": "ERROR",
            "image": "/static/images/status/cross-circle.png",
            "url": "/api/v1/statuses/down",
        },
    }

#### POST / PUT

Not supported

#### DELETE

Deletes the given event and returns the deleted event

##### Example

> DELETE /services/{service}/events/{sid} HTTP/1.1

    {
        "timestamp": "Mon, 28 Jun 2010 22:17:06 GMT",
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "id": "down",
            "name": "Down",
            "description": "An explanation of what this status represents",
            "level": "ERROR",
            "image": "/static/images/status/cross-circle.png",
            "url": "/statuses/down",
        },    
    }

## Status List Resource

The Status List resource represents all possible systems statuses.

### Resource URL

> api/v1/statuses

### Resource Properties

-------------------------------------------------------------

Property       Description
---------       ---------------------------------------------
id              The unique identifier by which to identify 
                the status
                
name            The name of the status, defined by the user

description     The description of the status

url             The URL of the specific status resource

level           The level of this status. Can be any value
                listed in the Levels List resource
                
image           The URL of the image for this status
-------------------------------------------------------------
Table: Status resource properties

### HTTP Methods

#### GET

Returns all possible service statuses

##### Example

> GET api/v1/statuses HTTP/1.1

    {
        "statuses": [
            {
                "name": "Available",
                "id": "available",
                "description": "An explanation of what this status represents",
                "level": "NORMAL",
                "image": "/static/images/status/tick-circle.png",
                "url": "api/v1/statuses/up",
            },
            {
                "name": "Down",
                "id": "down",
                "description": "An explanation of what this status represents",
                "level": "ERROR",
                "image": "/static/images/status/cross-circle.png",
                "url": "api/v1/statuses/down",
            },
        ]
    }
    
#### POST

Creates a new service status and returns this newly created status

-------------------------------------------------------------

Param          Optional    Description
-----           ---------   --------------------------------
name            Required    The name of the status

description     Required    The description of the status

level        	Required    The level of the status.
			    Must be a values listed in the
			    Levels resource

image           Required    The filename of the image, with
                            no extension. See the 
                            status-images resource
-------------------------------------------------------------
Table: Status Instance POST parameters

##### Example

> POST /api/v1/statuses HTTP/1.1
name=Down&description=A%20new%20status&severity=1000&image=cross-circle.png

    {
        "name": "Down",
        "id": "down"
        "description": "A new status",
        "level": "ERROR",
        "image": "cross-circle",
        "url": "/api/v1/statuses/down",
    }

#### PUT

Not Supported

#### DELETE

Not Supported

## Status Instance Resource

The Status Instance resource represents a single service status

### Resource Url

> /api/v1/statuses/{name}

### GET

Returns a status object

#### Example

    {
        "name": "Down",
        "id": "down",
        "description": "A new status",
        "level": "ERROR",
        "image": "/static/images/status/cross-circle.png",
        "url": "/api/v1/statuses/down",
    }
    
### POST

-------------------------------------------------------------

Param          Optional    Description
-----           ---------   --------------------------------
name            Optional    The name of the status

description     Optional    The description of the status

level           Optional    The level of the status. Must be
                            a string value listed in the
                            Levels resource (see below)

image           Optional    The filename of the image, with
                            no extension. See the 
                            status-images resource
-------------------------------------------------------------
Table: Status Instance POST parameters

Returns the newly updated status

#### Example

> POST /api/v1/statuses HTTP/1.1
description=A%20new%20status&severity=1010&image=cross-circle.png

    {
        "name": "Down",
        "id": "down",
        "description": "A new status",
        "level": "ERROR",
        "image": "/static/images/status/cross-circle.png",
        "url": "/api/v1/statuses/down",
    }

### DELETE

Delete the given status and return the deleted status

#### Example

> DELETE /api/v1/statuses/{name}

    {
        "name": "Down",
        "id": "down",
        "description": "A new status",
        "level": "ERROR",
        "image": "/static/images/status/cross-circle.png",
        "url": "/api/v1/statuses/down",
    }

### PUT 

Not supported

## Status Levels Resource

The Status Levels resource is a read-only resource which lists the possible levels for a status. 

### Resource Url

> /api/v1/levels

### GET

Returns a list of possible status levels in increasing severity

#### Example

> GET /api/v1/levels

    {
        "levels": [
            "INFO", 
            "NORMAL", 
            "WARNING", 
            "ERROR", 
            "CRITICAL",
        ]
    }
    
### POST / PUT

Not supported

### DELETE

Not supported

## Status Images Resource

The Status Images resource is a read-only resource which lists the icons available to use for statuses

### Resource Url

> /api/v1/status-images

### GET

Returns a list of status images.

#### Example

> GET /api/v1/status-images

    {
        "images": [
            {
                "name": "sample-image",
                "url": "/status-images/sample-image.png",
            },
            {
                "name": "sample-image",
                "url": "/status-images/sample-image.png",
            },
        ]
    }
    
### POST / PUT

Not supported

### DELETE

Not supported 
