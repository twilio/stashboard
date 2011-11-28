var stashboard = (function (parent, $) {
  
  var Service = Backbone.Model.extend({
    
    loadHistory: function() {
      // pass
    },
    
    loadStatus: function() {
      url = "/api/v1/services/" + this.get("slug") + "/events/current";
      $.getJSON(url, {}, function(data){
        this.set({"status": data});
      });
    },
    
    
  });
  
  var ServiceList = Backbone.Collection.extend({
    model: Service
  });
  
  var Services = new ServiceList;
  
  var ServiceView = Backbone.View.extend({
    
    initialize: function() {
      _.bindAll(this, 'status');
      
      // The table row already exists in the DOM
      this.el = $("#" + this.model.slug);
      this.model.bind('change:status', this.status);
      //this.model.bind('change:history', this.history);
      this.model.view = this;
      
      // Load the history and status
      //this.model.loadHistory();
      this.model.loadStatus();
    },
    
    status: function() {
      console.log(this.model.status);
    }

  });

  var ServicesView = Backbone.View.extend({
    
    initialize: function() {
      Services.bind('refresh', this.fetchAdditional);
    },
    
    fetchAdditional: function() {
      Services.each(function(m) {
        new ServiceView({model: m});
      });
    }
    
  });

  var App = new ServicesView;
  parent.services = Services;
  
  return parent;
}(stashboard || {}, jQuery));