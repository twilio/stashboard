from base import TestbedTest
from models import Status


class StatusTest(TestbedTest):

    def test_status_normal(self):
        s = Status(name=u"Hey", slug=u"hey", description=u"runaway",
                   image=u"helloworld.png", severity=10)
        s.put()

        data = s.rest("/api")
        self.assertEquals(data["level"], "NORMAL")

    def test_status_warning(self):
        s = Status(name=u"Hey", slug=u"hey", description=u"runaway",
                   image=u"helloworld.png", severity=30)
        s.put()

        data = s.rest("/api")
        self.assertEquals(data["level"], "WARNING")

    def test_status_error(self):
        s = Status(name=u"Hey", slug=u"hey", description=u"runaway",
                   image=u"helloworld.png", severity=40)
        s.put()

        data = s.rest("/api")
        self.assertEquals(data["level"], "ERROR")

    def test_status_critical(self):
        s = Status(name=u"Hey", slug=u"hey", description=u"runaway",
                   image=u"helloworld.png", severity=50)
        s.put()

        data = s.rest("/api")
        self.assertEquals(data["level"], "CRITICAL")
