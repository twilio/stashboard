from google.appengine.ext import db
import datetime
import config

class Service(db.Model):
    #ensure that name is url friendly
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    
    def sid(self):
        return str(self.key())
        
    def obj(self):
        """ Return a Python object representing this model"""

        m = {}
        m["name"] = str(self.name)
        m["description"] = str(self.description)

        return m

class Status(db.Model):
    text = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    service = db.ReferenceProperty(Service, required=True, 
        collection_name="statuses")
    
    def sid(self):
        return str(self.key())
        
    def obj(self):
        """ Return a Python object representing this model"""

        m = {}
        m["sid"] = self.sid()
        m["text"] = unicode(self.text)
        m["description"] = unicode(self.description)

        return m
    

class Event(db.Model):
    
    @staticmethod
    def current():
        pass
    
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
    
    def obj(self):
        """ Return a Python object representing this model"""
        
        m = {}
        m["sid"] = self.sid()
        m["start"] = self.start
        m["status"] = self.status.text
        m["duration"] = self.duration()
        
        if self.end == None:
            m["end"] = datetime.now()
        else:
            m["end"] = self.end
        
        return m
        
class Message(db.Model):
    text = db.TextProperty(required=True)
    date = db.DateTimeProperty(required=True, auto_now_add=True)
    event = db.ReferenceProperty(Event, required=True)
    
    def sid(self):
        return str(self.key())
    
    def obj(self):
        """ Return a Python object representing this model"""
        
        m = {}
        m["sid"] = self.sid()
        m["date"] = self.date
        m["message"] = self.text
        m["event"] = event.sid()
        
        return m
        
    

