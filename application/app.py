import oauth2
import json
import requests
import settings
from datetime import datetime
from datetime import timedelta
from flask import Flask, render_template, request
from pymongo import MongoClient
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('map.html', google_api_key=settings.GOOGLE_API_KEY)

@app.route('/api/')
def get_tweets_by_location():
    location = request.args.get('location')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    distance = request.args.get('distance')
    if not distance:
        distance = '70km'

    is_cached = check_cache_from_search(location, distance)
    if is_cached:
        tweets = get_tweets_from_cache(location, distance)
    else:
        store_search_data(location, distance)
        location_data = {
            'name': location,
            'lat': lat,
            'lng': lng
        }
        tweets = get_and_store_tweets(location_data, distance)
    return tweets

def oauth_req(url, key, secret, http_method='GET', post_body='', http_headers=None):
    consumer = oauth2.Consumer(key=settings.API_KEY, secret=settings.API_SECRET)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return json.loads(content)

def check_cache_from_search(location_name, distance):
    client = MongoClient('mongodb', 27017)
    db = client.twitter
    search_history = db.search_history
    cache_time = datetime.utcnow() - timedelta(hours=1)
    search_cache = search_history.find_one(
        {'$and': [
            {'timestamp': {
                '$gte': cache_time
                }
            },
            {'location': location_name},
            {'distance': distance}
        ]}
    )
    return search_cache != None


def get_and_store_tweets(location_data, distance):
    client = MongoClient('mongodb', 27017)
    db = client.twitter
    tweets = db.tweets
    url = 'https://api.twitter.com/1.1/search/tweets.json?q=%s&geocode=%s,%s,%s' % (location_data['name'], location_data['lat'], location_data['lng'], distance)
    results = oauth_req(url, settings.TOKEN_KEY, settings.TOKEN_SECRET)
    tweets_data = []
    for tweet in results['statuses']:
        if not tweet.has_key('retweeted_status'):
            tweet_data = {
                'text': tweet['text'],
                'location': location_data['name'],
                'distance': distance,
                'timestamp': datetime.utcnow()
            }
            tweets.insert(tweet_data)
            tweets_data.append(tweet['text'])
    return json.dumps(tweets_data)


def get_tweets_from_cache(location_name, distance):
    client = MongoClient('mongodb', 27017)
    db = client.twitter
    tweets = db.tweets
    results = tweets.find(
        {'$and': [
            {'location': location_name},
            {'distance': distance}
        ]}
    )
    data = []
    for item in results:
        data.append(item['text'])
    return json.dumps(data)

def store_search_data(location_name, distance):
    client = MongoClient('mongodb', 27017)
    db = client.twitter
    search_history = db.search_history
    search_data = {
        'location': location_name,
        'distance': distance,
        'timestamp': datetime.utcnow()
    }
    search_history.insert(search_data)
