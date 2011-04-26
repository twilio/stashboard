import logging
from google.appengine.api import users
from google.appengine.ext import db
from handlers import site
from models import Service, Status, Event, Level
from utils import slugify

def default_template_data():
    td = site.default_template_data()
    td["title"] = td["title"] + " Admin"
    return td

class RootHandler(site.BaseHandler):

    def get(self):
        self.redirect("/admin/services")

class SetupHandler(site.BaseHandler):

    def get(self):
        self.render(default_template_data(), 'admin/setup.html')

    def post(self):
        Status.install_defaults()
        self.redirect("/admin")

class ServiceHandler(site.BaseHandler):

    def get(self):
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
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/services_create.html')


class CreateServiceHandler(site.BaseHandler):

    def get(self):
        td = {
            "services_selected": True,
            "url": "/admin/api/v1/services",
            "action": "create",
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
            "description": status.description,
            "name": status.name,
            # "images": Images.all(),
            "levels": Level.all(),
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

class CreateServiceHandler(site.BaseHandler):

    def get(self):
        td = {
            "statuses_selected": True,
            "url": "/admin/api/v1/statuses",
            "action": "create",
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/statuses_create.html')

class StatusHandler(site.BaseHandler):

    def get(self):
        td = default_template_data()
        td["statuses_selected"] = True
        td["statuses"] = Status.all().order("name").fetch(1000)
        self.render(td, 'admin/status.html')

