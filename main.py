#!/usr/bin/python

"""The main SFPL webapp server.

  /            GET main page
  /search?     GET ajax request for movie list and information
  /store       POST method for filling the database

Expects to be run via Google App Engine.  See README.md for more information.
"""

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

import os

# The SFPL only has so many movies.  Keeping an upper limit helps
# queries to run faster.
MAX_NUM_MOVIES = 6000


class Movie(db.Model):
  rtid = db.StringProperty()
  title = db.StringProperty()
  year = db.IntegerProperty()
  mpaa = db.StringProperty()
  runtime = db.IntegerProperty()
  rating = db.IntegerProperty()
  thumbnail = db.StringProperty()
  starring = db.StringProperty()
  reviews = db.StringProperty()
  
  def toDict(self):
    """Returns dict representation of Movie for converting to JSON."""
    movie = {
        'rtid': self.rtid,
        'title': self.title,
        'year': self.year,
        'mpaa': self.mpaa,
        'runtime': self.runtime,
        'rating': self.rating,
        'thumbnail': self.thumbnail,
        'starring': self.starring,
        'reviews': self.reviews
        }
    if not movie['runtime']:
      movie['runtime'] = 'Unknown'
    return movie


class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, None))


class SearchHandler(webapp.RequestHandler):
  def get(self, id):
    """ /search? request returns JSON object {'metadata': {...}, 'movies': [...]}
    
    See QueryBuilder below for a list of filter params that can be passed into the URL
    to filter or sort the returned movie results.  By backbone.paginator convention,
    these all begin with a '$', even though that's weird as hell to read in Python. :)
    """
    movies = []
    top = int(self.request.get('$top', 10))
    start = int(self.request.get('$skip', 0))

    movie_query = self.QueryBuilder(request)
    
    for movie in movie_query.run(offset=start, limit=top):
      movies.append(movie.toDict())
      
    data = {'metadata': {'matched_count': matched_count},
            'movies': movies}
    data = simplejson.dumps(data)
    self.response.out.write(data)

  def QueryBuilder(self, request):
    """Return a Query object, given filters specified in the request object.
    
    Valid filters:
      $audiencerating: 0 through 5, the minimum audience rating to return
      $orderby: 'Rating', 'Title' or 'ReleaseDate'
    """
    movie_query = Movie.all()
    
    min_rating = self.request.get('$audiencerating', '0')
    # Convert stars (eg: 4.5) into RottenTomatoes percentage rating.
    min_rt_rating = int((float(min_rating) * 20) - 10)
    movie_query.filter('rating >=', min_rt_rating)
    
    orderby = self.request.get('$orderby', '')
    # The '-' represents reverse sort order
    if orderby == 'Title':
      movie_query.order('-title')
    elif orderby == 'ReleaseDate':
      movie_query.order('-year')
    else:
      movie_query.order('-rating')

    matched_count = movie_query.count(limit=MAX_NUM_MOVIES)
    
    return movie_query
    

def SmarterIntCast(value):
  if value:
    try:
      return int(value)
    except ValueError:
      return float(value)
  return 0  # Handle the empty string as zeroes
    
    
class DBInputHandler(webapp.RequestHandler):
  def post(self, id):
    """Fill the database with movies.
    
    TODO: Put behind admin password of some kind.
    """
    movie = Movie(rtid=self.request.get('rtid'),
                  title=self.request.get('title'),
                  year=SmarterIntCast(self.request.get('year')),
                  mpaa=self.request.get('mpaa'),
                  runtime=SmarterIntCast(self.request.get('runtime')),
                  rating=SmarterIntCast(self.request.get('rating')),
                  thumbnail=self.request.get('thumbnail'),
                  starring=self.request.get('starring'),
                  reviews=self.request.get('reviews'),
                  key_name=self.request.get('rtid'))
    movie.put()


application = webapp.WSGIApplication(
				     [('/', MainHandler),
				      ('/search\/?(.*)', SearchHandler),
				      ('/store\/?(.*)', DBInputHandler)],
				      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
