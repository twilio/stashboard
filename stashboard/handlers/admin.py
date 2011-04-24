from google.appengine.api import users
from handlers import site
from models import Service

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
