#!/usr/bin/python

"""Fills the database with RottenTomatos movies data.

Expects the database to contain rows with only a 'title' field (grabbed from
the SFPL database, see: SFPLScraper.py).  For each of these, looks up the
movie data about this film on RottenTomatoes.

IMPORTANT: This script deletes the movie row if no data can be found about
that film. 
"""

import json
import sqlite3
import urllib
import urllib2

API_KEY = 'udtyzh6dr22gm7mxntmfsw8h'

MAX_CAPACITY = 5000   # Rotten Tomatos API only allows so many calls per day

SFPL_DB = 'sfpl.db'  # sqlite3 database


class RottenTomatoData(object):
  """Given JSON blob of movie info, create a dict of db columns to update."""
  def __init__(self, jsonpage):
    data = json.loads(jsonpage)
    self.db_change = {}
    
    if data['movies']:
      self.parse(data['movies'][0])

  def parse(self, data):
    # Warning: parsing the data this way sets ourselves up to be sql-injection
    # attacked by Rotten Tomatoes.  Let's assume that's not a risk. :)
    db_change = {}
    db_change['rtid'] = data['id']
    db_change['year'] = data['year']
    db_change['mpaa'] = data['mpaa_rating']
    db_change['runtime'] = data['runtime']
    db_change['rating'] = data['ratings']['audience_score']
    db_change['thumbnail'] = data['posters']['thumbnail']
    
    cast = data['abridged_cast']
    db_change['starring'] = ', '.join([actor['name'] for actor in cast])
    
    db_change['reviews'] = data['links']['reviews']
    self.db_change = db_change
    

class Query(object):
  """Perform web query against the RottenTomato API."""
  def __init__(self):
    self.search_url = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json?apikey=%(apikey)s&q=%(query)s&page_limit=1'
    
  def scrape(self, query):
    params = {'apikey': API_KEY,
              'query': urllib.quote(query.encode('utf8')),
             }
    req = urllib2.Request(self.search_url % params)
    response = urllib2.urlopen(req)
    # TODO: handle errors
    data = response.read()
    return data


class FindAndFillDB(object):
  """Find rows in the DB that need RT data, and update with data from RT API."""
  def __init__(self, rt_query):
    self.conn = sqlite3.connect(SFPL_DB)
    self.rt_query = rt_query
    
  def next(self):
    c = self.conn.cursor()
    result = c.execute("SELECT * FROM movies WHERE rtid IS NULL;")
    movie = result.fetchone()
    
    page = self.rt_query.scrape(movie[0])  # title
    rtd = RottenTomatoData(page)
    
    movie_title = movie[0].replace('"', '""') # sqlite needs double quotes 
    if not rtd.db_change:
      # We couldn't find any data about this film.  The SFPL knows about it,
      # but Rotten Tomatoes doesn't.  Delete the movie.
      sql_statement = "DELETE FROM movies "
    else:
      sql_statement = "UPDATE movies SET "
      for key,value in rtd.db_change.items():
        value = str(value).replace('"', '\'')  # sub double-quote with single
        sql_statement += key + '="' + value + '", '
      sql_statement += 'title="%s" ' % (movie_title)
      
    sql_statement += 'WHERE title="%s"' % (movie_title)
    
    print sql_statement
    result = c.execute(sql_statement)
    self.conn.commit()


if __name__ == '__main__':
  filler = FindAndFillDB(Query())
  for i in range(MAX_CAPACITY):
    filler.next()
  
