#!/usr/bin/python

import json
import sqlite3
import urllib
import urllib2

API_KEY = 'udtyzh6dr22gm7mxntmfsw8h'

class RottenTomatoData(object):
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
  def __init__(self):
    self.conn = sqlite3.connect('sfpl.db')
    
  def next(self):
    c = self.conn.cursor()
    result = c.execute("SELECT * FROM movies WHERE rtid IS NULL;")
    movie = result.fetchone()
    
    page = rt.scrape(movie[0])  # title
    rtd = RottenTomatoData(page)
    
    movie_title = movie[0].replace('"', '""') # sqlite needs double quotes 
    if not rtd.db_change:
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
  rt = Query()
  
  filler = FindAndFillDB()
  for i in range(5000):
    filler.next()
  
