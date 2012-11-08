try:
    import json
except ImportError:
    import simplejson as json

from models import Status, Image
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
        self.status = Status(name="Foo", slug="foo", description="bar", 
            image="cross-circle")
        self.status.put()

    def test_update_wrong_image(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"image": "foobar"})
        self.assertEquals(response.status_code, 400)

    def test_update_default_false(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"default": "false"})
        self.assertEquals(response.status_code, 200)

        status = Status.get(self.status.key())
        self.assertFalse(status.default)

    def test_update_default(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"default": "true"})
        self.assertEquals(response.status_code, 200)

        status = Status.get(self.status.key())
        self.assertTrue(status.default)

    def test_update_image(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"image": "cross-circle"})
        self.assertEquals(response.status_code, 200)

        status = Status.get(self.status.key())
        self.assertEquals(status.image, "fugue/cross-circle.png")

    def test_update_description(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"description": "blah"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

        status = Status.get(self.status.key())
        self.assertEquals(status.description, "blah")

    def test_update_name(self):
        response = self.post("/admin/api/v1/statuses/foo",
            data={"name": "Foobar"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

        status = Status.get(self.status.key())
        self.assertEquals(status.name, "Foobar")

    def test_get_wrong_status(self):
        response = self.get("/api/v1/statuses/bat")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_status(self):
        response = self.get("/api/v1/statuses/foo")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_url_api_correct(self):
        response = self.get("/admin/api/v1/statuses/foo")
        data = json.loads(response.content)
        self.assertEquals(data['url'], 'http://localhost:80/admin/api/v1/statuses/foo')

    def test_url_admin_api_correct(self):
        response = self.get("/api/v1/statuses/foo")
        data = json.loads(response.content)
        self.assertEquals(data['url'], 'http://localhost:80/api/v1/statuses/foo')
 
    def test_delete_success(self):
        response = self.delete("/admin/api/v1/statuses/foo")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

        data = json.loads(response.content)

        self.assertEquals(data['url'], 'http://localhost:80/admin/api/v1/statuses/foo')

        status = Status.get(self.status.key())
        self.assertEquals(status, None)

    def test_delete_no_slug(self):
        response = self.delete("/admin/api/v1/statuses/bar")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_delete_wrong_version(self):
        response = self.delete("/admin/api/hey/statuses/foo")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_no_slug(self):
        response = self.post("/admin/api/v1/statuses/bar")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_wrong_version(self):
        response = self.post("/admin/api/hey/statuses/foo")
        self.assertEquals(response.status_code, 404)
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

    def test_existing_status(self):
        """Services should 400 without a name"""
        status = Status(name="Foo", slug="foo", description="hello",
            image="cross-circle")
        status.put()

        response = self.post("/admin/api/v1/statuses",
                             data={"description": "An example service API",
                                   "name": "Foo", 
                                   "image": "cross-circle"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_wrong_image(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/statuses",
                             data={"description": "An example service API",
                                   "name": "Foo",
                                   "image": "foobar"})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_missing_image(self):
        """Services should 400 without a name"""
        response = self.post("/admin/api/v1/statuses",
                             data={"description": "An example service API",
                                   "name": "Foo"})
        self.assertEquals(response.status_code, 400)
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


