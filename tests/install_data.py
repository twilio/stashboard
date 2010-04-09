from google.appengine.ext import db
from models import Status, Service, Event


def create_services():

    voice = Service(name="Twilio Voice", slug="twilio-voice", 
        description="Twilio's voice communications platform")
    
    sms = Service(name="Twilio SMS", slug="twilio-sms", 
        description="SMS broadcast, queuing, and messaging service")
    
    inter = Service(name="Twilio International", slug="twilio-international",
        description="Phone and SMS service to international numbers")

    foo = Service(name="Twilio Foo", slug="twilio-foo",
        description="If I'm a Foo and you're a Foo, are we both Foos?")
        
    voice.put()
    sms.put()
    inter.put()
    foo.put()
    
def create_statuses():
    up = Status(name="up", description="This service is up and running",
        image="tick-circle.png", severity=1)
        
    mat = Status(name="maintenance", description="The service is undergoing \
        scheduled maintenance", image="wrench-screwdriver.png",
        severity=5)
    
    down = Status(name="down", description="The service is completely down \
        and not working at all", image="cross-circle.png", severity=100000)
        
    cat = Status(name="intermittent", description="The service is currently \
        experiencing intermittent problems", image="exclamation.png", 
        severity=10)
        
    up.put()
    cat.put()
    mat.put()
    down.put()

def create_events():
    for service in Service.all():
        up = Status.get_by_name("up")
        e = Event(service=service, status=up, 
            message="Twilio is operating fine")
        e.put()

create_events()
