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
  
  window.MovieList = Backbone.Collection.extend({
    model: Movie,
    
    // Caught by main.py server to return a list of movies
    url: '/search',
    
    comparator: function(movie) {
      return 100 - movie.get("rating");
    }
  });
  
  window.MovieListContainer = Backbone.Collection.extend({
    defaults: {
      movieList: new MovieList(),
    },
    
    // Caught by main.py server to return metadata about the movies
    url: '/meta',
    
    parse: function(data) {
      // update the inner collection
      this.get('movieList').refresh(data.movieList);
      
      // Cleanup
      delete data.movieList;
      
      return data;
    }
  });
  
  window.Movies = new MovieList;
  window.MovieListContainer = new MovieListContainer(movieList=Movies);
  
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
  
  // The application
  // ----------------------
  
  window.AppView = Backbone.View.extend({
  
    el:$("#movieapp"),
    
    initialize: function() {
      _.bindAll(this, 'addOne', 'addAll', 'render');
      
      Movies.bind('add',     this.addOne);
      Movies.bind('refresh', this.addAll);
      Movies.bind('all',     this.render);
      
      Movies.fetch();
    },
    
    render: function() {
      this.addAll();
      this.$('#results_count').text(Movies.size());
      console.log(Movies.size());
    },
    
    addOne: function(movie) {
      var view = new MovieView({model: movie});
      this.$("#movies").append(view.render().el);
    },
    
    addAll: function() {
      Movies.each(this.addOne);
    }
    
  });
  
  window.App = new AppView;
});