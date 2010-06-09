The REST API always returns a JSON object. A list resources is represented as a object with a "data" attribute

    {
        "data": ["List", "of", "objects"]
    }
    
No authentication is needed to access resources via GET; however, all other methods require authentication
    
## Base URL

All URLs referenced in this document have the following base:

    http[s]://ismywebservicedown.appspot.com/api/v1
    
This includes urls included in the sample JSON responses

## /services

### GET

Returns a list of services

> GET /services HTTP/1.1

    {
        "data": [
            {
                "name": "Example Foo",
                "id": "example-foo",
                "description": "An explanation of this service"
                "url": "/services/example-foo",
            },
            {
                "name": "Example Bar",
                "id": "example-bar",
                "description": "An explanation of this service"
                "url": "/services/example-bar",
            }
        ]
    }
    
### POST

Create a new service (or updates an existing server) and returns the new service object. 

#### Parameters

* **name**: Name of the service
* **description**: Description of service

> POST /services HTTP/1.1
name=New%20Service&description=A%20great%20service

    {
        "name": "New Service",
        "id": "new-service",
        "description": "A great service"
        "url": "/services/new-service",
    }


## /services/{service}

### GET

Returns a service instance

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

> POST /services/{service} description=System%20is%20now%20operational

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System% is now operational",
        "url": "/services/example-service",
    }

### DELETE

Delete a service, returns the service object deleted

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

> GET /services/{service}/events HTTP/1.1

    {
        "data": [
            {
                "timestamp": "2010-05-22T01:52:23.104012", 
                "message": "Problem fixed", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM",
                "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM",
                "status": "/statuses/up"
            }, 
            {
                "timestamp": "2010-05-22T01:52:16.383246", 
                "message": "Might be up", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
                "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
                "status": "/statuses/intermittent"
            }
        ]
    }

### POST

#### Parameters

* **status**: An valid system status. See /statuses
* **message**: A message for the event

Will return the newly created status

> POST /services/{service}/events  HTTP/1.1 status=AVAILABLE&message=System%20is%20now%20operational

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": "/statuses/intermittent"
    }
    
### PUT

Not supported

### DELETE

Not supported
    
## /services/{service}/events/current

### GET

Returns the current service status

> GET /services/{service}/events/current HTTP/1.1

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": "/statuses/intermittent"
    }

### POST / PUT

Not supported

### DELETE

Not supported


## /services/{service}/events/{sid}

Returns the status with the given sid

### GET

> GET /services/{service}/events/{sid}

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": "/statuses/intermittent"
    }
    
### POST / PUT

Not supported

### DELETE

#### Parameters

Deletes the given event. Returns the deleted event

> DELETE /services/{service}/events/{sid} HTTP/1.1

    {
        "timestamp": "2010-05-22T01:52:16.383246", 
        "message": "Might be up", 
        "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "url": "/services/example-service/events/ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M",
        "status": "/statuses/intermittent"
    }


## /statuses

### GET

Returns the possible states

> GET /statuses HTTP/1.1

    {
        "data": [
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

> POST /statuses HTTP/1.1
name=down&description=A%20new%20status&severity=1000&image=cross-circle.png

    {
        "name": "down",
        "description": "A new status",
        "severity": 1000,
        "image": "/static/images/status/cross-circle.png",
        "url": "/statuses/down",
    }

### DELETE

Not Supported

### PUT

Not Supported

## /statuses/{name}

### GET

Return a status

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
