import logging

MIGRATIONS = {}


def register(migration):
    """ Register a migratin with the runner """
    MIGRATIONS[migration.__name__] = migration


def find(migration_name):
    """ Return the migration for a given class name

    If no migration found, returns None

    Arguments:
    key -- Name of a migration class

    """
    if migration_name in MIGRATIONS:
        return MIGRATIONS[migration_name]
    else:
        return None


def all():
    """ Return all registred migrations """
    return MIGRATIONS.values()


def clear():
    """ Clear all registerd migrations """
    MIGRATIONS.clear()


class Migration(object):
    """App Engine data migration

    A doc string is where you describe what your migration does

    No output is shown to the user, so make liberal use logging.

    Before running a migration on produciton data, download portitions of
    real data into an sample application using the bulk exporter

    Register migrations with the MigrationRunner.register method
    """

    def start(self):
        logging.info("Staring migration %s" % self.__class__.__name__)
        self.run()
        logging.info("Finished migration %s" % self.__class__.__name__)

    def run(self):
        """Run the migration """
        pass


class SampleMigration(Migration):
    """ Migrate sample data

    This migration does nothing. NOTHING!

    """

    def run(self):
        pass


register(SampleMigration)
