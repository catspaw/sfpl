from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

import os

class MovieList(db.Model):
  timestamp = db.DateTimeProperty(auto_now_add=True)

class Movie(db.Model):
  rtid = db.StringProperty()
  title = db.StringProperty()
  year = db.StringProperty()
  mpaa = db.StringProperty()
  runtime = db.StringProperty()
  rating = db.StringProperty()
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
    for movie in Movie.all()[start:start+top]:
      movies.append(movie.toDict())
    movies = simplejson.dumps(movies)
    self.response.out.write(movies)


class MetaHandler(webapp.RequestHandler):
  def get(self, id):
    data = {"movies": 9, "mpaa": ["G", "PG", "PG 13", "R", "Unrated"]}
    data = simplejson.dumps(data)
    self.response.out.write(data)
    
    
class DBInputHandler(webapp.RequestHandler):
  def post(self, id):
    movie = Movie(rtid=self.request.get('rtid'),
                  title=self.request.get('title'),
                  year=self.request.get('year'),
                  mpaa=self.request.get('mpaa'),
                  runtime=self.request.get('runtime'),
                  rating=self.request.get('rating'),
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
