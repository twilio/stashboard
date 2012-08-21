# Stashboard

[![Build Status](https://secure.travis-ci.org/twilio/stashboard.png?branch=master)](http://travis-ci.org/twilio/stashboard)

Stashboard was written by Twilio to provide status information on our phone, SMS, and Communication APIs. We open sourced the code to provide a generic status page designed to be customized by any hosted services company to provide customers up-to-date status information. The code can be downloaded, customized with your logo, and run on any Google App Engine account.

## Installation

1. Download and install the [App Engine SDK for Python][appengine]
2. `git clone git://github.com/twilio/stashboard.git`
3. Add your application id to `app.yaml`
4. Open the SDK, choose `File > Add Existing Application...` and select the `stashboard` folder inside the cloned repository
5. Update the settings in `settings.py`
6. Visit http://your-app-id.appspot.com/admin/setup to complete the installation

From here you can either run Stashboard locally in the [App Engine development environment][local] or [deploy to Appspot][deploy].
See the [Getting Started](http://code.google.com/appengine/docs/python/gettingstarted) guide for a basic overview of the App Engine platform.

[local]: http://code.google.com/appengine/docs/python/gettingstarted/devenvironment.html
[deploy]: http://code.google.com/appengine/docs/python/gettingstarted/uploading.html
[appengine]: http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python

## Demo

The most recent version of Stashboard lives at http://stashboard.appspot.com

## Documentation

Full documentation can be found on [Read The Docs](http://readthedocs.org/docs/stashboard/en/latest)

## Community

All Stashboard development and discussion happens in the [Stashboard google group](https://groups.google.com/forum/#!forum/stashboard)

To keep up to date, you can follow [@stashboard](http://twitter.com/stashboard) on Twitter or join the [#stashboard](irc://irc.freenode.net/stashboard) channel on freenode

## Development

You'll need to install a couple more packages to hack on Stashboard
  
    pip install -r requirements.txt

To run the unit tests, 

    python tests/runner.py tests

## Future

The [roadmap](https://github.com/twilio/stashboard/wiki/Roadmap) details future plans for Stashboard.

## Acknowledgements
* Buttons by [Necolas](https://github.com/necolas/css3-github-buttons)
* Fugue icons by [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/)
* Iconic icons by [P.J. Onori](http://somerandomdude.com/projects/iconic/)
* OAuth support via [simplegeo/python-oauth2](https://github.com/simplegeo/python-oauth2)
