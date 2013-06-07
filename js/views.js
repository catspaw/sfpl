(function (views) {

views.MovieView = Backbone.View.extend({
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


views.PaginatedView = Backbone.View.extend({
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


// The application
// ----------------------

views.AppView = Backbone.View.extend({
  el:$("#movieapp"),

  events: {
    'click #next':                  'nextResultsPage',
    'click #audiencerating :radio':  'updateFilters'
  },
      
  initialize: function() {
    _.bindAll(this, 'addOne', 'addAll', 'render', 'refresh');
    
    MovieCollection.bind('add',     this.addOne);
    MovieCollection.bind('all',     this.render);
    MovieCollection.filters.bind('change', this.refresh);
    MovieCollection.statistics.bind('change', this.updateStats);
    
    MovieCollection.pager();
  },
  
  render: function() {
    // pass
  },
  
  refresh: function() {
    console.log("AppView refresh");
    this.$("#movies").empty();
    MovieCollection.reset();
  },
  
  addOne: function(movie) {
    console.log("addOne called");
    var view = new app.views.MovieView({model: movie});
    this.$("#movies").append(view.render().el);
  },
  
  addAll: function() {
    console.log("addAll called");
    MovieCollection.each(this.addOne);
  },
  
  nextResultsPage: function(e) {
    e.preventDefault();
    MovieCollection.requestNextPage();
  },
   
  updateFilters: function(e) {
    MovieCollection.filters.set('audienceRating',
                                $('input[name="audience"]:checked').val());
  },
  
  updateStats: function(e) {
    $('#results_count').text(e.get('matched_count'));
    console.log(e.get('matched_count'));
  }
});

})( app.views );