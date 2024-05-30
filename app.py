import os

import requests
from requests import post, get
import json
import urllib.parse
import datetime
from flask import Flask, redirect, request, jsonify, session, render_template
import flask
from pymongo import MongoClient

app = Flask(__name__)

client_id = '36b258fc1e66468eb7b030418e2363c0'
client_secret = 'e1dd5b9ba7884a8ea1480c474e579200'
app.secret_key = 'hsjking0403@naver.com'
""" --------------------------------------------------------------------------------------------------------- """

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Assuming MongoDB is running locally

db_user = client['user_spotify_info']
db_recommend=client['recommendation_info']

# db
playlists_collection = db_user['playlists'] # user's playlist collection

user_most_listened_to_songs_collection = db_user['most_listened_songs'] # user's most listened songs collection

user_top_artists_collection = db_user['top_artists'] # user's most listened to artists collection

top_tracks_collection=db_recommend['top_tracks'] # global_top_tracks collection

kr_top_collection=db_recommend['kr_top_tracks'] # korea_top_tracks collection

global_latest_tracks_collection=db_recommend['global_latest_tracks'] # worldwide latest track collection

recommendations_collection = db_recommend['recommendations'] # recommended songs collection


""" 
#  database 2 (user_spotify_info, recommendation_info) + collection 7

# 1 user_spotify_info

# 1.1 playlists_collection
# 1.2 user_most_listened_to_songs_collection
# 1.3 user_top_artists_collection

# 2. recommendation_info

# 2.1 recommendations_collection
# 2.2 top_tracks_collection
# 2.3 kr_top_collection
# 2.4 global_latest_tracks_collection
"""


""" --------------------------------------------------------------------------------------------------------- """

@app.route('/')
def index():
    """Index page of app"""
    # return "See Spotify Data <a href='/login'> Login with Spotify </a>"
    return flask.render_template("index.html")


@app.route('/login')
def login():
    """Login request"""
    # Spotify API에 로그인하기 위한 인증 코드를 요청합니다. 사용자는 승인 후 애플리케이션으로 다시 리디렉션
    scope = "user-read-recently-played user-top-read user-library-read user-read-private user-read-email user-follow-read"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': 'http://localhost:5000/callback',
        'show_dialog': 'True'
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

    # http://localhost:5000/callback?error=access_denied경우 index.html로 이동
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle login response"""
    # 로그인 후 Spotify에서 전달된 인증 코드를 받아 액세스 토큰을 요청하고, 토큰을 세션에 저장

    # if there is an error
    if 'error' in request.args:
        return flask.render_template("index.html")

    if 'code' in request.args:
        body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/callback',
            'client_id': client_id,
            'client_secret': client_secret
        }

        # get request
        url = "https://accounts.spotify.com/api/token"
        response = post(url, data=body)
        token_info = response.json()

        # store important info
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires'] = datetime.datetime.now().timestamp() + token_info['expires_in']

        return redirect('/home')


@app.route('/home')
def home_page():

    """Landing page"""
    # 사용자의 액세스 토큰이 있는지 확인하고 만료되지 않았는지 확인한 후, 메인 페이지를 렌더링
    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    return flask.render_template("landing.html")


@app.route('/playlists')
def get_playlists():
    """Get playlists"""
    #사용자의 플레이리스트를 가져와 템플릿에 표시

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    # url = "https://api.spotify.com/v1/me/playlists"

    response = get("https://api.spotify.com/v1/me/playlists", headers=headers)
    playlists = response.json()
    p=[]
    for playlist in playlists['items']:
        name = playlist['name']
        images = []

        # Check if images exist and are iterable
        if 'images' in playlist and playlist['images']:
            images = [image['url'] for image in playlist['images'] if 'url' in image]

        # Check if playlist already exists in MongoDB
        existing_playlist = playlists_collection.find_one({'name': name, 'images': images})

        # Append playlist info for template rendering
        p.append({
            'name': name,
            'images': images
        })

        if existing_playlist:
            # Playlist already exists, skip insertion
            continue
        else:
            # Playlist does not exist, insert into MongoDB
            playlists_collection.insert_one({
                'name': name,
                'images': images
            })
    # Retrieve all playlists from MongoDB for rendering
    return render_template("playlists.html", playlists=p)

@app.route('/songs')
def get_songs():
    """Get top songs"""
    # 사용자의 인기 트랙을 가져와 템플릿에 표시

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    # url = "https://api.spotify.com/v1/me/top/tracks"

    response = get("https://api.spotify.com/v1/me/top/tracks", headers=headers, timeout=10)
    data = response.json()
    # Extract information for each track and store in MongoDB
    tracks_info = []
    for item in data['items']:  # Iterate over the 'items' key in 'data'
        track_name = item['name']
        artist_name = item['artists'][0]['name']

        # Check if 'images' key exists for the album of the track
        if 'images' in item['album']:
            album_images = [image['url'] for image in item['album']['images'] if image['height'] == 300 and image['width'] == 300]
        else:
            album_images = []

        preview_url = item['preview_url']

        # Check if track_info already exists in MongoDB
        existing_track = user_most_listened_to_songs_collection.find_one({
            'track_name': track_name,
            'artist_name': artist_name
        })

        if existing_track:
            # If track_info already exists in MongoDB, use the existing data
            track_info = existing_track
        else:
            # If track_info does not exist in MongoDB, create a new track_info dictionary
            track_info = {
                'track_name': track_name,
                'artist_name': artist_name,
                'album_images': album_images,
                'preview_url': preview_url
            }
            # Insert track_info into MongoDB collection
            user_most_listened_to_songs_collection.insert_one(track_info)

        # Append track_info to tracks_info list
        tracks_info.append(track_info)

    return render_template("songs.html", tracks_info=tracks_info)


@app.route('/artists')
def get_artists():

    """Get top artists"""
    # 사용자의 인기 아티스트를 가져와 템플릿에 표시

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = get("https://api.spotify.com/v1/me/top/artists", headers=headers, timeout=10)
    data = response.json()
    artists_info = []

    for item in data.get("items", []):
        name = item.get("name", "")
        genres = item.get("genres", [])
        image_320_url = next((img.get("url") for img in item.get("images", []) if img.get("height") == 320), "")

        if name and genres and image_320_url:
            artist_doc = {
                "name": name,
                "genres": genres,
                "image_320_url": image_320_url
            }

            # Check if artist already exists in MongoDB to avoid duplicates
            existing_artist = user_top_artists_collection.find_one({"name": name})
            if not existing_artist:
                # Insert new artist info into MongoDB
                user_top_artists_collection.insert_one(artist_doc)
                artists_info.append(artist_doc)
            else:
                artists_info.append(existing_artist)
    return render_template("artists.html", artists_info=artists_info)
@app.route('/global_top_tracks')
def global_top_tracks():
    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    # Send the HTTP GET request to the Spotify API for the top tracks
    response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks?limit=10',
                            headers=headers)
    top_tracks = response.json()['items']
    recommend_info = []

    for track in top_tracks:
        # Extract track details
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        album_image_url = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
        release_date = track['track']['album']['release_date']  # Extract release date

        # Prepare recommendation data to be stored
        recommendation_data = {
            "artist_name": artists,
            "track_name": track_name,
            "album_image_url": album_image_url,
            "release_date": release_date,
        }
        # 데이터 중복 확인
        existing_data = top_tracks_collection.find_one({
            "artist_name": recommendation_data["artist_name"],
            "track_name": recommendation_data["track_name"]
            # 이 외에도 필요한 조건을 추가할 수 있습니다 (예: release_date 등)
        })

        if existing_data is None:
            # MongoDB에 저장
            top_tracks_collection.insert_one(recommendation_data)
        # Add to recommend_info list for rendering
        recommend_info.append(recommendation_data)

    return render_template("global_top_tracks.html", recommend_info=recommend_info)


@app.route('/global_and_kr_tendency')
# global_and_kr_tendcy
def global_and_kr_tendency():
    """Get recommended songs"""
     # 사용자의 인기 아티스트를 기반으로 추천 음악을 가져와 템플릿에 표시

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # 인기곡 -대한 민국(주간)
    response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbJZGli0rRP3r/tracks?limit=20', headers=headers)
    top_tracks_kr = response.json()['items']


    # 국내외 신곡들 (매주 업데이트)
    response_2 = requests.get('https://api.spotify.com/v1/playlists/37i9dQZF1DXdlsL6CGuL98/tracks?limit=20', headers=headers)
    recent_tracks = response_2.json()['items']

    top_tracks_kr_info=[]
    recent_tracks_info=[]

    for track in top_tracks_kr:
        # Extract track details
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        album_images = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
        preview_url = track['track']['preview_url']
        release_date = track['track']['album']['release_date']

        data_kr=({
            'track_name': track_name,
            'artists': artists,
            'album_image': album_images,
            'preview_url': preview_url,
            'release_date': release_date
        })
        # MongoDB에 중복 삽입 방지
        if not kr_top_collection.find_one({'track_name': track_name, 'artists': artists}):
            kr_top_collection.insert_one(data_kr)
        # Add to recommend_info list for rendering
        top_tracks_kr_info.append(data_kr)



    for track in recent_tracks:
        # Extract track details
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        album_images = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
        preview_url = track['track']['preview_url']
        release_date = track['track']['album']['release_date']

        data_recent_tracks=({
            'track_name': track_name,
            'artists': artists,
            'album_image': album_images,
            'preview_url': preview_url,
            'release_date': release_date
        })
        # MongoDB에 중복 삽입 방지
        if not global_latest_tracks_collection.find_one({'track_name': track_name, 'artists': artists}):
            global_latest_tracks_collection.insert_one(data_recent_tracks)
        # Add to recommend_info list for rendering
        recent_tracks_info.append(data_recent_tracks)
    return render_template("global_and_kr_tendency.html", recent_tracks_info=recent_tracks_info, top_tracks_kr_info=top_tracks_kr_info)



@app.route('/recommendations')
def get_recommendations():

    """Get recommended songs"""
     # 사용자의 인기 아티스트를 기반으로 추천 음악을 가져와 템플릿에 표시

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # get seed artist ids
    response = get("https://api.spotify.com/v1/me/top/artists?limit=5", headers=headers, timeout=10)
    data = response.json()

    if data['total'] == 0: # Check if no artists were found
        # Send the HTTP GET request to the Spotify API for the top tracks
        response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks?limit=10', headers=headers)
        top_tracks = response.json()['items']
        recommend_info = []

        for track in top_tracks:
            # Extract track details
            track_name = track['track']['name']
            artists = [artist['name'] for artist in track['track']['artists']]
            album_image_url = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
            release_date = track['track']['album']['release_date']  # Extract release date

            # Prepare recommendation data to be stored
            recommendation_data = {
                "artist_name": artists,
                "track_name": track_name,
                "album_image_url": album_image_url,
                "release_date":release_date,
            }

            # 데이터 중복 확인
            existing_data = top_tracks_collection.find_one({
                "artist_name": recommendation_data["artist_name"],
                "track_name": recommendation_data["track_name"]
                # 이 외에도 필요한 조건을 추가할 수 있습니다 (예: release_date 등)
            })

            if existing_data is None:
                # MongoDB에 저장
                top_tracks_collection.insert_one(recommendation_data)

            # Add to recommend_info list for rendering
            recommend_info.append(recommendation_data)

        return render_template("global_top_tracks.html", recommend_info=recommend_info)

    ids = [item["id"] for item in data["items"]]
    artist_ids = ','.join(ids)

    # get recommendations with artist id as input
    response = get(f"https://api.spotify.com/v1/recommendations?seed_artists={artist_ids}&limit=100", headers=headers,timeout=10)
    recommendations = response.json()
    recommend_info = []


    # Assuming 'recommendations' is the JSON response from Spotify API
    for track in recommendations['tracks']:
        artists = ", ".join([artist['name'] for artist in track['artists']])
        track_name = track['name']
        preview_url = track['preview_url']
        album_image_url = track['album']['images'][0]['url']

        if preview_url is not None:
            # Check if the recommendation already exists in MongoDB
            if not recommendations_collection.find_one({
                "artist_name": artists,
                "track_name": track_name
            }):
                # Prepare recommendation data to be stored
                recommendation_data = {
                    "artist_name": artists,
                    "track_name": track_name,
                    "preview_url": preview_url,
                    "album_image_url": album_image_url
                }
                # Add to recommend_info list for rendering
                recommend_info.append(recommendation_data)
                # Insert into MongoDB to avoid duplicates
                recommendations_collection.insert_one(recommendation_data)
    return render_template("recommendations.html", recommend_info=recommend_info)


@app.route('/refresh-token')
def refresh_token():

    """Refresh access token once it has expired"""
    # 토큰의 만료 기간이 지났을 때 자동으로 토큰을 갱신.

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = get("https://accounts.spotify.com/api/token", data=body)
        new_info = response.json()

        session['access_token'] = new_info['access_token']
        session['expires'] = datetime.datetime.now().timestamp() + new_info['expires_in']
        return redirect('/playlists')


@app.route("/checkLayout")
def checkLayout():
    return render_template("main.html")

@app.route("/check")
def check():
    return render_template("playlist.html")

@app.route("/songlist")
def songlist():
    return render_template("songlist.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
