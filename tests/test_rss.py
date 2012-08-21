import datetime
import random
import xml.etree.ElementTree
import models
import settings
from test_api import StashboardTest

class RSSFeedTest(StashboardTest):

    def setUp(self):
        super(RSSFeedTest, self).setUp()
        self.services = []
        self.statuses = []
        for name in ['web', 'billing', 'notifications']:
            service = models.Service(name=name.title(),
                                     slug=name,
                                     description="test service")
            service.put()
            self.services.append(service)
        for name in ['up', 'down', 'warning']:
            status = models.Status(name=name.title(),
                                   slug=name,
                                   description="test status",
                                   image="test image")
            status.put()
            self.statuses.append(status)

    def test_empty_feed(self):
        response = self.get("/rss")
        self.assertTrue("application/rss+xml" in response.headers["Content-Type"])
        self.assertEquals(response.status_code, 200)

    def test_feed_with_events(self):
        event = models.Event(start=datetime.datetime.now(), message="test hello",
                                service=random.choice(self.services),
                                status=random.choice(self.statuses))
        event.put()
        response = self.get("/rss")
        self.assertTrue("application/rss+xml" in response.headers["Content-Type"])
        self.assertEquals(response.status_code, 200)

        result = xml.etree.ElementTree.fromstring(response.content)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].tag, 'channel')
        channel = result[0]

        # assert that response has 1 event.
        self.assertEquals(len(channel.findall('item')), 1)

        # assert existence of title, description, and link elements in channel.
        for tag in ['title', 'description', 'link']:
            self.assertEquals(len(channel.findall(tag)), 1)

        item = channel.find('item')
        # assert existence of title, description, link, category, pubDate, and guid
        # elements in channel.
        for tag in ['title', 'description', 'link', 'category', 'pubDate', 'guid']:
            self.assertEquals(len(item.findall(tag)), 1)


    def test_feed_does_not_exceed_max(self):
        for _ in xrange(settings.RSS_NUM_EVENTS_TO_FETCH + 20):
            event = models.Event(start=datetime.datetime.now(), message="test hello",
                                    service=random.choice(self.services),
                                    status=random.choice(self.statuses))
            event.put()

        response = self.get("/rss")

        self.assertTrue("application/rss+xml" in response.headers["Content-Type"])
        self.assertEquals(response.status_code, 200)

        result = xml.etree.ElementTree.fromstring(response.content)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].tag, 'channel')
        channel = result[0]

        # assert that response does not have more than RSS_NUM_EVENTS_TO_FETCH events.
        self.assertEquals(len(channel.findall('item')), settings.RSS_NUM_EVENTS_TO_FETCH)

