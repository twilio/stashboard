import logging
from models import Image
from models import Status

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
    @classmethod
    def name(cls):
        return cls.__name__

    def start(self):
        logging.info("Staring migration %s" % self.__class__.__name__)
        self.run()
        logging.info("Finished migration %s" % self.__class__.__name__)

    def run(self):
        """Run the migration """
        pass


class UpdateStatusMigration(Migration):
    """ Migrate sample data

    This migration does nothing. NOTHING!

    """
    def run(self):
        logging.info("Update each status")
        # For each status
        for status in Status.all().fetch(100):

            # Set the status to default
            status.default = False

            # Update the status url
            status.image = "icons/fugue/" + status.image + ".png"

            # Save the status
            status.put()

        # Get the up status and make it default
        default_status = Status.get_by_slug("up")

        if default_status is None:
            logging.error("Could not find the up status")
            return

        default_status.default = True
        default_status.put()
        logging.info("Set up status as the default")


class AddImagesMigration(Migration):
    """ Add images to the database """

    def run(self):
        logging.info("Load the images into the database")
        Image.load_defaults()
        logging.info("Loading complete")


register(AddImagesMigration)
register(UpdateStatusMigration)
