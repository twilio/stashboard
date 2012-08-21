from google.appengine.ext import testbed
import models
from test_api import StashboardTest

class PublicEventsTest(StashboardTest):

    def setUp(self):
        super(PublicEventsTest, self).setUp()
        service = models.Service(name="Foo", slug="foo", description="Hello")
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

    def setUp(self):
        super(EventInstanceTest, self).setUp()
        service = models.Service(name="Foo", slug="foo", description="Hello")
        service.put()

        self.status = models.Status(name="Up", slug="up", default=True,
            description="bar", image="cross-circle")
        self.status.put()

        self.event = models.Event(service=service, status=self.status,
                message="Foo")
        self.event.put()

    def test_current_get_wrong_service(self):
        response = self.get("/admin/api/v1/services/bar/events/current")
        self.assertEquals(response.status_code, 404)

    def test_current_get_wrong_version(self):
        response = self.get("/admin/api/foo/services/foo/events/current")
        self.assertEquals(response.status_code, 404)

    def test_delete_wrong_service(self):
        response = self.delete("/admin/api/v1/services/bar/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_delete_wrong_sid(self):
        response = self.delete("/admin/api/v1/services/foo/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_delete_wrong_version(self):
        response = self.delete("/admin/api/foo/services/foo/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_service(self):
        response = self.get("/admin/api/v1/services/bar/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_sid(self):
        response = self.get("/admin/api/v1/services/foo/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_version(self):
        response = self.get("/admin/api/foo/services/foo/events/foo")
        self.assertEquals(response.status_code, 404)

    def test_get_current_event(self):
        url = "/admin/api/v1/services/foo/events/current"
        response = self.get(url)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

    def test_delete_wrong_event(self):
        service = models.Service(name="Bar", slug="bar", description="Hello")
        service.put()

        event = models.Event(service=service, status=self.status, message="foo")
        event.put()

        url = "/admin/api/v1/services/foo/events/%s" % event.key()
        response = self.delete(url)
        self.assertEquals(response.status_code, 404)

    def test_get_wrong_event(self):
        service = models.Service(name="Bar", slug="bar", description="Hello")
        service.put()

        event = models.Event(service=service, status=self.status, message="foo")
        event.put()

        url = "/admin/api/v1/services/foo/events/%s" % event.key()
        response = self.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_event(self):
        url = "/admin/api/v1/services/foo/events/%s" % self.event.key()
        response = self.get(url)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)

    def test_put_not_supported(self):
        response = self.put("/admin/api/foo/services/foo/events/foo")
        self.assertEquals(response.status_code, 405)

    def test_post_wrong_version(self):
        response = self.post("/admin/api/foo/services/foo/events/foo")
        self.assertEquals(response.status_code, 405)

    def test_delete_event(self):
        url = "/admin/api/v1/services/foo/events/%s" % self.event.key()
        response = self.delete(url)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        self.assertEquals(response.status_code, 200)


class EventListTest(StashboardTest):

    def setUp(self):
        super(EventListTest, self).setUp()
        service = models.Service(name="Foo", slug="foo", description="Hello")
        service.put()
        status = models.Status(name="Up", slug="up", default=True,
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

    def test_post_with_twitter(self):
        response = self.post("/admin/api/v1/services/foo/events",
            data={"message": "hello", "status": "up", "tweet": "on"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        queue_tasks = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME).GetTasks('default')

        # Assert that we have the Twitter task in the queue
        queue_endpoints = [task['url'] for task in queue_tasks]
        self.assertTrue('/admin/tweet' in queue_endpoints)

        response = self.post("/admin/api/v1/services/foo/events",
            data={"message": "hello", "status": "up", "tweet": "checked"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        queue_tasks = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME).GetTasks('default')

        # Assert that we have two Twitter tasks lined up.
        queue_endpoints = [task['url'] for task in queue_tasks]
        self.assertEquals(queue_endpoints.count('/admin/tweet'), 2)


    def test_post_without_twitter(self):
        response = self.post("/admin/api/v1/services/foo/events",
            data={"message": "hello", "status": "up", "tweet": ""})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")
        queue_tasks = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME).GetTasks('default')

        # Assert that we have no Twitter tasks lined up.
        queue_endpoints = [task['url'] for task in queue_tasks]
        self.assertTrue('/admin/tweet' not in queue_endpoints)

