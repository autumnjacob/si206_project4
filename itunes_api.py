import requests
import json
import sqlite3


CACHE_FNAME = 'itunes_cache.json'

def get_with_caching(artist):
    try:
        with open('itunes_cache.json', 'r') as file: #opening the file
            data = json.loads(file.read()) #reading through the data
            if artist in data.keys(): #looping through key values to see if information is present
                print ('using cache data')
                return data[artist]
    except:
        print ('getting data from internet') #if data is not there we make a request to the url

    # If data not in cache file
    BASE_URL = 'https://itunes.apple.com/search' #setting baseurl
    data = requests.get(BASE_URL, params={'term': artist, 'entity': 'album', 'limit': 100}).json() #adding in params, search limit and formating
    with open('itunes_cache.json', 'w') as file: #writing in file
        file.write(json.dumps({ artist : data}))

    return data

# Get artist albums from itunes api
artist_api_data = get_with_caching('Frank Zappa')

conn = sqlite3.connect('itunes_data.sqlite') #creating the sqlite database
cur = conn.cursor()


cur.execute('DROP TABLE IF EXISTS artist')
cur.execute('CREATE TABLE artist (album_name TEXT, release_date TEXT, track_count INTEGER)')


for result in artist_api_data['results']: #this iterates through the dict data to grab the info we need for the sql table
    album_name = result['collectionName'] #gets album names
    release_date = result['releaseDate'] #gets release dates
    track_count = result['trackCount']
    tup = (album_name, release_date, track_count) #easy to insert into sql table
    cur.execute('INSERT INTO artist (album_name, release_date, track_count) VALUES(?, ?, ?)', tup) #putting data into each column
conn.commit()

conn.close()
