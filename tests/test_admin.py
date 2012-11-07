from base import TestbedTest
from models import InternalEvent
from handlers import admin


class AdminTest(TestbedTest):

    def test_no_setup(self):
        self.assertFalse(admin.setup_occurred())

    def test_finished_setup(self):
        admin.finish_setup()
        self.assertTrue(admin.setup_occurred())
