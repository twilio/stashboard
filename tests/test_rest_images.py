from test_api import StashboardTest

class ImageTest(StashboardTest):

    def test_wrong_version(self):
        response = self.get("/api/foo/status-images")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_images(self):
        response = self.get("/api/v1/status-images")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")



