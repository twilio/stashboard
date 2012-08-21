try:
    import json
except ImportError:
    import simplejson as json

from mock import patch
from models import Service, List
from test_api import StashboardTest


class PublicServicesTest(StashboardTest):

    def test_get(self):
        response = self.get("/api/v1/services")
        self.assertEquals(response.status_code, 200)

    def test_post(self):
        response = self.post("/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        response = self.delete("/api/v1/services")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        response = self.put("/api/v1/services")
        self.assertEquals(response.status_code, 405)


class ServiceInstanceTest(StashboardTest):

    def setUp(self):
        super(ServiceInstanceTest, self).setUp()
        self.service_list = List(slug="foo", name="Foo", description="Bar")
        self.service_list.put()
        self.service = Service(name="Foo", slug="foo", description="foo")
        self.service.put()

    @patch("handlers.api.invalidate_cache")
    def test_delete_service(self, mock):
        response = self.delete("/admin/api/v1/services/foo")
        self.assertEquals(response.status_code, 200)

    def test_delete_wrong_service(self):
        response = self.delete("/admin/api/v1/services/bar")
        self.assertEquals(response.status_code, 404)

    def test_delete_wrong_version(self):
        response = self.delete("/admin/api/foo/services/foo")
        self.assertEquals(response.status_code, 404)

    def test_post_wrong_service(self):
        response = self.post("/admin/api/v1/services/bar")
        self.assertEquals(response.status_code, 404)

    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/services/foo")
        self.assertEquals(response.status_code, 404)

    def test_post_update_list(self):
        response = self.post("/admin/api/v1/services/foo",
                data={"list": "foo"})

        print response.content

        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

        service = Service.get(self.service.key())
        self.assertEquals(service.list.name, "Foo")
        
    def test_post_update_desc(self):
        response = self.post("/admin/api/v1/services/foo",
                data={"description": "hello"})
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

        service = Service.get(self.service.key())
        self.assertEquals(service.description, "hello")

    def test_post_update(self):
        response = self.post("/admin/api/v1/services/foo",
            data={"name": "bar"})
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

        service = Service.get(self.service.key())
        self.assertEquals(service.name, "bar")

    def test_get_wrong_service(self):
        response = self.get("/admin/api/v1/services/bar")
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_version(self):
        response = self.get("/admin/api/foo/services/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_service(self):
        response = self.get("/admin/api/v1/services/foo")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")


class ServicesTest(StashboardTest):

    def setUp(self):
        super(ServicesTest, self).setUp()
        self.service_list = List(slug="foo", name="Foo", description="Bar")
        self.service_list.put()
 
    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/services")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_wrong_version(self):
        response = self.get("/api/foo/services")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_services_list(self):
        """Services should return a 200 with the proper content type"""
        response = self.get("/api/v1/services")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_create_service_bad_list(self):
        """Services should 201 """
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API",
                                   "name": "Some Random Name",
                                   "list": "bar"})
        service = json.loads(response.content)
        self.assertEquals(response.status_code, 400)

    def test_create_service_list(self):
        """Services should 201 """
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API",
                                   "name": "Some Random Name",
                                   "list": "foo"})
        service = json.loads(response.content)
        self.assertEquals(response.status_code, 201)

    def test_create_service_name(self):
        """Services should 201 """
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API",
                                   "name": "Some Random Name"})
        service = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(service["name"], "Some Random Name")
        self.assertEquals(service["description"], "An example service API")

    def test_missing_service_name(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/services",
                             data={"description": "An example service API"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_description(self):
        """Services should 400 without a description"""
        response = self.post("/admin/api/v1/services",
                                  data={"name": "Some Random Name"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_data(self):
        """Creating a service should 400 without data"""
        response = self.post("/admin/api/v1/services")
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_delete(self):
        "should return 405 Method Not Allowed"
        response = self.delete("/admin/api/v1/services")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put(self):
        """Should return 405 Content Length Required"""
        response = self.put("/admin/api/v1/services")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put_with_data(self):
        """should return 405 Method Not Allowed"""
        response = self.put("/admin/api/v1/services",
                            data={"description": "An example service API"})
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")


