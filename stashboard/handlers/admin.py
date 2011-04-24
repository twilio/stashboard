from google.appengine.api import users
from handlers import site
from models import Service
from utils import slugify
from forms import ServiceForm

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
        td["services"] = Service.all().fetch(1000)
        self.render(td, 'admin/services.html')

    def post(self):
        form = ServiceForm(self.request)
        if form.validate():
            s = form.create()
            self.redirect("/admin/services/" + s.slug)
        else:
            self.error(400)
            self.render(form.td("create"), form.template)


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

    def post(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        form = ServiceForm(self.request, instance=service)
        if form.validate():
            form.edit()
            self.redirect("/admin/services/" + service.slug)
        else:
            self.error(400)
            self.render(form.td("edit"), form.template)


class EditServiceHandler(site.BaseHandler):

    def get(self, slug):
        service = Service.get_by_slug(slug)
        if not service:
            self.not_found()
            return

        form = ServiceForm(self.request, instance=service)
        self.render(form.td("edit"), form.template)


class CreateServiceHandler(site.BaseHandler):

    def get(self):
        form = ServiceForm(self.request)
        self.render(form.td("create"), form.template)
