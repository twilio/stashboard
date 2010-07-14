from google.appengine.ext import db
from models import Status, Service, Event
from datetime import datetime, timedelta

bar = Service(name="Service Foo", slug="service-foo",
              description="Scalable and reliable foo service across the globe")

bar.put()
    

cat = Status.get_by_slug("down")        
day = datetime.today() - timedelta(days=2)
e = Event(service=service, status=cat, 
          message="Error fine", start=day)
e.put()


