from google.appengine.ext import db
from models import Status, Service, Event
from datetime import datetime, timedelta, date

foo = Service(name="Service Foo", slug="service-foo",
              description="Scalable and reliable foo service across the globe")
foo.put()
bar = Service(name="Service Bar", slug="service-bar",
              description="Scalable and reliable foo service")
bar.put()
delete = Service(name="Delete Me", slug="delete", 
                 description="Delete Me Please")
delete.put()

cat = Status.get_by_slug("down")        

dates = [
    datetime(2010, 6, 5), 
    datetime(2010, 6, 10),
]

for d in dates:
    e = Event(service=bar, status=cat, 
          message="Error fine", start=d)
    e.put()


