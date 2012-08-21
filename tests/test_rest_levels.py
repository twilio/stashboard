from models import Service
from test_api import StashboardTest

class LevelTest(StashboardTest):

    def test_wrong_version(self):
        response = self.get("/api/foo/levels")
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.headers["Content-Type"], "application/json")

    def test_get_levels(self):
        response = self.get("/api/v1/levels")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers["Content-Type"], "application/json")



