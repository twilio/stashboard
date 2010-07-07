// Common functions used on all pages

var stashboard = {};

// Display a message
stashboard.displayMessage = function(message, klass){
    $("#notice span").text(message);
    $("#notice").removeClass().addClass(klass).show();
};

// Display an error message
stashboard.error = function(message){
    stashboard.displayMessage(message, "error");
};

// Display an error message
stashboard.success = function(message){
    stashboard.displayMessage(message, "success");
};

// Display an info message
stashboard.info = function(message){
    stashboard.displayMessage(message, "info");
};

$(document).ready(function(){
    $("#notice a").click(function(){
	$("#notice").hide();
    });
});