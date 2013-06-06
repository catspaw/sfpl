#!/usr/bin/python

import urllib2
import re
import sqlite3

class HTMLToDVDs(object):
  """Given search results pages, rip the DVD information.
  
  Note: the SFPL library HTML is so poor that BeautifulSoup does not properly
  parse the page and drops most of the DVD links.
  """
  def __init__(self):
    # Find all links on the page whose href starts with '/search~S1'
    # then traverse until the > tag is closed.  Then traverse that tag.
    # Lastly, the titles come out like this:
    #  The Lion King [videorecording] / produced by Disney ...
    # so we stop once we see the [videorecording] tag.
    self.regex = '<a href="/search~S1[^>]*>(.*?) \\[videorecording\\]'
  
  def grab(self, page):
    links = re.findall(self.regex, page)
    for i in range(len(links)):
      links[i] = links[i].decode('utf8', 'ignore')
    return links


class SFPLScraper(object):
  """Scrapes the DVDs from the SFPL database."""

  def __init__(self):
    # Using search term 'a' as that seems to select most movies.
    self.search_term = 'a'
    
    # Requires a search term, start and end indexes
    self.search_url = 'http://sflib1.sfpl.org/search~S1?/Xa&searchscope=1&p=&m=g&Da=&Db=&SORT=D/Xa&searchscope=1&p=&m=g&Da=&Db=&SORT=D&SUBKEY=%(search_term)s/%(start)s,%(end)s,%(end)s,B/browse'
    
  def scrape(self, start):
    """Given a start index, scrape a page of DVDs and return HTML page."""
    params = {'search_term': self.search_term,
              'start': start,
              'end': start + 12  # 12 max results
             }
    req = urllib2.Request(self.search_url % params)
    response = urllib2.urlopen(req)
    # TODO: handle errors
    data = response.read()
    return data


class DBWriter(object):
  def __init__(self):
    self.conn = sqlite3.connect('sfpl.db')
    
  def write(self, movies):
    c = self.conn.cursor()
    
    # Convert [title, title, title] into [[title], [title], ...]
    movies = [[movie] for movie in movies]
    
    c.executemany('INSERT INTO movies VALUES (?)', movies)
    self.conn.commit()
    

if __name__ == '__main__':
  scraper = SFPLScraper()
  ripper = HTMLToDVDs()
  db = DBWriter()
  
  index = 12
  while True:
    print index
    page = scraper.scrape(index)
    movies = ripper.grab(page)
    if not movies:
      print 'Movies list empty.'
      break
    for movie in movies:
      print movie
    db.write(movies)
    index += 12