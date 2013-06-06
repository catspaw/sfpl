//

// Load the application once jQuery.ready is called
$(function() {

  window.Movie = Backbone.Model.extend({
    initialize: function() {
    },
    
    clear: function() {
      this.destroy();
      this.view.remove();
    }
  });

  window.PaginatedCollection = Backbone.Paginator.requestPager.extend({
    model: Movie,
    
    paginator_core: {
      // the type of the request (GET by default)
      type: 'GET',

      // the type of reply (jsonp by default)
      dataType: 'json',

      // the URL (or base URL) for the service
      url: '/search'
    },
    
    paginator_ui: {
      // the lowest page index your API allows to be accessed
      firstPage: 0,

      // which page should the paginator start from
      // (also, the actual page the paginator is on)
      currentPage: 0,

      // how many items per page should be shown
      perPage: 7,

      // a default number of total pages to query in case the API or
      // service you are using does not support providing the total
      // number of pages for us.
      // 10 as a default in case your service doesn't return the total
      totalPages: 10
    },
    
    server_api: {
      // the query field in the request
      '$filter': '',

      // number of items to return per request/page
      '$top': function() { return this.perPage },

      // how many results the request should skip ahead to
      // customize as needed. For the Netflix API, skipping ahead based on
      // page * number of results per page was necessary.
      '$skip': function() { return this.currentPage * this.perPage },

      // field to sort by
      '$orderby': 'Rating',

      // what format would you like to request results in?
      '$format': 'json',

      // custom parameters
      '$inlinecount': 'allpages'
    },

    comparator: function(movie) {
      return 100 - movie.get("rating");
    },
        
    parse: function(response) {
      // Be sure to change this based on how your results
      // are structured (e.g d.results is Netflix specific)
      
      // var tags = response.d.results;
      
      //Normally this.totalPages would equal response.d.__count
      //but as this particular NetFlix request only returns a
      //total count of items for the search, we divide.
      
      //this.totalPages = Math.ceil(response.d.__count / this.perPage);
      
      this.totalRecords = this.totalPages * this.perPage;
      console.log("Parse called");
      return response;
    },
    
    error: function(resp, options) {
      console.log("Error calling backbone parse.");
    }
  });
  
  window.MovieCollection = new PaginatedCollection;
  
  window.MovieView = Backbone.View.extend({
    tagName: "div",
    
    // Cache the template function for a single movie
    template: _.template($('#movie-template').html()),
    
    // The MovieView listens for changes to its model, re-rendering.
    initialize: function() {
      _.bindAll(this, 'render');
      this.model.bind('change', this.render);
      this.model.view = this;
    },
    
    // Re-render the contents of the movie item,
    render: function() {
      console.log('MovieView render called');
      $(this.el).html(this.template(this.model.toJSON()));
      this.setContent();
      return this;
    },
    
    setContent: function() {
      this.$('.movietitle').text(this.model.get('title'));
      this.$('.year').text(this.model.get('year'));
      this.$('.starring').text(this.model.get('starring'));
      this.$('.runtime_value').text(this.model.get('runtime'));
      this.$('.mpaa_value').text(this.model.get('mpaa'));
      this.$('.thumbnail img').attr('src', this.model.get('thumbnail'));
      this.$('.reviews a').attr('href', this.model.get('reviews'));
      this.$('.rating').text(this.getRating(this.model.get('rating')));
    },
    
    getRating: function(score) {
      // Todo: make this into graphical stars
      if (score >= 90) {
        return 'SSSSS';
      } else if (score >= 80) {
        return 'SSSS-';
      } else if (score >= 70) {
        return 'SSSS ';
      } else if (score >= 60) {
        return 'SSS- ';
      } else if (score >= 50) {
        return 'SSS  ';
      } else if (score >= 40) {
        return 'SS-  ';
      } else if (score >= 30) {
        return 'SS   ';
      } else if (score >= 20) {
        return 'S-   ';
      } else if (score >= 10) {
        return 'S    ';
      } else {
        return '-    ';
      }
    }
  });
  
  window.PaginatedView = Backbone.View.extend({
    tagName: 'aside',
    
    initialize: function() {
      MovieCollection.bind('sync', this.render);
      this.$el.appendTo('#movies');
    },
    
    render: function () {
      console.log('PaginatedView render');
			var html = this.template(PaginatedView.info());
			this.$el.html(html);
		},
  });
  window.pagination = PaginatedView;

  // The application
  // ----------------------
  
  window.AppView = Backbone.View.extend({
    el:$("#movieapp"),

    events: {
      'click #next': 'nextResultsPage'
    },
        
    initialize: function() {
      _.bindAll(this, 'addOne', 'addAll', 'render');
      
      MovieCollection.bind('add',     this.addOne);
      //MovieCollection.bind('refresh', this.addAll);
      MovieCollection.bind('all',     this.render);
      
      MovieCollection.pager();
//      MovieCollection.fetch();
     // MovieCollection.bootstrap({totalRecords: 50});
    },
    
    render: function() {
      console.log("AppView render");
      this.$('#results_count').text(MovieCollection.totalRecords);
    },
    
    addOne: function(movie) {
      console.log("addOne called");
      var view = new MovieView({model: movie});
      this.$("#movies").append(view.render().el);
    },
    
    addAll: function() {
      console.log("addAll called");
      MovieCollection.each(this.addOne);
    },
    
    nextResultsPage: function(e) {
      e.preventDefault();
      MovieCollection.requestNextPage();
    }    
  });
  
  window.App = new AppView;
});

function lastPostFunc() { 
    // Show a 'loading' image...
//    $('div#lastPostsLoader').html('<img src="bigLoader.gif">');

    // Grab more content.
    MovieCollection.requestNextPage();
    
    // Hide the 'loading' image.
};

$(window).scroll(function(){
        if  ($(window).scrollTop() == $(document).height() - $(window).height()){
           lastPostFunc();
        }
});