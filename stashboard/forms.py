from models import Service
from utils import slugify
from handlers import site

class Form(object):
    pass

        # form = ServiceForm()
        # if form.validate():
        #     s = form.create()
        #     self.redirect("/admin/services")
        # else:
        #     self.error(400)
        #     self.render(form.td(), form.template)o


class ServiceForm(object):

    template = 'admin/services_create.html'

    def __init__(self, request, instance=None):
        self.request = request
        self.error = None
        self.instance = instance

        if instance:
            self.description = instance.description
            self.name = instance.name
            self.slug = instance.slug
        else:
            self.description = ""
            self.name = ""

    def validate(self):
        # Clean this function up
        self.name = self.request.get('name', default_value=self.name)
        self.description = self.request.get('description',
                                            default_value=self.description)

        # Return False if the data is wrong
        if not self.name and not self.description:
            self.error = "Name and description are required"
            return False

        if self.instance:
            return True

        self.slug = slugify.slugify(self.name)
        if Service.get_by_slug(self.slug):
            self.error = "A service with that name already exists"
            return False

        return True

    def create(self):
        s = Service(name=self.name, slug=self.slug,
                    description=self.description)
        s.put()
        return s

    def edit(self):
        self.instance.name = self.name
        self.instance.description = self.description
        self.instance.put()

    def td(self, mode):
        td = site.default_template_data()
        td["services_selected"] = True
        if mode == "edit":
            td["url"] = "/admin/services/" + self.slug
            td["button_text"] = "Edit"
        else:
            td["url"] = "/admin/services"
            td["button_text"] = "Create"

        td["description"] = self.description
        td["name"] = self.name
        td["error"] = self.error
        return td
