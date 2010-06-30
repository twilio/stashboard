from google.appengine.ext import db
from models import Status, Service, Event
from datetime import datetime, timedelta

def create_services():
    
    bar = Service(name="Service Foo", slug="service-foo",
        description="Scalable and reliable foo service across the globe")

    foo = Service(name="Service Bar", slug="service-bar",
        description="Scalable and reliable bar service across the globe")
        
    foo.put()
    bar.put()
    
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
        low = Status.default()
        day = datetime.today() - timedelta(days=2)
        e = Event(service=service, status=low, 
            message="This service is operating fine", start=day)
        e.put()

create_statuses()
create_services()
create_events()

