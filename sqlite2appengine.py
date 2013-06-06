#!/usr/bin/python

"""Takes the data in the sqlite db, and stores it in app engine."""

APPENGINE_DB_LOADER = 'http://localhost:8085/store'

import urllib
import urllib2
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx].encode('utf-8')
    return d

def SaveToAppEngine(movie):
  data = urllib.urlencode(movie)
  u = urllib2.urlopen(APPENGINE_DB_LOADER, data)
  u.read()  # Let the connection complete
  u.close()
  

def GrabMovies():
  conn = sqlite3.connect('sfpl.db')
  conn.row_factory = dict_factory
  c = conn.cursor()
  result = c.execute('SELECT * FROM movies WHERE rtid IS NOT NULL')
  movie = result.fetchone()
  while movie:
    SaveToAppEngine(movie)
    movie = result.fetchone()

if __name__ == '__main__':
  GrabMovies()