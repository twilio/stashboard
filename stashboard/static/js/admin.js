var stashboard = (function (parent, $) {

  $(document).ready(function(){
       
    $("form.admin").submit(function(e){
      e.preventDefault();
      $.post($("form.admin").attr("action"),
        $("form.admin").serialize(), function(data){
          location.href = "/admin/services";
      }, "json")
      .error(function(jqXHR){
        var data = JSON.parse(jqXHR.responseText);
        $(".error").html(data.message).show();
      });
    });
    
    $("form.delete").submit(function(e){
      e.preventDefault();
      $.ajax({
        type: "DELETE",
        data: {},
        dataType: "json",
        url: $("form.delete").attr("action"),
        success: function(data){
          location.href = "/admin/services";
        },
        error: function(data){
          $(".error").html(data.message).show();
        }
      });
    });
    
  });

}(stashboard || {}, jQuery));