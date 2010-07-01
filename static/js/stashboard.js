// StashBoard :{
stashboard = {};
  
stashboard.start = function(){
  var jsonp = document.createElement('script');
  jsonp.setAttribute("src","http://localhost:8080/api/v1/services?callback=stashboard.callback");
  jsonp.setAttribute("type", "text/javascript");
  document.body.appendChild(jsonp);
};

stashboard.callback = function(data){
  var services = data.services || [];
  var severity = 0;
  var summary = "green";
  var escalate = null;
  var serv = null;
  
  var levels = {
    NORMAL: [0, "green"],
    WARNING: [10, "yellow"],
    ERROR: [20, "red"],
    CRITICAL: [30, "red"],
  };
  
  console.log(services.length);
  for (var i=0; i < services.length; i++) {
    var service = services[i];
    var evt = service["current-event"];
    var level = null;
    
    if (evt) {
      var level = evt["status"].level;
    }
    
    console.log(level);
    
    if (level && levels[level][0] > severity) {
      escalate = evt;
      summary = levels[level][1];
      severity = levels[level][0];
      serv = service;
    }
    
  }
  
  var div = document.createElement('div');
  div.setAttribute("id", "stashboardStatus");
  var style = "width: 65px; height: 70px;";
  style    += "position: absolute; top: 0px; right: 45px;";
  style    += "background:#ccc;";
  style    += "-moz-border-radius-bottomleft: 15px; -webkit-border-bottom-left-radius: 15px;";
  style    += "-moz-border-radius-bottomright: 15px; -webkit-border-bottom-right-radius: 15px;";
  style    += "border-bottom-right-radius: 15px; border-bottom-left-radius: 15px;";
  style    += "border-bottom: 1px solid #999; border-left: 1px solid #999; border-right: 1px solid #999;"
  style    += "-moz-box-shadow: 0px 0px 10px #ccc; -webkit-box-shadow: 0px 0px 10px #ccc; z-index: 9999";
  div.setAttribute("style", style);
  
  
  var img = document.createElement('img');
  img.setAttribute("style", "width: 64px");
  img.setAttribute("src", "http://localhost:8080/images/widget/" + summary + ".png");
  
  
  var a = document.createElement('a');
  a.setAttribute("style", "text-decoration: none; border: 0;");
  a.setAttribute("href", "http://localhost:8080/");
  a.appendChild(img);
  div.appendChild(a);
  document.body.appendChild(div);
  
  
  if (escalate) {
    var message = document.createElement('div');
    message.setAttribute("id", "stashboardMessage");
    message.setAttribute("style", "-webkit-border-bottom-left-radius: 15px; -webkit-border-bottom-right-radius: 15px; border-bottom-right-radius: 15px; border-bottom-left-radius: 15px; position: absolute;top: 0px;height: 45px;right: 20px;padding: 0px 105px 0 15px;line-height: 45px;-moz-box-shadow: 0px 0px 8px rgb(204, 204, 204);-moz-border-radius-bottomleft: 15px;-moz-border-radius-bottomright: 15px;border-bottom: 1px solid #ccc;border-left: 1px solid #ccc;border-right: 1px solid #ccc; background: #eee;z-index: 99;");
  
  
    var img = document.createElement('img');
    img.setAttribute("style", "float: left; margin: 14px 10px 0 0;");
    img.setAttribute("src", escalate.status.image);
  
    var strong = document.createElement('strong');
    strong.innerHTML = serv.name + ":  ";
  
    var p = document.createElement('span');
    p.innerHTML = escalate.message;
  
    message.appendChild(img);
    message.appendChild(strong);
    message.appendChild(p);
    document.body.appendChild(message);
  }
      
};

window.onload = stashboard.start;

  