from google.appengine.ext import db
import datetime
import config

class Service(db.Model):
    """A service to track

        Properties:
        name        -- string: The name of this service
        description -- string: The function of the service
        slug        -- stirng: URL friendly version of the name

    """
    @staticmethod
    def get_by_slug(service_slug):
        return Service.all().filter('slug = ', service_slug).get()
        
    def current_event(self):
        return self.events.order('-start').get()
        
    def past_five_days(self):
        return [None] * 5

    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    
    def sid(self):
        return str(self.key())
        
    def rest(self):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = str(self.name)
        m["id"] = str(self.slug)
        m["description"] = str(self.description)

        return m

class Status(db.Model):
    """A possible system status

        Properties:
        name        -- string: The name of this status
        description -- string: The state this status represents
        image       -- string: Image in /static/images/status
        severity    -- int: The serverity of this status

    """
    @staticmethod
    def get_by_name(status_name):
        return Status.all().filter('name = ', status_name).get()
        
    @staticmethod
    def lowest_severity():
        return Status.all().order('severity').get()
        
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    image = db.StringProperty(required=True)
    severity = db.IntegerProperty(required=True)
    
    def sid(self):
        return str(self.key())
        
    def rest(self):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = unicode(self.name)
        m["description"] = unicode(self.description)
        m["severity"] = str(self.severity)
        
        return m
    

class Event(db.Model):
    
    @staticmethod
    def current(service):
        return Event.all().filter('service =', service).order('-start').get()
    
    start = db.DateTimeProperty(required=True, auto_now_add=True)
    end = db.DateTimeProperty()
    status = db.ReferenceProperty(Status, required=True)
    message = db.TextProperty(required=True)
    service = db.ReferenceProperty(Service, required=True, 
        collection_name="events")
        
    def duration(self):
        # calculate the difference between start and end
        # should evantually be stored
        pass
        
    def sid(self):
        return str(self.key())
    
    def rest(self):
        """ Return a Python object representing this model"""
        
        m = {}
        m["sid"] = self.sid()
        m["start"] = self.start.isoformat()
        m["status"] = self.status.name
        m["message"] = str(self.message)
        
        if self.end == None:
            m["end"] = None
            m["duration"] = self.duration()
        else:
            m["end"] = self.end
            m["duration"] = self.duration()
        
        return m
    

