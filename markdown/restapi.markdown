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
    
## Services

The services REST resource represents all web services currently tracked via Stashboard. The resources also allows for the creation of new, trackable web services.

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

url             The URL of the specific service resource
-------------------------------------------------------------

### HTTP Methods

#### GET

Returns a list of all current services tracked by Stashboard

##### Example

> GET /api/v1/services HTTP/1.1

    {
        "services": [
            {
                "name": "Example Foo",
                "id": "example-foo",
                "description": "An explanation of this service"
                "url": "/api/v1/services/example-foo",
            },
            {
                "name": "Example Bar",
                "id": "example-bar",
                "description": "An explanation of this service"
                "url": "/api/v1/services/example-bar",
            }
        ]
    }
    
#### POST

Create a new service (or updates an existing server) and returns the new service object. 

-------------------------------------------------------------

Param          Optional    Description
-----           ---------   --------------------------------
name            Required    Name of the service

description     Required    Description of service
-------------------------------------------------------------
Table: Service POST parameters

##### Example

> POST /services HTTP/1.1
name=New%20Service&description=A%20great%20service

    {
        "name": "New Service",
        "id": "new-service",
        "description": "A great service"
        "url": "/services/new-service",
        "defaultStatus": {}
    }


## /services/{service}

### GET

Returns a service instance

#### Example

> GET /services/{service} HTTP/1.1

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "An explanation of what this service represents"
        "url": "/services/example-service",
    }
    
### POST

Update a service's description. Returns the updated object

* **description**: Description of service

#### Example

> POST /services/{service} description=System%20is%20now%20operational

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System% is now operational",
        "url": "/services/example-service",
    }

### DELETE

Delete a service, returns the service object deleted

#### Example

> DELETE /services/{service} HTTP/1.1

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System% is now operational",
        "url": "/services/example-service",
    }

## /services/{service}/events

### GET

Returns all events associated with a given service, ordered by reverse chronological order. 

#### Example

> GET /services/{service}/events HTTP/1.1

    {
        "events": [
            {
                "timestamp": "2010-05-22T01:52:23.104012", 
                "message": "Problem fixed", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM",
                "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM",
                "status": {
                    "name": "down",
                    "description": "An explanation of what this status represents",
                    "severity": 1000,
                    "image": "/static/images/status/cross-circle.png",
                    "url": "/statuses/down",
                },
            }, 
            {
                "timestamp": "2010-05-22T01:52:16.383246", 
                "message": "Might be up", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
                "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
                "status": {
                    "name": "down",
                    "description": "An explanation of what this status represents",
                    "severity": 1000,
                    "image": "/static/images/status/cross-circle.png",
                    "url": "/statuses/down",
                },
            }
        ]
    }

### POST

#### Parameters

* **status**: An valid system status identifier. See /statuses
* **message**: A message for the event

Will return the newly created event

#### Example

> POST /services/{service}/events  HTTP/1.1 status=AVAILABLE&message=System%20is%20now%20operational

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "name": "down",
            "description": "An explanation of what this status represents",
            "severity": 1000,
            "image": "/static/images/status/cross-circle.png",
            "url": "/statuses/down",
        },
    }
    
### PUT

Not supported

### DELETE

Not supported
    
## /services/{service}/events/current

### GET

Returns the current service status

#### Example

> GET /services/{service}/events/current HTTP/1.1

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "name": "down",
            "description": "An explanation of what this status represents",
            "severity": 1000,
            "image": "/static/images/status/cross-circle.png",
            "url": "/statuses/down",
        },
    }

### POST / PUT

Not supported

### DELETE

Not supported

## /services/{service}/calendar

### GET

Supports query parameters start and end, which are dates

returns 

    {
        calendar: [
            {
                date: "June 21, 2010",
                events: [],
                summary: status
            },
            {
                date: "June 20, 2010",
                events: [],
                summary: status
            },
            {
                date: "June 19, 2010",
                events: [],
                summary: status
            },
            {
                date: "June 18, 2010",
                events: [],
                summary: status
            },
            {
                date: "June 17, 2010",
                events: [],
                summary: status
            },
        ]
    }
    
Where summary is the overall status of the system for that day

## /services/{service}/events/{sid}

Returns the status with the given sid

### GET

#### Example

> GET /services/{service}/events/{sid}

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "name": "down",
            "description": "An explanation of what this status represents",
            "severity": 1000,
            "image": "/static/images/status/cross-circle.png",
            "url": "/statuses/down",
        },
    }

### POST / PUT

Not supported

### DELETE

Deletes the given event. Returns the deleted event

#### Example

> DELETE /services/{service}/events/{sid} HTTP/1.1

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": {
            "name": "down",
            "description": "An explanation of what this status represents",
            "severity": 1000,
            "image": "/static/images/status/cross-circle.png",
            "url": "/statuses/down",
        },    
    }


## /statuses

### GET

Returns the possible states

#### Example

> GET /statuses HTTP/1.1

    {
        "statuses": [
            {
                "name": "available",
                "description": "An explanation of what this status represents",
                "severity": 10,
                "image": "/static/images/status/tick-circle.png",
                "url": "/statuses/up",
            },
            {
                "name": "down",
                "description": "An explanation of what this status represents",
                "severity": 1000,
                "image": "/static/images/status/cross-circle.png",
                "url": "/statuses/down",
            },
        ]
    }
    
### POST

#### Parameters
* **name**: The type of the new status
* **description**: The explanation of the status
* **severity**: The severity of the status
* **image**: The filename of the image. No path information

#### Example

> POST /statuses HTTP/1.1
name=down&description=A%20new%20status&severity=1000&image=cross-circle.png

    {
        "name": "down",
        "description": "A new status",
        "severity": 1000,
        "image": "cross-circle",
        "url": "/statuses/down",
    }

### DELETE

Not Supported

### PUT

Not Supported

## /statuses/{name}

### GET

Return a status

#### Example

    {
        "name": "down",
        "description": "A new status",
        "severity": 1000,
        "image": "/static/images/status/cross-circle.png",
        "url": "/statuses/down",
    }
    
### POST
* **description**: The explanation of the status
* **severity**: The severity of the status
* **image**: The filename of the image. No path information

Returns the newly updated status

#### Example

> POST /statuses HTTP/1.1
description=A%20new%20status&severity=1010&image=cross-circle.png

    {
        "name": "down",
        "description": "A new status",
        "severity": 1010,
        "image": "/static/images/status/cross-circle.png",
        "url": "/statuses/down",
    }

### DELETE

Delete the given status

#### Example

> DELETE /statuses/{name}

    {
        "name": "down",
        "description": "A new status",
        "severity": 1010,
        "image": "/static/images/status/cross-circle.png",
        "url": "/statuses/down",
    }

### PUT 

Not supported

## /status-images

### GET

Returns a list of status images.

#### Example

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
