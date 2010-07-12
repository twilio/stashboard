from google.appengine.ext import db
import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from datetime import timedelta
from datetime import date
import config
import urlparse

class Level(object):
    """
    A fake db.Model object, just in case we want to actually store things
    in the future
    """
    levels = {
        "NORMAL": 10,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    
    normal  = "NORMAL"
    warning = "WARNING"
    critial = "CRITICAL"
    error   = "ERROR"
    
    @staticmethod
    def all():
        llist = []
        for k in Level.levels.keys():
            llist.append((k, Level.levels[k]))
        
        return map(lambda x: x[0], sorted(llist, key=lambda x: x[1]))
        
    @staticmethod
    def get_severity(level):
        try:
            return Level.levels[level]
        except:
            return False
            
    @staticmethod
    def get_level(severity):
        for k in Level.levels.keys():
            if Level.levels[k] == severity:
                return k
        return False
     

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
        event = self.events.order('-start').get()
        return event


    #Specialty function for front page
    def last_five_days(self):
        
        
        lowest = Status.default()
        severity = lowest.severity
        
        yesterday = date.today() - timedelta(days=1)
        ago = yesterday - timedelta(days=5)
        
        events = self.events.filter('start >', ago) \
            .filter('start <', yesterday).fetch(100)
        
        stats = {}
        
        for i in range(5):
            stats[yesterday.day] = {
                "image": lowest.image,
                "day": yesterday,
            }
            yesterday = yesterday - timedelta(days=1)
        
        for event in events:
            if event.status.severity > severity:
                stats[event.start.day]["image"] = "information"
                stats[event.start.day]["information"] = True
        results = []
        for k in stats.keys():
            results.append(stats[k])
            
        results.reverse()
        
        return results
        
        
    def events_for_day(self, day):
        """ Return the largest seveirty (of events) for a given day. If no 
        events occured, return the lowest severity rating.
        
        Arguments: 
        day         -- Date object: The day to summarize
        
        """
        
        next_day = day + timedelta(days=1)
        
        return self.events.filter('start >', day) \
            .filter('start <', next_day).fetch(40)
            
    def compare(self, other_status):
        return 0
    
    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    
    def sid(self):
        return str(self.key())
        
    def resource_url(self):
        return "/services/" + self.slug
        
    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = str(self.name)
        m["id"] = str(self.slug)
        m["description"] = str(self.description)
        m["url"] = base_url + self.resource_url()
        
        event = self.current_event()
        if event:
            m["current-event"] = event.rest(base_url)
        else:
            m["current-event"] = None

        return m

class Status(db.Model):
    """A possible system status

        Properties:
        name        -- string: The friendly name of this status
        slug        -- stirng: The identifier for the status
        description -- string: The state this status represents
        image       -- string: Image in /static/images/status
        severity    -- int: The serverity of this status

    """
    @staticmethod
    def get_by_slug(status_slug):
        return Status.all().filter('slug = ', status_slug).get()
        
    @staticmethod
    def default():
        """
        Return the first status with a NORMAL level.
        """
        normal = Level.get_severity(Level.normal)
        return Status.all().filter('severity == ', normal).get()

    @staticmethod
    def install_defaults():
        """
        Install the default statuses. I am not sure where these should live just yet
        """
        # This should be Level.normal.severity and Level.normal.text
        normal = Level.get_severity(Level.normal)
        warning = Level.get_severity(Level.warning)
        error = Level.get_severity(Level.error)

        d = Status(name="Down", slug="down", image="cross-circle", severity=error, \
                       description="The service is currently down")
        u = Status(name="Up", slug="up", image="tick-circle", severity=normal, \
                       description="The service is up")
        w = Status(name="Warning", slug="warning", image="exclamation", severity=warning, \
                       description="The service is experiencing intermittent problems")

        d.put()
        u.put()
        w.put()

        s = Setting(name="installed_defaults")
        s.put()
        
        
    name = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    image = db.StringProperty(required=True)
    severity = db.IntegerProperty(required=True)
    
    def image_url(self):
        return "/images/status/" + unicode(self.image) + ".png"
        
    def resource_url(self):
        return "/statuses/" + str(self.slug)
        
    def rest(self, base_url):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = str(self.name)
        m["id"] = str(self.slug)
        m["description"] = str(self.description)
        m["level"] = Level.get_level(int(self.severity))
        m["url"] = base_url + self.resource_url()
        # This link shouldn't be hardcoded
        
        o = urlparse.urlparse(base_url)
        m["image"] = o.scheme + "://" +  o.netloc + self.image_url()
        
        return m
    

class Event(db.Model):

    start = db.DateTimeProperty(required=True, auto_now_add=True)
    informational = db.BooleanProperty(default=False)
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
        
    def resource_url(self):
        return self.service.resource_url() + "/events/" + self.sid()
    
    def rest(self, base_url):
        """ Return a Python object representing this model"""
        
        m = {}
        m["sid"] = self.sid()

        stamp = mktime(self.start.timetuple())
        m["timestamp"] = format_date_time(stamp)
        m["informational"] = self.informational
        m["status"] = self.status.rest(base_url)
        m["message"] = str(self.message)
        m["url"] = base_url + self.resource_url()
        
        return m
        
class Profile(db.Model):
    owner = db.UserProperty(required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)

class AuthRequest(db.Model):
    owner = db.UserProperty(required=True)
    request_secret = db.StringProperty()

class Setting(db.Model):
    name = db.StringProperty(required=True)

