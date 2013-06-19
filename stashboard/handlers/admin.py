import cgi
import logging
import oauth2 as oauth
import os
import migrations
from django.conf import settings
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from handlers import api
from handlers import site
from models import List, Service, Status, Event, Image, Profile, InternalEvent
from utils import slugify


import oauth2 as oauth
import socket
import urllib

def default_template_data():
    td = site.default_template_data()
    td["title"] = td["title"] + " Admin"
    return td


def setup_occurred():
    return InternalEvent.get_by_key_name("load_defaults") is not None


def finish_setup():
    assert InternalEvent.get_or_insert("load_defaults", name="load_defaults")


class RootHandler(site.BaseHandler):

    def get(self):
        self.redirect("/admin/services")


class SetupHandler(site.BaseHandler):

    def get(self):
        if setup_occurred():
            self.redirect("/admin")
        self.render(default_template_data(), 'admin/setup.html')

    def post(self):
        if not setup_occurred():
            Status.load_defaults()
            Image.load_defaults()
            api.invalidate_cache()
            finish_setup()
        self.redirect("/admin")


class SkipHandler(site.BaseHandler):

    def get(self):
        finish_setup()
        self.redirect("/admin")


class ServiceHandler(site.BaseHandler):

    def get(self):
        if not setup_occurred():
            self.redirect("/admin/setup")

        td = default_template_data()
        td["services_selected"] = True
        td["services"] = Service.all().order("name").fetch(1000)
        self.render(td, 'admin/services.html')


class ServiceInstanceHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if service:
            td = default_template_data()
            td["services_selected"] = True
            td["service"] = service
            td["events"] = service.events.order("-start").fetch(1000)
            self.render(td, 'admin/services_instance.html')
        else:
            self.not_found()


class DeleteServiceHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        td = {
            "services_selected": True,
            "url": "/admin/api/v1/services/" + slug,
            "description": service.description,
            "name": service.name,
            "slug": service.slug,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/services_delete.html')

class EditServiceHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        td = {
            "services_selected": True,
            "url": "/admin/api/v1/services/" + slug,
            "description": service.description,
            "slug": service.slug,
            "name": service.name,
            "action": "edit",
            "service_lists": List.all().fetch(100),
            }

        if service.list is not None:
            td["list"] = service.list.name
        else:
            td["list"] = ""

        td.update(site.default_template_data())
        self.render(td, 'admin/services_create.html')


class CreateServiceHandler(site.BaseHandler):

    def get(self):
        td = {
            "services_selected": True,
            "url": "/admin/api/v1/services",
            "action": "create",
            "service_lists": List.all().fetch(100),
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/services_create.html')


class UpdateStatusHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        td = {
            "services_selected": True,
            "service": service,
            "statuses": Status.all().fetch(100),
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/events_create.html')

class NoteHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        td = {
            "services_selected": True,
            "service": service,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/events_note.html')


class DeleteEventHandler(site.BaseHandler):

    def get(self, slug, key_str):
        service = Service.get_by_slug(slug)
        event = db.get(key_str)
        if not service or not isinstance(event, Event):
            self.not_found()
            return

        td = {
            "services_selected": True,
            "service": service,
            "event": event,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/events_delete.html')

class EditStatusHandler(site.BaseHandler):

    def get(self, slug):
        status = Status.get_by_slug(slug)
        if not status:
            self.not_found()
            return

        td = {
            "statuses_selected": True,
            "status": status,
            "action": "edit",
            "url": "/admin/api/v1/statuses/" + slug,
            "description": status.description,
            "name": status.name,
            "image_url": status.image,
            "images": Image.all().fetch(200),
            "default": status.default,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/status_edit.html')


class DeleteStatusHandler(site.BaseHandler):

    def get(self, slug):
        status = Status.get_by_slug(slug)
        if not status:
            self.not_found()
            return

        td = {
            "statuses_selected": True,
            "status": status,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/status_delete.html')


class StatusHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["statuses_selected"] = True
        td["statuses"] = Status.all().order("name").fetch(1000)
        self.render(td, 'admin/status.html')


class CreateStatusHandler(site.BaseHandler):

    def get(self):
        td = {
            "statuses_selected": True,
            "action": "create",
            "url": "/admin/api/v1/statuses",
            "images": Image.all().fetch(200),
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/status_create.html')


class EditListHandler(site.BaseHandler):

    def get(self, slug):
        list = List.get_by_slug(slug)
        if not list:
            self.not_found()
            return

        td = {
            "lists_selected": True,
            "list": list,
            "action": "edit",
            "url": "/admin/api/v1/service-lists/" + slug,
            "description": list.description,
            "name": list.name,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/list_edit.html')

class DeleteListHandler(site.BaseHandler):

    def get(self, slug):
        list = List.get_by_slug(slug)
        if not list:
            self.not_found()
            return

        td = {
            "listss_selected": True,
            "list": list,
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/list_delete.html')


class ListHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["lists_selected"] = True
        td["lists"] = List.all().order("name").fetch(1000)
        self.render(td, 'admin/list.html')

class CreateListHandler(site.BaseHandler):

    def get(self):
        td = {
            "lists_selected": True,
            "action": "create",
            "url": "/admin/api/v1/service-lists",
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/list_create.html')


class MigrationStarter(site.BaseHandler):

    def post(self, key):
        migration = migrations.find(key)
        migration().run()


class MigrationHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["migrations"] = migrations.all()
        self.render(td, "admin/migrations.html")

    def post(self):
        migration = self.request.get("migration", None)

        if migration is None:
            self.error(400)
            return

        taskqueue.add(url="/admin/migrations/%s" % migration)

        td = default_template_data()
        td["migrations"] = migrations.all()
        td["notice"] = "Migration %s started. Check the logs for output" % migration
        self.render(td, "admin/migrations.html")


class CredentialHandler(site.BaseHandler):

    def get(self):

        user = users.get_current_user()
        profile = Profile.all().filter('owner = ', user).get()

        td = default_template_data()
        td["credentials_selected"] = True
        td["consumer_key"] = settings.CONSUMER_KEY
        td["consumer_secret"] = settings.CONSUMER_SECRET

        if os.environ['SERVER_SOFTWARE'].startswith('Development'):
            td["authorized"] = True
            td["oauth_token"] = "ACCESS_TOKEN"
            td["oauth_token_secret"] = "ACCESS_TOKEN_SECRET"
        elif profile:
            td["authorized"] = True
            td["oauth_token"] = profile.token
            td["oauth_token_secret"] = profile.secret
        else:
            td["authorized"] = False

        self.render(td, 'admin/credentials.html')
        return


class OAuthRequestHandler(site.BaseHandler):

    def get(self):
        user = users.get_current_user()
        host = self.request.headers.get('host', 'nohost')
        consumer_key = settings.CONSUMER_KEY
        consumer_secret = settings.CONSUMER_SECRET

        callback = 'https://%s/admin/oauth/verify' % host
        request_token_url = ('https://%s/_ah/OAuthGetRequestToken?'
                             'oauth_callback=%s' % (host, callback))
        authorize_url = 'https://%s/_ah/OAuthAuthorizeToken' % host

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)

        resp, content = client.request(request_token_url, "GET")

        if resp['status'] != '200':
            self.error(400)
            self.response.out.write("Getting Request Token failed")
            return

        request_token = dict(cgi.parse_qsl(content))
        token = request_token['oauth_token_secret']

        if not memcache.set("oauth_token", token, namespace=user.email()):
            logging.error("Memcache set failed on oauth_token")

        oauth_url = ("%s?oauth_token=%s" %
                     (authorize_url, request_token['oauth_token']))

        self.redirect(oauth_url)


class OAuthVerifyHandler(site.BaseHandler):

    def get(self):
        oauth_token = self.request.get('oauth_token', default_value=None)
        oauth_verifier = self.request.get('oauth_verifier', default_value=None)
        user = users.get_current_user()
        request_secret = memcache.get("oauth_token", namespace=user.email())

        if not oauth_token or not oauth_verifier or not request_secret:
            self.error(400)
            self.response.out.write("Missing data")
            return

        host = self.request.headers.get('host', 'nohost')
        access_token_url = 'https://%s/_ah/OAuthGetAccessToken' % host

        consumer_key = settings.CONSUMER_KEY
        consumer_secret = settings.CONSUMER_SECRET
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        token = oauth.Token(oauth_token, request_secret)
        token.set_verifier(oauth_verifier)

        client = oauth.Client(consumer, token)

        resp, content = client.request(access_token_url, "POST")

        if resp['status'] != '200':
            self.error(400)
            logging.error("Authorization failed!")
            return

        access_token = dict(cgi.parse_qsl(content))

        profile = Profile(
            owner=user,
            token=access_token['oauth_token'],
            secret=access_token['oauth_token_secret']
            )
        profile.put()

        self.redirect("/admin/credentials")


class EventTweetHandler(webapp.RequestHandler):
    def post(self):
        if not (settings.TWITTER_CONSUMER_KEY and settings.TWITTER_CONSUMER_SECRET and \
                settings.TWITTER_ACCESS_TOKEN and settings.TWITTER_ACCESS_TOKEN_SECRET):
            logging.error('Twitter credentials not configured properly in settings.py')
            return

        service_name = self.request.get('service_name')
        status_name = self.request.get('status_name')
        message = self.request.get('message')

        if not service_name or not status_name or not message:
            logging.error('Internal Twitter endpoint not called correctly')
            return

        consumer = oauth.Consumer(key=settings.TWITTER_CONSUMER_KEY, secret=settings.TWITTER_CONSUMER_SECRET)
        token = oauth.Token(key=settings.TWITTER_ACCESS_TOKEN, secret=settings.TWITTER_ACCESS_TOKEN_SECRET)

        client = oauth.Client(consumer, token, timeout=10)

        try:
            resp, content = client.request(
                'http://api.twitter.com/1.1/statuses/update.json',
                method='POST',
                body=urllib.urlencode({'status': '[%s - %s] %s' % (service_name, status_name, message)})
            )
            if resp.status == 200:
                logging.info('Tweet successful: [%s - %s] %s' % (service_name, status_name, message))
            else:
                logging.error('Tweet failed: %s' % resp)
        except socket.timeout:
            logging.error('Unable to post to Twitter API.')


class InvalidateCacheHandler(site.BaseHandler):

    def get(self):
        api.invalidate_cache()
        self.response.out.write("Success")
