from datetime import datetime
from datetime import date
from datetime import timedelta
from base import TestbedTest
from models import Event
from models import Service
from models import Status

class HistoryTest(TestbedTest):

    def setUp(self):
        super(HistoryTest, self).setUp()
        Status.load_defaults()
        self.service = Service(slug="account", name="Account",
                               description="The BEST SERVICE")
        self.service.put()

    def test_history_order(self):
        start = date(2011, 4, 13)
        up = Status.get_by_slug("up")
        history = self.service.history(5, up, start=start)
        self.assertEquals(len(history), 5)

        history_days = [ h["day"] for h in history ]
        expected = [
            date(2011, 4, 12),
            date(2011, 4, 11),
            date(2011, 4, 10),
            date(2011, 4, 9),
            date(2011, 4, 8),
            ]

        self.assertEquals(history_days, expected)

    def test_history_order_early_month(self):
        start = date(2011, 4, 2)
        up = Status.get_by_slug("up")
        history = self.service.history(5, up, start=start)

        history_days = [ h["day"] for h in history ]
        expected = [
            date(2011, 4, 1),
            date(2011, 3, 31),
            date(2011, 3, 30),
            date(2011, 3, 29),
            date(2011, 3, 28),
            ]

        self.assertEquals(history_days, expected)

        for h in history:
            self.assertFalse(h["information"])


    def test_history_order_late_month(self):
        start = date(2011, 4, 5)
        up = Status.get_by_slug("up")
        history = self.service.history(5, up, start=start)

        history_days = [ h["day"] for h in history ]
        expected = [
            date(2011, 4, 4),
            date(2011, 4, 3),
            date(2011, 4, 2),
            date(2011, 4, 1),
            date(2011, 3, 31),
            ]

        self.assertEquals(history_days, expected)

    def test_history_no_errors_boundary(self):
        down = Status.get_by_slug("down")
        up = Status.get_by_slug("up")

        now = datetime(2011, 4, 5)
        event = Event(status=down, service=self.service, start=now, message="HEY")
        event.put()

        history = self.service.history(5, up, start=date(2011, 4, 5))
        self.assertEquals(history[0]["information"], False)

    def test_history_one_error(self):
        down = Status.get_by_slug("down")
        up = Status.get_by_slug("up")

        now = datetime(2011, 4, 4, 12)
        event = Event(status=down, service=self.service, start=now, message="HEY")
        event.put()

        history = self.service.history(5, up, start=date(2011, 4, 5))

        self.assertEquals(history[0]["information"], True)
        self.assertEquals(history[0]["name"], "information")

    def test_history_one_error_boundary(self):
        down = Status.get_by_slug("down")
        up = Status.get_by_slug("up")

        now = datetime(2011, 3, 31)
        event = Event(status=down, service=self.service, start=now, message="HEY")
        event.put()

        history = self.service.history(5, up, start=date(2011, 4, 5))

        self.assertEquals(history[4]["information"], True)
        self.assertEquals(history[4]["name"], "information")

    def test_history_count(self):
        up = Status.get_by_slug("up")
        history = self.service.history(10, up, start=date(2011, 4, 5))
        self.assertEquals(len(history), 10)

    def test_history_current_status(self):
        down = Status.get_by_slug("down")
        up = Status.get_by_slug("up")

        now = datetime(2011, 4, 4, 12, 51)
        event = Event(status=down, service=self.service, start=now, message="HEY")
        event.put()

        history, = self.service.history(1, up, start=date(2011, 4, 5))

        self.assertEquals(history["information"], True)

