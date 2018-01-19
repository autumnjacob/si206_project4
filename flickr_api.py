import requests
import json
import sqlite3
from flickrapi import FlickrAPI
from pprint import pprint


flickr_public = 'd886a09e9dcd82ff028879ab5066b83c'
flickr_secret = '64e48884080e4079'

CACHE_FNAME = "flickr_cache.json"

try:
    cache_file = open(CACHE_FNAME,'r') #opening the file
    cache_contents = cache_file.read() #reading through the data
    cache_file.close() #closing
    CACHE_DICTION = json.loads(cache_contents) #loading data into a dict
except:
    CACHE_DICTION = {}



def get_flickr_photos(search): #checking if data is in the cache
    if search in CACHE_DICTION:
        print("using cache data")
        return CACHE_DICTION[search]
    else:
        print('getting data from internet') # getting data from the web if it isn't in the cache
        flickr = FlickrAPI(flickr_public, flickr_secret, format='parsed-json') #create correct base for access
        extras = 'date_taken, date_upload, owner, tags' #adding in all the info to gather
        puppy_search = flickr.photos.search(text= search, per_page=100, extras=extras) #syntax to search for photos, we want 100 photos
        photos = puppy_search['photos']['photo'] #indexing to filter unwanted data
        CACHE_DICTION[search] = photos
        f = open(CACHE_FNAME,'w') #writing into file
        f.write(json.dumps(CACHE_DICTION)) #dumping it
        f.close
    return photos

puppy_photos = get_flickr_photos(input('Search term:')) #calls the function to search

conn = sqlite3.connect('flickr_data.sqlite') #creating the sqlite database
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS photos')
cur.execute('''CREATE TABLE photos(username TEXT, title TEXT, tags TEXT)''')

for data in puppy_photos: #this iterates through the dict data to grab the info we need for the sql table
	username = data['owner'] #gets username
	title = data['title'] #gets photo title
	tags = data['tags'] #gets tags
	tup2 = (username, title, tags) #creating tuple to insert into table
	cur.execute('INSERT INTO photos (username, title, tags) VALUES(?, ?, ?)', tup2) #putting the data into the table which creates the rows for each column

conn.commit()
