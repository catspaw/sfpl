from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

import os

# The SFPL only has so many movies.  Keeping an upper limit helps
# queries to run faster.
MAX_NUM_MOVIES = 6000

class MovieList(db.Model):
  timestamp = db.DateTimeProperty(auto_now_add=True)

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
    movies = []
    top = int(self.request.get('$top', 3))
    start = int(self.request.get('$skip', 0))

    movie_query = Movie.all()
    
    min_rating = self.request.get('$audiencerating', '0')
    # Convert stars (eg: 4.5) into RottenTomatoes percentage rating.
    min_rt_rating = int((float(min_rating) * 20) - 10)
    
    movie_query.filter('rating >=', min_rt_rating)
    
    if self.request.get('$orderby', '') == 'Rating':
      movie_query.order('-rating')  # reverse order sort for 'rating'

    matched_count = movie_query.count(limit=MAX_NUM_MOVIES)
    
    for movie in movie_query.run(offset=start, limit=top):
      movies.append(movie.toDict())
      
    data = {'metadata': {'matched_count': matched_count},
            'movies': movies}
    data = simplejson.dumps(data)
    self.response.out.write(data)


class MetaHandler(webapp.RequestHandler):
  def get(self, id):
    data = {"movies": 9, "mpaa": ["G", "PG", "PG 13", "R", "Unrated"]}
    data = simplejson.dumps(data)
    self.response.out.write(data)
    

def SmarterIntCast(value):
  if value:
    try:
      return int(value)
    except ValueError:
      return float(value)
  return 0  # Handle the empty string as zeroes
    
class DBInputHandler(webapp.RequestHandler):
  def post(self, id):
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
				      ('/meta\/?(.*)', MetaHandler),
				      ('/store\/?(.*)', DBInputHandler)],
				      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
