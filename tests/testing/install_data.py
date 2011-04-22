# Copyright (c) 2010 Twilio Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from google.appengine.ext import db
from models import Status, Service, Event
from datetime import datetime, timedelta, date

#foo = Service(name="Service Foo", slug="service-foo",
#              description="Scalable and reliable foo service across the globe")
#foo.put()
#bar = Service(name="Service Bar", slug="service-bar",
              description="Scalable and reliable foo service")
#bar.put()
#delete = Service(name="Delete Me", slug="delete", 
                 description="Delete Me Please")
#delete.put()

bar = Service.get_by_slug("bar")
cat = Status.get_by_slug("down")        

dates = [
    datetime(2010, 6, 5), 
    datetime(2010, 6, 10),
    datetime(2010, 7, 16), 
    datetime(2010, 7, 17),
    datetime(2010, 7, 18, 7),
]

for d in dates:
    e = Event(service=bar, status=cat, 
          message="Error fine", start=d)
    e.put()


