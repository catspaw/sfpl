(function() {

  window.app = {};
  app.views = {};
  app.models = {};
  
  // Defer initialization until jQuery.ready is called
  $(function() {

     window.pagination = app.views.PaginatedView;
     window.App = new app.views.AppView;
  });

})();

// --- Infinite scroll triggering:

function lastPostFunc() { 
    // TODO: Show a 'loading' image...
    //    $('div#lastPostsLoader').html('<img src="bigLoader.gif">');

    // Grab more content.
    MovieCollection.requestNextPage();
    
    // TODO: 
    // Hide the 'loading' image.
};


$(window).scroll(function(){
  if  ($(window).scrollTop() == $(document).height() - $(window).height()){
    lastPostFunc();
  }
});