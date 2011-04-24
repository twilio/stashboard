from google.appengine.api import users
from handlers import site
from models import Service
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
            td["url"] = "/admin/services/" + slug
            td["button_text"] = "Edit"
            td["description"] = service.description
            td["name"] = service.name
            self.render(td, 'admin/services_create.html')
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
            "url": "/api/v1/services/" + slug,
            "description": service.description,
            "name": service.name,
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
            "url": "/api/v1/services/" + slug,
            "description": service.description,
            "name": service.name,
            "action": "edit",
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/services_create.html')


class CreateServiceHandler(site.BaseHandler):

    def get(self):
        td = {
            "services_selected": True,
            "url": "/api/v1/services",
            "action": "create",
            }

        td.update(site.default_template_data())
        self.render(td, 'admin/services_create.html')
