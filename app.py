import os
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

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Assuming MongoDB is running locally
db = client['spotify_playlists']
playlists_collection = db['playlists']
user_most_listened_to_songs_collection = db['most_listened_songs']
user_top_artists_collection = db['top_artists']
recommendations_collection = db['recommendations']

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
    context = {"playlists": p}
    return render_template("playlists.html", **context)

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
    ids = [item["id"] for item in data["items"]]
    artist_ids = ','.join(ids)

    # get recommendations with artist id as input
    response = get(f"https://api.spotify.com/v1/recommendations?seed_artists={artist_ids}&limit=30", headers=headers, timeout=10)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
