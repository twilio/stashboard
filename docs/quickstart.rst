Getting Started
=================

Running Locally
----------------

Download and install the `App Engine SDK for Python
<http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python>`_.

You'll then need to checkout the Stashboard repository.

.. code-block:: bash

    git clone git://github.com/twilio/stashboard.git`

Open the SDK, choose ``File > Add Existing Application...`` and select the
``stashboard`` folder inside the cloned repository. Then click the green "Run"
button to start the application.

Visit http://localhost:8080/admin/setup to complete the installation.

Customzing
-------------

Open the ``settings.py`` file and change the ``SITE_NAME``, ``SITE_URL``, and
``REPORT_URL`` options to the desired values.

If you're planning on authenicating using the REST API, you need to `register
your application with Google <https://accounts.google.com/ManageDomains>`_ to
get your ``CONSUMER_KEY`` and ``CONSUMER_SECRET`` values.

Configuring Twitter Updates
---------------------------

To configure posting to Twitter, you must create an application and
follow the `instructions for generating access tokens for a single
user <https://dev.twitter.com/docs/auth/tokens-devtwittercom>`_.

1. Create a Twitter account for posting status messages.
2. Log into `dev.twitter.com <http://dev.twitter.com>`_ with the
   account you want to use for posting statuses.
3. Create an application with Read and Write permissions.
4. Visit your application's page and create an access token.
5. Update ``settings.py`` with your Twitter username, consumer key, consumer
   secret, access token, and access token secret.

Deploying
-------------

Before you can deploy to Appspot, you'll need to `create an application on App
Engine <https://appengine.google.com/start/createapp>`_. Once you've done that,
update the ``app.yaml`` with your application id.

Hit the "Deploy" button, wait a couple of seconds, and then naviagate to
``http://{application}.appspot.com`` to enjoy your new status dashboard.
