from base import TestbedTest
from models import Image

class ImageTest(TestbedTest):

    def test_create_image(self):
        i = Image(slug="broom", icon_set="fugue",
                  path="icons/fugue/broom.png")
        i.put()
        self.assertEquals(i.slug, "broom")
        self.assertEquals(i.icon_set, "fugue")
        self.assertEquals(i.path, "icons/fugue/broom.png")
        self.assertEquals(i.absolute_url(), "/images/icons/fugue/broom.png")

    def test_load_default_images(self):
        Image.load_defaults()
        images = Image.all().fetch(1000)
        self.assertEquals(len(images), 112)

        fugue = Image.all().fetch(1000)

