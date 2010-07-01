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
  var escalte = null;
  var serv = null;
  
  console.log(services.length);
  for (var i=0; i < services.length; i++) {
    var service = services[i];
    var evt = service["current-event"];
    var level = null;
    
    if (evt) {
      var level = evt["status"].level;
    }
    
    console.log(level);
    
    if (level === "INFO" && severity === 0) {
      severity = 1;
      summary = "blue";
    } else if (level !== "NORMAL" && severity < 2) {
      if (level === "WARNING" && severity < 3){
        summary = "yellow";
        escalte = evt;
        serv = service;
        severity = 2;
      } else {
        summary = "red";
        escalte = evt;
        serv = service;
        severity = 3;
      }
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
  div.appendChild(img);
  document.body.appendChild(div);
  
  
  if (escalte) {
    var message = document.createElement('div');
    message.setAttribute("id", "stashboardMessage");
    message.setAttribute("style", "-webkit-border-bottom-left-radius: 15px; -webkit-border-bottom-right-radius: 15px; border-bottom-right-radius: 15px; border-bottom-left-radius: 15px; position: absolute;top: 0px;height: 45px;right: 20px;padding: 0px 105px 0 15px;line-height: 45px;-moz-box-shadow: 0px 0px 8px rgb(204, 204, 204);-moz-border-radius-bottomleft: 15px;-moz-border-radius-bottomright: 15px;border-bottom: 1px solid #ccc;border-left: 1px solid #ccc;border-right: 1px solid #ccc; background: #eee;z-index: 99;");
  
  
    var img = document.createElement('img');
    img.setAttribute("style", "float: left; margin: 14px 10px 0 0;");
    img.setAttribute("src", escalte.status.image);
  
    var strong = document.createElement('strong');
    strong.innerHTML = serv.name + ":  ";
  
    var p = document.createElement('span');
    p.innerHTML = escalte.message;
  
    message.appendChild(img);
    message.appendChild(strong);
    message.appendChild(p);
    document.body.appendChild(message);
  }
      
};

window.onload = stashboard.start;

  