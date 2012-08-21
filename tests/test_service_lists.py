try:
    import json
except ImportError:
    import simplejson as json

from mock import patch
from models import Service, List
from test_api import StashboardTest


class PublicServiceListsTest(StashboardTest):

    def test_get(self):
        response = self.get("/api/v1/service-lists")
        self.assertEquals(response.status_code, 200)

    def test_post(self):
        response = self.post("/api/v1/service-lists")
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        response = self.delete("/api/v1/service-lists")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        response = self.put("/api/v1/service-lists")
        self.assertEquals(response.status_code, 405)


class ServiceListInstanceTest(StashboardTest):

    def setUp(self):
        super(ServiceListInstanceTest, self).setUp()
        self.service_list = List(slug="foo", name="Foo", description="Bar")
        self.service_list.put()
        self.service = Service(list=self.service_list, name="Foo", slug="foo",
                               description="foo")
        self.service.put()

    def test_resource_url(self):
        service_list = List(slug="foo", name="Foo", description="Bar")
        self.assertEquals(service_list.resource_url(), "/service-lists/foo")

    def test_url(self):
        service_list = List(slug="foo", name="Foo", description="Bar")
        self.assertEquals(service_list.url(), "/service-lists/foo")

    def test_delete_wrong_service(self):
        response = self.delete("/admin/api/v1/service-lists/bar")
        self.assertEquals(response.status_code, 404)

    def test_delete_wrong_version(self):
        response = self.delete("/admin/api/foo/service-lists/foo")
        self.assertEquals(response.status_code, 404)

    def test_post_wrong_service(self):
        response = self.post("/admin/api/v1/service-lists/bar")
        self.assertEquals(response.status_code, 404)

    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/service-lists/foo")
        self.assertEquals(response.status_code, 404)

    def test_post_update_desc(self):
        response = self.post("/admin/api/v1/service-lists/foo",
                data={"description": "hello"})
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

        service = List.get(self.service_list.key())
        self.assertEquals(service.description, "hello")

    def test_post_update(self):
        response = self.post("/admin/api/v1/service-lists/foo",
                    data={"name": "bar"})
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

        service = List.get(self.service_list.key())
        self.assertEquals(service.name, "bar")

    def test_get_wrong_service(self):
        response = self.get("/admin/api/v1/service-lists/bar")
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_version(self):
        response = self.get("/admin/api/foo/service-lists/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_service_list(self):
        response = self.get("/admin/api/v1/service-lists/foo")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")


class ServiceListTest(StashboardTest):

    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/service-lists")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_wrong_version(self):
        response = self.get("/api/foo/service-lists")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_services_list(self):
        """Services should return a 200 with the proper content type"""
        response = self.get("/api/v1/service-lists")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_create_service_name(self):
        """Services should 201 """
        response = self.post("/admin/api/v1/service-lists",
                             data={"description": "An example service API",
                                   "name": "Some Random Name"})
        service = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(service["name"], "Some Random Name")
        self.assertEquals(service["description"], "An example service API")

    def test_missing_service_name(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/service-lists",
                             data={"description": "An exmple service API"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_description(self):
        """Services should 400 without a description"""
        response = self.post("/admin/api/v1/service-lists",
                                  data={"name": "Some Random Name"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_data(self):
        """Creating a service should 400 without data"""
        response = self.post("/admin/api/v1/service-lists")
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_delete(self):
        "should return 405 Method Not Allowed"
        response = self.delete("/admin/api/v1/service-lists")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put(self):
        """Should return 405 Content Length Required"""
        response = self.put("/admin/api/v1/service-lists")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put_with_data(self):
        """should return 405 Method Not Allowed"""
        response = self.put("/admin/api/v1/service-lists",
                            data={"description": "An example service API"})
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")


