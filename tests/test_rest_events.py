import json
from stashboard.models import Status, Image, Event, Service
from test_api import StashboardTest

class PublicEventsTest(StashboardTest):

    def setUp(self):
        super(PublicEventsTest, self).setUp()
        service = Service(name="Foo", slug="foo", description="Hello")
        service.put()

    def test_get(self):
        response = self.get("/api/v1/services/foo/events")
        self.assertEquals(response.status_code, 200)

    def test_post(self):
        response = self.post("/api/v1/services/foo/events")
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        response = self.delete("/api/v1/services/foo/events")
        self.assertEquals(response.status_code, 405)

    def test_put(self):
        response = self.put("/api/v1/services/foo/events")
        self.assertEquals(response.status_code, 405)


class EventInstanceTest(StashboardTest):
    pass


class EventListTest(StashboardTest):

    def setUp(self):
        super(EventListTest, self).setUp()
        service = Service(name="Foo", slug="foo", description="Hello")
        service.put()
        status = Status(name="Up", slug="up", default=True,
            description="bar", image="cross-circle")
        status.put()

    def test_post_with_status(self):
        response = self.post("/admin/api/v1/services/foo/events", 
            data={"message": "hello", "status": "up"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_success(self):
        response = self.post("/admin/api/v1/services/foo/events", 
            data={"message": "hello"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_no_message(self):
        response = self.post("/admin/api/v1/services/foo/events")
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_wrong_service(self):
        response = self.post("/admin/api/v1/services/foobar/events",
            data={"message": "bat"})
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_wrong_service(self):
        response = self.get("/api/v1/services/foobar/events")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/services/foo/events")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_wrong_version(self):
        response = self.get("/api/foo/services/foo/events")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")



