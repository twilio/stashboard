# Is My Web Service Down Rest API


## /services/

### GET

Returns a list of services

> GET /services/

    [
        {
            "name": "twiliophone",
            "description": "An explanation of what this service represents"
        },
        {
            "name": "twiliosms",
            "description": "An explanation of what this service represents"
        }
    ]
    
### POST

Create a new service

#### Parameters

* **name**: Name of new service
* **description**: Description of service

## /services/{service}/

### GET

Returns a service instance

> GET /services/{service}/

    {
        "name": "twiliophone",
        "description": "An explanation of what this service represents"
    }
    
### POST

Update a service's description

> POST /services/{service}/ description=System%20is%20now%20operational

    {
        "name": "twiliophone",
        "description": "An explanation of what this service represents"
    }

### DELETE

Delete a service, returns the service object deleted

> DELETE /services/{service}/

## /services/{service}/events/

### GET

Returns an array of status objects, ordering by reverse chronological order

TODO Add a link to the messages?

> GET /services/{service}/events/

    [
        {
            "sid": "908903jkdjf92349asdf",
            "start": "2010-03-11 20:00:00Z",
            "end": "2010-03-11 20:50:34Z",
            "duration": "00:50:34",
            "state": "AVAILABLE"
        },
        {
            "sid": "908903jkdjf92349asdf",
            "start": "2010-03-11 20:00:00Z",
            "end": "2010-03-11 20:50:34Z",
            "duration": "00:50:34",
            "state": "AVAILABLE"
        }
    ]

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
