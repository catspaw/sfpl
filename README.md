A demo of a superior web interface to the movies available at the SFPL (San Francisco Public Library).

You can see the original interface here: http://sfpl.org

There are two parts to the files in this repo:
    1) A set of scripts that build up the database of movies.
    2) A Google App Engine web interface to those movies.
 
All of the scripts in #1 are required because we don't have actual access to the SFPL database.

Here's how they work.

Scrape movies from the SFPL website.

    cd scripts/
    touch sfpl.db
    python SFPLScraper.py

The next step is to take the titles from the SFPL website, and collect information about each of the movies.

We temporarily store this information into an sqlite database, because the next step requires several days to complete, due to the API limits of the Rotten Tomatoes API.

    python RottenTomatoes.py

At some point, this command will fail due to the API limit having been reached.  Wait a day and try again, until complete.

Finally, upload this data to the App Engine datastore.

    python sqlite2appengine.py

Note that this command can be run at any point during the RottenTomatoes.py lifecycle.  Duplicates will not be added to the App Engine datastore.  In that way, you can populate the sqlite database with some Rotten Tomatoes data, work on the website, and then populate it with more on another day.

Also, due to the way that App Engine datastores work, you can use the same sqlite database to fill your local App Engine datastore, or to fill a production one.  See sqlite2appengine.py to configure the server that the data is uploaded to.

Lastly, to run the server itself, either begin an instance on App Engine servers, or run a local App Engine Launcher.  That app can be found here: http://developers.google.com/appengine/downloads