import json
from stashboard.models import Status, Image
from test_api import StashboardTest

class PublicStatusesTest(StashboardTest):

    def test_get(self):
        response = self.get("/api/v1/statuses")
        self.assertEquals(response.status_code, 200)

    def test_post(self):
        response = self.post("/api/v1/statuses")
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        response = self.delete("/api/v1/statuses")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        response = self.put("/api/v1/statuses")
        self.assertEquals(response.status_code, 405)


class StatusInstanceTest(StashboardTest):

    def setUp(self):
        super(StatusInstanceTest, self).setUp()
        image = Image(icon_set="fugue", slug="cross-circle",
                      path="fugue/cross-circle.png")
        image.put()
        status = Status(name="Foo", slug="foo", description="bar", 
            image="cross-circle")
        status.put()

    def test_get_wrong_status(self):
        response = self.get("/api/v1/statuses/bat")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_status(self):
        response = self.get("/api/v1/statuses/foo")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_wrong_version(self):
        response = self.get("/api/hey/statuses/foo")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")


class StatusesTest(StashboardTest):

    def setUp(self):
        super(StatusesTest, self).setUp()
        image = Image(icon_set="fugue", slug="cross-circle",
                      path="fugue/cross-circle.png")
        image.put()

    def test_statuses_list_version(self):
        """Services should return a 404 when no using v1"""
        response = self.get("/api/hey/statuses")
        self.assertEquals(response.status_code, 404)


    def test_get_statuses_list(self):
        """Services should return a 200 with the proper content type"""
        response = self.get("/api/v1/statuses")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_create_service_name(self):
        """Services should 201 """
        response = self.post("/admin/api/v1/statuses",
                             data={"description": "An example status",
                                   "name": "Some Random Name",
                                   "image": "cross-circle",
                                   "level": "ERROR",
                                   "default": "true"})
        status = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(status["name"], "Some Random Name")
        self.assertEquals(status["description"], "An example status")
        self.assertEquals(status["level"], "NORMAL")

    def test_wrong_default_data(self):
        """Services should 400 because the default value isn't supported"""
        response = self.post("/admin/api/v1/statuses",
                             data={"default": "foo"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_wrong_version(self):
        """Services should 404 with the wrong version"""
        response = self.post("/admin/api/hey/statuses",
                             data={"description": "An example service API"})
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")


    def test_missing_service_name(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/statuses",
                             data={"description": "An example service API"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_description(self):
        """Services should 400 without a description"""
        response = self.post("/admin/api/v1/statuses",
                                  data={"name": "Some Random Name"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_service_data(self):
        """Creating a service should 400 without data"""
        response = self.post("/admin/api/v1/statuses")
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_delete(self):
        "should return 405 Method Not Allowed"
        response = self.delete("/admin/api/v1/statuses")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put(self):
        """Should return 405 Content Length Required"""
        response = self.put("/admin/api/v1/statuses")
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_put_with_data(self):
        """should return 405 Method Not Allowed"""
        response = self.put("/admin/api/v1/statuses",
                            data={"description": "An example service API"})
        self.assertEquals(response.status_code, 405)
        self.assertEquals(response.headers["Content-Type"], "application/json")


