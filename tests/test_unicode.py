# -*- coding: utf-8 -*-
from base import TestbedTest
from models import Service, Status, Event

class UnicodeTest(TestbedTest):

    def test_create_service(self):
        s = Service(slug=u"Ð", name=u"µ", description=u"À")
        s.put()
        data = s.rest("/api")

    def test_create_image(self):
        s = Status(name=u"∆", slug=u"∑´", description=u"œˆø", image=u"©˙")
        s.put()
        data = s.rest("/api")

    def test_create_event(self):
        s = Service(slug=u"hey", name=u"you", description=u"lol")
        s.put()

        stat = Status(name=u"you", slug=u"leave", description=u"why",
                      image=u"cry")
        stat.put()

        e = Event(status=stat, service=s, message=u"¨¥¨œ∑´æ")
        e.put()

        data = e.rest("/api")


