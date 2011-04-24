from google.appengine.api import users
from handlers import site

def default_template_data():
    td = site.default_template_data()
    td["title"] = td["title"] + " Admin"
    return td

class RootHandler(site.BaseHandler):

    def get(self):
        self.redirect("/admin/site")

class SiteHandler(site.BaseHandler):

    def get(self):
        self.render(default_template_data(), 'index.html')

class SetupHandler(site.BaseHandler):

    def get(self):
        self.render(default_template_data(), 'admin/setup.html')

    def post(self):
        Status.install_defaults()
        self.redirect("/admin/site")


