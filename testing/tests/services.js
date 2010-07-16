function rfc1123(date){
    rfc = $.datepicker.formatDate("D, d M yy", date);
    rfc = rfc + " " + date.getHours() + ":";
    rfc = rfc + date.getMinutes() + ":" + date.getSeconds();
    offset = date.getTimezoneOffset();
    minutes = offset % 60;
    hours = (offset - minutes) / 60;

    if (offset < 0) {
	off = "+";
    } else {
	off = "-";
    }
    
    if (hours < 10) {
	off += "0";
    } 
    off += hours.toString();

    if (minutes < 10) {
	off += "0";
    }
    off += minutes.toString();
	
    return rfc + " " + off;
}

function testError(url, method, code, data){
    return function() {
	expect(2);
	data = data || {};
	$.ajax({ 
	    type: method,
	    Url: url,
	    Datatype: 'json', 
	    data: data,
	    success: function(service){ 
		start();
	    },
	    error: function(evt){
		data = JSON.parse(evt.responseText);
		equals(data.code, code);
		equals(data.error, true);
		start();
	    }
	});
    }
}

module("Services Test");

asyncTest("Getting a Non-existent service fails", function() {
    expect(2);
    $.ajax({ 
	type: "GET",
	url: "/api/v1/services/wrong-service",
	Datatype: 'json', 
	success: function(evt){ 
	    start();
	},
	error: function(evt){ 
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 404);
	    equals(data.error, true);
	    start();
	}
    });
});

asyncTest("Getting a service succeeds", function() {
    expect(3);
    $.ajax({ 
	type: "GET",
	url: "/api/v1/services/service-foo",
	Datatype: 'json', 
	success: function(service){ 
	    equals("Service Foo",service.name);
	    equals("Scalable and reliable foo service across the globe",service.description);
	    equals("service-foo",service.id);
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });
});

asyncTest("Deleting a service succeeds", function() {
    expect(3);
    $.ajax({ 
	type: "DELETE",
	url: "/api/v1/services/delete",
	Datatype: 'json', 
	success: function(service){ 
	    equals("Delete Me",service.name);
	    equals("Delete Me Please",service.description);
	    equals("delete",service.id);
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });
});

asyncTest("Accessing a url with a trailing slash fails",function() {
    expect(2);
    $.ajax({ 
	type: "GET",
	url: "/api/v1/services/",
	Datatype: 'json', 
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 404);
	    equals(data.error, true);
	    start()
	}
    });
});


asyncTest("Posting to /services without a service name", function() {
    expect(2);
    $.ajax({ 
	type: "POST",
	url: "/api/v1/services",
	Datatype: 'json', 
	data: {
	    "description": "An example service API",
        },
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 400);
	    equals(data.error, true);
	    start()
	}
    });
});

asyncTest("Posting to /services without a service description", function() {
    expect(2);
    $.ajax({ 
	type: "POST",
	url: "/api/v1/services",
	Datatype: 'json', 
	data: {
	    "name": "An example API",
        },
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 400);
	    equals(data.error, true);
	    start();
	}
    });
});

asyncTest("Posting to /services without data", function() {
    expect(2);
    $.ajax({ 
	type: "POST",
	url: "/api/v1/services",
	Datatype: 'json', 
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 400);
	    equals(data.error, true);
	    start();
	}
    });
});

asyncTest("DELETE /services should fail", function() {
    expect(2);
    $.ajax({ 
	type: "DELETE",
	url: "/api/v1/services",
	Datatype: 'json', 
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 405);
	    equals(data.error, true);
	    start();
	}
    });
});

asyncTest("PUT /services should fail", function() {
    expect(2);
    $.ajax({ 
	type: "PUT",
	Url: "/api/v1/services",
	Datatype: 'json', 
	data: {},
	success: function(service){ 
	    start();
	},
	error: function(evt){
	    data = JSON.parse(evt.responseText);
	    equals(data.code, 405);
	    equals(data.error, true);
	    start();
	}
    });
});

module("Events");

asyncTest("GET Test that the calendar resource respects timezone offset", 2, function(){
    //There should only be one event
    startD = 'Wed, 9 Jun 2010 0:0:0 -0001';
    endD = 'Thu, 10 Jun 2010 0:0:0 -0001';

    url = "/api/v1/services/service-bar/events/calendar";
    url += "?start=" + startD + "&end=" + endD;

    $.ajax({ 
	type: "GET",
	url: url,
	Datatype: 'json', 
	success: function(service){ 
	    ok(service.days[0].information, "Day has information attached");
	    ok(!service.days[1].information, "Day has no information attached");
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });    
});

asyncTest("GET Test that the calendar resource uses UTC by default", 2, function(){
    //There should only be one event
    startD = 'Wed, 9 Jun 2010 0:0:0';
    endD = 'Thu, 10 Jun 2010 0:0:0';

    url = "/api/v1/services/service-bar/events/calendar";
    url += "?start=" + startD + "&end=" + endD;

    $.ajax({ 
	type: "GET",
	url: url,
	Datatype: 'json', 
	success: function(service){ 
	    ok(service.days[1].information, "Day has information attached");
	    ok(!service.days[0].information, "Day has no information attached");
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });    
});

asyncTest("GET Test that the event resource filters properly", 1, function(){
    startD = 'Wed, 9 Jun 2010 0:0:0';
    endD = 'Wed, 9 Jun 2010 23:59:59';

    url = "/api/v1/services/service-bar/events";
    url += "?start=" + startD + "&end=" + endD;

    $.ajax({ 
	type: "GET",
	url: url,
	Datatype: 'json', 
	success: function(service){ 
	    equals(service.events.length, 0, "No events returned");
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });    
});

asyncTest("GET Test that the event resource filters properly", 1, function(){
    startD = 'Wed, 9 Jun 2010 0:0:0';
    endD = 'Thu, 10 Jun 2010 0:0:0';

    url = "/api/v1/services/service-bar/events";
    url += "?start=" + startD + "&end=" + endD;

    $.ajax({ 
	type: "GET",
	url: url,
	Datatype: 'json', 
	success: function(service){ 
	    equals(service.events.length, 1, "One event returned");
	    start();
	},
	error: function(evt){ 
	    start();
	}
    });    
})