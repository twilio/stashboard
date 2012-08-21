try:
    import json
except ImportError:
    import simplejson as json

import os
import unittest

from google.appengine.ext import testbed

def load_schemas(path):
    schemas = {}
    for f in os.listdir(path):
        filename, ext = os.path.splitext(f)
        if ext == ".json":
            schemas[filename] = json.load(open(os.path.join(path, f)))
    return schemas

class TestbedTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()
