## Overview

Hello, and welcome to StashBoard, the open-source status dashboard. StashBoard's REST API allows users to programmatically update and manage web service status.

This document will only cover the basics of the StashBoard. See the [REST API section](/documentation/rest) for full documentation.

### Basics

The StashBoard REST API is broken down into three resources: Services, Events, and Statuses. 

#### Services

Services are the basic unit of StashBoard. A service is any web service that can be consumed, and more importantly, can fail. Using StashBoard, you can easily inform your users of the current service status. To handle system status, StashBoard uses the concept of events.

Read more about creating and modifying services in the [Status Resource section](/documentation/rest#status-list-resource) of the REST API documentation.

#### Events

A service has a list of events, listed in reverse chronological order, which represent the state of that service. To track the state of a web service, an administrator creates events for a given service.

For example, if a service is currently down, create an event with a "DOWN" status, explaining why the service isn't working. Once the service is up again, simply create a new event with an attached "UP" status. 

Read more about creating and modifying events in the [Events Resource section](/documentation/rest#events-list-resource) of the REST API documentation.

#### Statuses

A status represents the state of a web service. Instead of being directly attached to services, a status is attached to a service event (described above). Therefore, the current system status is simply the status attached to the most recent event. 

Read more about creating and modifying statuses in the [Status Resource section](/documentation/rest#status-list-resource) of the REST API documentation.

### Authentication

To access information through the REST API, no authentication is required. However, to change any information via the REST API (POST/PUT/DELETE), authentication and SSL are required.

StashBoard uses OAuth for authentication purposes. To authenticate your account and obtain your API keys, head over to the [API Credentials section](/documentation/credentials). 



