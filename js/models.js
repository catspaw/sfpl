window.Movie = Backbone.Model.extend({
  clear: function() {
    console.log("goodbye cruel world");
    this.view.remove();
  }
});
  
window.Filters = Backbone.Model.extend({
  defaults: {
    audienceRating: 0
  }
});

window.Statistics = Backbone.Model.extend({
  defaults: {
    matched_count: 0
  }
});

window.PaginatedCollection = Backbone.Paginator.requestPager.extend({
  model: Movie,
  
  initialize: function() {
    this.filters = new Filters();
    this.statistics = new Statistics();
  },
  
  paginator_core: {
    type: 'GET',
    dataType: 'json',
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
    '$audiencerating': function() { 
        return this.filters.get('audienceRating')
     }
  },

  comparator: function(movie) {
    return 100 - movie.get("rating");
  },
      
  parse: function(response) {
    // Our server returns the JSON blob as:
    // {'metadata': {...},
    //  'movies': [...]
    // }
    // This function uses the metadata to update data about the movies itself
    // but returns only the movies, to update the collection model.
    this.totalRecords = this.totalPages * this.perPage;
    this.statistics.set('matched_count', response.metadata.matched_count);
    
    return response.movies;
  },
  
  reset: function() {
    _.each(this.models, function(obj) { obj.clear() });
    this.currentPage = 0;
    this.pager();
  }
});

window.MovieCollection = new PaginatedCollection;
