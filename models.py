from google.appengine.ext import db
import datetime
from datetime import timedelta
from datetime import date
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
        
    def critical_incident(self, day):
        """ Return the largest seveirty (of events) for a given day. If no 
        events occured, return the lowest severity rating.
        
        Arguments: 
        day         -- Date object: The day to summarize
        
        """
        
        next_day = day + timedelta(days=1)
        
        events = self.events.filter('start >', day) \
            .filter('start <', next_day).fetch(40)
            
        if events:
            levels = map(lambda x: x.status.severity, events)
            lowest = Status.lowest_severity()
            return max(levels) > lowest.severity
        else:
            return False 
        
        
    def past_five_days(self):
        days = []
        day = date.today()
        for i in range(5):
            day = day - timedelta(days=1)
            if self.critical_incident(day):
                days.append(day)
            else:
                days.append(None)
            
        return days

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
    def get_info():
        """ The info status. We don't make this a real status object because 
            it should not have a severity ranking. This is prety hacky
        """
        info = {}
        info["name"] = "Information Available"
        info["image"] = "information.png"
        info["description"] = "There is information available"
        info["severity"] = -1
        return info
        
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
        m["timestamp"] = self.start.isoformat()
        m["status"] = self.status.name
        m["message"] = str(self.message)
        #m["service"] = self.service.sid()
        
        return m
    

