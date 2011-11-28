import unittest
import migrations
from migrations import Migration


class SampleMigration(Migration):
    pass


class MigrationTest(unittest.TestCase):

    def test_register_find(self):
        migrations.clear()
        migrations.register(SampleMigration)
        m = migrations.find("SampleMigration")
        self.assertTrue(m.__name__, "SampleMigration")

    def test_register_cant_find(self):
        migrations.clear()
        m = migrations.find("SampleMigration")
        self.assertEquals(m, None)

    def test_register_all(self):
        migrations.clear()
        migrations.register(SampleMigration)
        ms = migrations.all()
        self.assertEquals(len(ms), 1)

    def test_register_clear(self):
        migrations.clear()
        migrations.register(SampleMigration)
        migrations.clear()
        ms = migrations.all()
        self.assertEquals(len(ms), 0)
