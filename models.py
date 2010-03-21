from google.appengine.ext import db
import datetime
import config

class Service(db.Model):
    #ensure that name is url friendly
    @staticmethod
    def get_by_name(service_name):
        return Service.all().filter('name = ', service_name).get()
    
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    
    def sid(self):
        return str(self.key())
        
    def rest(self):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = str(self.name)
        m["description"] = str(self.description)

        return m

class Status(db.Model):
    @staticmethod
    def get_by_name(status_name, service):
        return Status.all().filter('name = ', status_name).filter('service =', service).get()
    
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    service = db.ReferenceProperty(Service, required=True, 
        collection_name="statuses")
    
    def sid(self):
        return str(self.key())
        
    def rest(self):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = unicode(self.name)
        m["description"] = unicode(self.description)

        return m
    

class Event(db.Model):
    
    @staticmethod
    def current(service):
        return Event.all().filter('service =', service).order('-start').get()
    
    start = db.DateTimeProperty(required=True, auto_now_add=True)
    end = db.DateTimeProperty()
    status = db.ReferenceProperty(Status, required=True)
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
        
        if self.end == None:
            m["end"] = None
            m["duration"] = self.duration()
        else:
            m["end"] = self.end
            m["duration"] = self.duration()
        
        return m
        
class Message(db.Model):
    @staticmethod
    def get_by_sid(sid):
        return Message.get(db.Key(encoded=sid))
    
    text = db.TextProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)
    event = db.ReferenceProperty(Event, required=True)
    service = service = db.ReferenceProperty(Service, required=True, 
        collection_name="messages")
    
    def sid(self):
        return str(self.key())
    
    def rest(self):
        """ Return a Python object representing this model"""
        
        m = {}
        m["sid"] = self.sid()
        m["date"] = self.date.isoformat()
        m["message"] = str(self.text)
        m["event"] = self.event.sid()
        
        return m
        
    

