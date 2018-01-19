import facebook
import json
import requests
from datetime import datetime
import plotly.plotly as py
import plotly.graph_objs as go
import sqlite3


CACHE_FNAME = "facebook_cache.json"
#cache set up
try:
    cache_file = open(CACHE_FNAME,'r') #opening the file
    cache_contents = cache_file.read() #reading through the data
    cache_file.close() #closing
    CACHE_DICTION = json.loads(cache_contents) #loading data into a dict
except:
    CACHE_DICTION = {}

baseurl = "https://graph.facebook.com/v2.3/me/feed" # Baseurl with my data

## Building the Facebook parameters dictionary
url_params = {}
url_params["access_token"] = 'EAACEdEose0cBACIWuTFe2FswMVh6IWfjNM1Ta7tNw0MSsTHyZAgG536yJWlQJvHfu3ZCrhGQcFT4QfF41d9SuPKJGsxyZADd81E8GxZCj6ZBiGnEJNNhVb3EjVYGDt3ghlKRrBvJ3Hjbd5Qg5IDS59rBPvyZBVZCgt60ruKB9M2AkgEa4ZAWT0v56vZC7zn2E6vKiLyVawNmZCNwZDZD'
url_params["fields"] = "message,story,comments,likes,created_time,from"  #fields is accessing my posts which contains the information to help me index through the dicts and gather what I need
url_params["limit"] = 100 #getting 100 posts bc the defult is 25
user_id = '1035252473155524' #me


def get_facebook_posts(user): #checking if data is in the cache
	if user in CACHE_DICTION:
		print('using cache data')
		return CACHE_DICTION[user]
	else:
		print('getting data from internet') # getting data from the web if it isn't in the cache
		results = requests.get(baseurl, params=url_params) #making a facebook request by combining the baseurl and the params
		CACHE_DICTION[user] = json.loads(results.text) #loading into correct format
		f = open(CACHE_FNAME,'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close
	return results

facebook_posts = get_facebook_posts(user_id) #calling the function with my id and setting it to the value facebook_posts so that I can index through

conn = sqlite3.connect('facebook_data.sqlite') #creating the sqlite database
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Posts')
cur.execute('CREATE TABLE Posts (post_id TEXT, day TEXT, time_of_day TEXT)') #making the columns


for user in facebook_posts['data']: #this iterates through the dict data to grab the info we need for the sql table
    post_id = user['id'] #gets ids
    time_of_day = datetime.strptime(user['created_time'], '%Y-%m-%dT%H:%M:%S+0000') #this gets the time and converts with datetime and strptime method to make it readable
    day = time_of_day.strftime("%A") #this uses the time we created to get the exact day of the week
    tup = (post_id, day, time_of_day) #makes it easy to insert into the sql
    cur.execute("INSERT INTO Posts (post_id, day, time_of_day) VALUES(?,?,?)", tup) #puts the data into the sql

conn.commit()

global mon,tue,wed,thu,fri,sat,sun #using these values as counters and x values for the plotly graph

mon=0
tue=0
wed=0
thu=0
sat=0
fri=0
sun=0

cur = conn.cursor()
cur.execute("SELECT day FROM posts") #pulling data from the sql to use in upcoming for loop

rows = cur.fetchall() #grabs all data

for row in rows: #this for loop is suming up the days of the week based on the day, for example if a row has the word "Monday" it will add to mon
    if(row=='Monday'):
        mon=1+mon
    elif(row=='Tuesday'):
        tue=1+tue
    elif (row=='Wednesday'):
        wed=1 +wed
    elif (row=='Thursday'):
        thu=1 +thu
    elif (row=='Friday'):
        fri=1 +fri
    elif (row=='Saturday'):
        sat=1 +sat
    elif (row=='Sunday'):
        sun=1 +sun

def plot(mon,tue,wed,thu,fri,sat,sun): #using the counters made we can properly make a bar graph
    print("plotting graph")
    py.sign_in('autumnjacob', '9FDRtVCkJfArTQB9NMAi')
    trace1 = go.Bar(
        x = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        y = [mon,tue,wed,thu,fri,sat,sun],
        name = "Facebook Posts",
        marker = dict(
            color = ['rgba(255,0,255,0.9)', 'rgba(204,204,204,1)', #making the highest amount of posts stand out
               'rgba(204,204,204,1)', 'rgba(204,204,204,1)',
               'rgba(204,204,204,1)','rgba(204,204,204,1)','rgba(204,204,204,1)']),
        )
    data = [trace1] #x and y values
    layout = go.Layout(
    title='Which Days Do I Post the Most on Facebook?',
    xaxis=dict(
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    yaxis=dict(
        title='Posts per Day',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
     legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(124, 58, 182, 1)',
        bordercolor='rgba(124, 58, 182, 1)'
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1
)
    fig = go.Figure(data=data, layout=layout) #putting everything together formating with style
    py.iplot(fig, filename='Facebook Data')

plot(mon,tue,wed,thu,fri,sat,sun)
print ('copy the link below in your browser to see my pretty bar graph! \nhttps://plot.ly/~autumnjacob/2/which-days-do-i-post-the-most-on-facebook/')
