import requests
from requests.utils import quote
import json
import re
import sqlite3


CACHE_FNAME = 'cache.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    # CACHE_DICTION = cache_contents
    cache_file.close()
except:
    CACHE_DICTION = {}

# Retrieves album information from itunes API

# TODO: Get API access to work
def getAlbumWith(personName):
    rurl = requestURL('https://itunes.apple.com/search', params={'term': personName,   'entity': 'album'})
    if rurl in CACHE_DICTION:
        response_text = CACHE_DICTION[rurl]
    else:
        response = requests.get(rurl)

    response_dictionary = json.loads(response.text)

    return response_dictionary


# Gets info from cache if prior searched, else get from API
def getWithCaching(artist):
    try:
        with open('itunesCache.json', 'r') as file:
            data = json.loads(file.read())
            if artist in data.keys():
                return data[artist]
    except:
        print ("fetching from the web")

    # If data not in cache file
    BASE_URL = 'https://itunes.apple.com/search'
    data = requests.get('https://itunes.apple.com/search', params={'term': artist, 'entity': 'album'}).json()
    with open('itunesCache.json', 'w') as file:
        file.write(json.dumps({ artist : data}))

    return data


# Sorts albums by release data
def Most_Recent_Album(d):
    # look at output from iTunes API and sort accordingly
    alphabetized_keys = sorted(d.keys())
    res = []
    for k in alphabetized_keys:
        res.append((k, d[k]))
    return res

def canonical_order(d):
    alphabetized_keys = sorted(d.keys())
    res = []
    for k in alphabetized_keys:
        res.append((k, d[k]))
    return res

def requestURL(baseurl, params = {}, input_headers = {}):
    req = requests.Request(method = 'GET', url = baseurl, params = canonical_order(params), headers=input_headers)
    prepped = req.prepare()
    return prepped.url

############################################### My classes ###########################################################
class Artist:
    track_count = 0
    #self.time_between_album = 0
    def __init__(self, artist_name):
        self.name = artist_name
        self.albums = []

    def __str__(self):
        return self.name

    def sum_tracks(self):
        for album in self.albums:
            self.track_count += album.get_track_count()
    def get_track_count(self):
        return self.track_count

    def get_name(self):
        return self.name

# Get user artist input
input = input("Please enter an artist to search for: ")
# TODO: set later
artist = Artist(input)
# Get artist albums from itunes api
artist_api_data = getWithCaching(artist.get_name())

conn = sqlite3.connect('itunes_data.sqlite') #creating the sqlite database
cur = conn.cursor()


cur.execute('DROP TABLE IF EXISTS artist')
cur.execute('CREATE TABLE artist (album_name TEXT, release_date TEXT, track_count INTEGER)')

for result in artist_api_data['results']:
    album_name = result['collectionName']
    release_date = result['releaseDate']
    track_count = result['trackCount']
    tup = (album_name, release_date, track_count)
    cur.execute('INSERT INTO artist (album_name, release_date, track_count) VALUES(?, ?, ?)', tup)


conn.commit()
