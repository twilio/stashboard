class Migration(object):
    """App Engine data migration

    The timestamp is used to order migrations. No output is shown to the
    user, so make liberal use logging.

    Before running a migration on produciton data, download portitions of
    real data into an sample application using the bulk exporter
    """
    timestamp = None

    def run(self):
        """Run the migration """
        pass
