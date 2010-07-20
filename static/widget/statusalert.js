// StashBoard :{
stashboard = {};

stashboard.host = "http://stashboard.appspot.com";

stashboard.start = function(){
  var previous = document.getElementById("stashboardJavascript");
  if (previous){
    previous.parentNode.removeChild(previous);
  }
  
  var jsonp = document.createElement('script');
  jsonp.setAttribute("id", "stashboardJavascript");
  jsonp.setAttribute("src", stashboard.host + "/api/v1/services?callback=stashboard.callback&random=" + Math.random());
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
    CRITICAL: [30, "red"]
  };
  
  for (var i=0; i < services.length; i++) {
    var service = services[i];
    var evt = service["current-event"];
    var level = null;
    
    if (evt) {
      level = evt.status.level;
    }
    
    if (level && levels[level][0] > severity) {
      escalate = evt;
      summary = levels[level][1];
      severity = levels[level][0];
      serv = service;
    }
    
  }
  
  var div = document.createElement('div');
  var style = "width: 45px; height: 45px; position: absolute; top: 0px; right: 20px;background:#ccc;-moz-border-radius-bottomleft: 15px; -webkit-border-bottom-left-radius: 15px;-moz-border-radius-bottomright: 15px; -webkit-border-bottom-right-radius: 15px;border-bottom-right-radius: 15px; border-bottom-left-radius: 15px;border-bottom: 1px solid #999; border-left: 1px solid #999; border-right: 1px solid #999;-moz-box-shadow: 0px 0px 10px #ccc; -webkit-box-shadow: 0px 0px 10px #ccc; z-index: 9999";
  div.setAttribute("style", style);
  
  var img = document.createElement('img');
  img.setAttribute("style", "width: 45px; border: 0");
  img.setAttribute("src", stashboard.host + "/images/widget/" + summary + ".png");
  
  
  var a = document.createElement('a');
  a.setAttribute("style", "text-decoration: none; border: 0;");
  a.setAttribute("href", stashboard.host);
  a.appendChild(img);
  div.appendChild(a);
  var previous = document.getElementById("stashboardStatus");
  if (previous){
    previous.parentNode.removeChild(previous);
  }
  div.setAttribute("id", "stashboardStatus");
  document.body.appendChild(div);
  
  var message = null;
  if (escalate) {
    message = document.createElement('div');
    message.setAttribute("style", "font-size: 14px; max-width: 35%; overflow: hidden;-webkit-border-bottom-left-radius: 15px; -webkit-border-bottom-right-radius: 15px; border-bottom-right-radius: 15px; border-bottom-left-radius: 15px; position: absolute;top: 0px;height: 45px;right: 20px;padding: 0px 55px 0 15px;line-height: 45px;-moz-box-shadow: 0px 0px 8px rgb(204, 204, 204);-moz-border-radius-bottomleft: 15px;-moz-border-radius-bottomright: 15px;border-bottom: 1px solid #ccc;border-left: 1px solid #ccc;border-right: 1px solid #ccc; background: #eee;z-index: 99;");

  
  
    img = document.createElement('img');
    img.setAttribute("style", "float: left; margin: 14px 10px 0 0;");
    img.setAttribute("src", escalate.status.image);
  
    var strong = document.createElement('strong');
    strong.innerHTML = serv.name + ":  ";
  
    var p = document.createElement('span');
    p.innerHTML = escalate.message;
  
    message.appendChild(img);
    message.appendChild(strong);
    message.appendChild(p);
  }
  
  previous = document.getElementById("stashboardMessage");
  if (previous){
    previous.parentNode.removeChild(previous);
  }
  if (message){
    message.setAttribute("id", "stashboardMessage");
    document.body.appendChild(message);
  }
  
  
  setTimeout(stashboard.start, 6000);

};

window.onload = stashboard.start;

  