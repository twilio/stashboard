# Stashboard

## About

Stashboard was written by Twilio to provide status information on our phone, SMS, and Communication APIs. We open sourced the code and to provide a generic status page designed to be customized by any hosted services company to provide customers up-to-date status information. The code can be downloaded, customized with your logo, and run on any Google App Engine account.

## Installation

First, install the App Engine SDK for Python.

Next, download and extract Stashboard to your computer.

### Run Locally

Open the SDK, choose File > Add Existing Application..., select the stashboard folder you downloaded above and choose a port. Press Run and navigate to http://localhost:{port} to see your Stashboard installation.

### Deploy to AppSpot

Before you can deploy Stashboard, you will need to create an application on App Engine.

Once your application is registered, open app.yaml in the Stashboard directory and change application-id to the name of your newly created application.

Hit the 'Deploy' button, wait a couple of seconds, and then naviagate to http://{app-name}.appspot.com to enjoy your new status dashboard

## Basic View

By default, Stashboard exposes a rich client, utilizing AJAX and jQuery.

## REST API

Full documentation of the REST API can be found at <http://stashboard.appspot.com/documentation/rest>

## Community

All Stashboard development and discussion happens in the [Stashboard google group](https://groups.google.com/forum/#!forum/stashboard)

To keep up to date, you can follow [@stashboard](http://twitter.com/stashboard) on Twitter or join the [#stashboard](irc://irc.freenode.net/stashboard) channel on freenode

## Future

Future plans include RSS feeds, Web Hook integration, and a richer support for different status page views.

## Acknowledgements
* Buttons by [Necolas](https://github.com/necolas/css3-github-buttons)
* Fugue icons from [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/)
* Iconic icons from [P.J. Onori](http://somerandomdude.com/projects/iconic/)
