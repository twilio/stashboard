# Is My Web Service Down Rest API

Rest API always returns a JSON object. A list resources is represented as a object with a "data" attribute

    {
        "data": ["List", "of", "objects"]
    }

## /services/

### GET

Returns a list of services

> GET /services/

    {
        "data": [
            {
                "name": "Example Foo",
                "id": "example-foo",
                "description": "An explanation of this service"
            },
            {
                "name": "Example Bar",
                "id": "example-bar",
                "description": "An explanation of this service"
            }
        ]
    }
    
### POST

Create a new service (or updates an existing server) and returns the new service object

#### Parameters

* **name**: Name of the service
* **description**: Description of service

## /services/{service}/

### GET

Returns a service instance

> GET /services/{service}/

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "An explanation of what this service represents"
    }
    
### POST

Update a service's description. Returns the updated object

> POST /services/{service}/ description=System%20is%20now%20operational

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System% is now operational"
    }

### DELETE

Delete a service, returns the service object deleted

> DELETE /services/{service}/

    {
        "name": "Example Service",
        "id": "example-service",
        "description": "System% is now operational"
    }

## /services/{service}/events/

### GET

Returns all events associated with a given service, ordered by reverse chronological order. 

> GET /services/{service}/events/

    {
        "data": [
            {
                "status": {
                    "image": "/static/images/status/tick-circle.png",       
                    "description": "This service is up and running",            
                    "severity": "1", 
                    "name": "up"
                }, 
                "timestamp": "2010-05-22T01:52:23.104012", 
                "message": "Problem fixed", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GBAM"
            }, 
            {
                "status": {
                    "image": "/static/images/status/exclamation.png", 
                    "description": "The service is currently         experiencing intermittent problems", 
                    "severity": "10", 
                    "name": "intermittent"
                }, 
                "timestamp": "2010-05-22T01:52:16.383246", 
                "message": "Might be up", 
                "sid": "ahJpc215d2Vic2VydmljZWRvd25yCwsSBUV2ZW50GA8M"
            }
        ]
    }

### POST

#### Parameters

* **status**: An valid system state. See /states
* **message**: Optional. Will create a message at the same time

Will return the newly created status

> POST /services/{service}/events/ status=AVAILABLE&message=System%20is%20now%20operational

    {
        "sid": "908903jkdjf92349asdf",
        "start": "2010-03-11 20:00:00Z",
        "end": "2010-03-11 20:50:34Z",
        "duration": "00:50:34",
        "status": "AVAILABLE"
    }
    
## /statuses/current/


### GET

Returns the current system status

> GET /services/{service}/events/current/

    {
        "sid": "908903jkdjf92349asdf",
        "start": "2010-03-11 20:00:00Z",
        "end": "2010-03-11 20:50:34Z",
        "duration": "00:50:34",
        "status": "AVAILABLE"
    }

### POST / PUT

Not supported

### DELETE

Not supported


## /services/{service}/events/{sid}/

Returns the status with the given sid

## GET

> GET /services/{service}/events/{sid}/
    {
        "sid": "908903jkdjf92349asdf",
        "start": "2010-03-11 20:00:00Z",
        "end": "2010-03-11 20:50:34Z",
        "duration": "00:50:34",
        "status": "AVAILABLE"
    }
    
## POST

Not supported


## DELETE

#### Parameters

Deletes the given status

> DELETE /services/{service}/events/{sid}/

TODO What should I return here? StatusResponse?

## /services/{service}/messages/

### GET

    [
        {
            "sid": "j829kadjfa98j32adf",
            "message": "The server is down due to matience",
            "date": "2010-03-11 20:50:34Z"
            "status": {
                "sid": "908903jkdjf92349asdf",
                "url": "http://status.example.com/status/908903jkdjf92349asdf"
            }
        }
    ]
    
### POST

#### Parameters
* **message**: Text of a new message

Returns the new message 

    {
        "sid": "j829kadjfa98j32adf",
        "message": "The server is down due to matience",
        "date": "2010-03-11 20:50:34Z"
        "status": {
            "sid": "908903jkdjf92349asdf",
            "url": "http://status.example.com/status/908903jkdjf92349asdf"
        }
    }
    
### Delete

Not supported

### PUT 

Not supported

## /services/{service}/messages/{sid}/

### GET

    {
        "sid": "j829kadjfa98j32adf",
        "message": "The server is down due to matience",
        "date": "2010-03-11 20:50:34Z"
        "status": {
            "sid": "908903jkdjf92349asdf",
            "url": "http://status.example.com/status/908903jkdjf92349asdf"
        }
    }
    
### POST

Edit the body of a message

#### Parameters
* **message**: Body of the new message

TODO Should we be able to update the times as well?

## /services/{service}/statuses/

### GET

Returns the possible states

> GET /services/{service}/statuses/

    [
        {
            "name": "AVAILABLE",
            "description": "An explanation of what this state represents"
        },
        {
            "name": "DOWN",
            "description": "An explanation of what this state represents"
        },
        {
            "name": "INTERMITTENT",
            "description": "An explanation of what this state represents"
        }
    ]
    
### POST

#### Parameters
* **text**: The type of the new status
* **description**: The explanation of the status

### DELETE

Not Supported

### PUT

Not Supported

## /services/{service}/statuses/{name}/

### GET

return the state

    {
        "name": "INTERMITTENT",
        "description": "An explanation of what this state represents"
    }
    
### POST
* **description**: The new description of the task

Returns the newly updated state

> POST /services/{service}/statuses/{name}/ description=Newstuffhere

    {
        "name": "INTERMITTENT",
        "description": "Newstuffhere"
    }

### DELETE

> DELETE /services/{service}/statuses/{name}/

TODO What should it return?

### PUT 

Not supported
