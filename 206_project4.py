import requests
import json
import facebook
import datetime
import sqlite3

facebook_access_token = "EAACEdEose0cBAHb72LYCqTyA8qUCMMyAfug4HY8RqV4KZBe2cvPdDFt5W24Azn1Cnc77zpVlDXb5ZCL5MsGRlBanZC8MZAB3XFoH3vKrQFcIefRlHz0B1V4e8zMu9iCVtpjgMZC0Q9gk6WnFwohSYB7mnfobZAHXSJnTCSZCZBoi88ZCFvuq1ToGMlyZBLp6QbcmAZD"


baseurl = "https://graph.facebook.com/v2.3/me/feed"

url_params = {}
url_params["access_token"] = facebook_access_token
url_params["fields"] = "message,story,comments,likes,created_time,from"
url_params["limit"] = 25


CACHE_FNAME = "facebook_cache.json"
# Put the rest of your caching setup here:
try:
    cache_file = open(CACHE_FNAME,'r') #opening the file
    cache_contents = cache_file.read() #reading through the data
    cache_file.close() #closing
    CACHE_DICTION = json.loads(cache_contents) #loading data into a dict
except:
    CACHE_DICTION = {}

def get_facebook_data(data): #checking if data is in the cache
	if data in CACHE_DICTION:
        print ("using data from cache")
        r = CACHE_DICTION[data]
	else:
        print('getting data from internet') # getting data from the web if it isn't in the cache
        r = requests.get(baseurl,params=url_params) #all the data unfilltered 
        CACHE_DICTION[data] = r
        f = open(CACHE_FNAME,'w')
        f.write(json.dumps(CACHE_DICTION))
        f.close
    return r
