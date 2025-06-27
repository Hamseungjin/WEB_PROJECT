import os
import requests
from requests import post, get
import json
import urllib.parse
import datetime
from flask import Flask, redirect, request, jsonify, session, render_template
import flask
from pymongo import MongoClient
from chat import get_response
from bson.objectid import ObjectId

app=Flask(__name__)
""" --------------------------------------------------------------------------------------------------------- """
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
app.secret_key = os.getenv("secret_key")
""" --------------------------------------------------------------------------------------------------------- """

# MongoDB connection setup
import os
# Docker 환경에서는 서비스 이름을 사용, 로컬 환경에서는 localhost 사용
mongo_host = os.getenv('MONGO_HOST', 'mongodb')
client = MongoClient(f'mongodb://{mongo_host}:27017/')

db_user = client['user_spotify_info']
db_recommend=client['recommendation_info']
db_review = client['review_info']

# db
playlists_collection = db_user['playlists'] # user's playlist collection

user_most_listened_to_songs_collection = db_user['most_listened_songs'] # user's most listened songs collection

user_top_artists_collection = db_user['top_artists'] # user's most listened to artists collection

top_tracks_collection=db_recommend['top_tracks'] # global_top_tracks collection

kr_top_collection=db_recommend['kr_top_tracks'] # korea_top_tracks collection

global_latest_tracks_collection=db_recommend['global_latest_tracks'] # worldwide latest track collection

recommendations_collection = db_recommend['recommendations'] # recommended songs collection

review_collection = db_review['review']


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

@app.get("/")
def index_get():
    return render_template("start.html")

@app.route('/test')
def test_api():
    """API 테스트용 라우트"""
    if 'access_token' not in session:
        return "로그인이 필요합니다. <a href='/login'>로그인</a>"
    
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    
    test_results = {}
    
    # 1. 사용자 정보 테스트
    try:
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        test_results['user_info'] = response.json()
    except Exception as e:
        test_results['user_info'] = f"오류: {e}"
    
    # 2. 여러 플레이리스트 테스트
    playlist_ids = [
        ('37i9dQZEVXbMDoHDwVN2tF', 'Global Top 50'),  # 글로벌 톱 50
        ('37i9dQZF1DXcBWIGoYBM5M', 'Today\'s Top Hits'),  # 오늘의 인기곡
        ('37i9dQZF1DX0XUsuxWHRQd', 'RapCaviar'),  # 랩 플레이리스트
        ('4rOoJ6Ffppi7wEeAhRMynV', 'Test Playlist')  # 테스트용
    ]
    
    for playlist_id, name in playlist_ids:
        try:
            response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=3', headers=headers)
            result = response.json()
            test_results[f'playlist_{name}'] = {
                'status': response.status_code,
                'has_items': 'items' in result and len(result.get('items', [])) > 0,
                'error': result.get('error'),
                'first_track': result.get('items', [{}])[0].get('track', {}).get('name', 'No track') if result.get('items') else 'No items'
            }
        except Exception as e:
            test_results[f'playlist_{name}'] = f"오류: {e}"
    
    # 3. 사용자 상위 트랙 테스트 (Free 계정 제한)
    try:
        response = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=5', headers=headers)
        test_results['user_top_tracks'] = response.json()
    except Exception as e:
        test_results['user_top_tracks'] = f"오류: {e}"
    
    return f"<pre>{json.dumps(test_results, indent=2, ensure_ascii=False)}</pre>"

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    
    # 입력 유효성 검사
    if not text or len(text.strip()) == 0:
        return jsonify({"answer": "메시지를 입력해주세요!"})
    
    if len(text) > 1000:
        return jsonify({"answer": "메시지가 너무 깁니다. 1000자 이하로 입력해주세요."})
    
    # Gemma-3-4b-it 모델로 응답 생성
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

@app.post("/chat/clear")
def clear_chat_history():
    """챗봇 대화 기록 초기화"""
    try:
        from chat import music_chatbot
        music_chatbot.clear_history()
        return jsonify({"status": "success", "message": "대화 기록이 초기화되었습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"초기화 중 오류가 발생했습니다: {str(e)}"})

@app.get("/chat/status")
def chat_status():
    """챗봇 상태 확인"""
    try:
        from chat import music_chatbot
        is_model_loaded = music_chatbot.model is not None
        device_info = music_chatbot.device if hasattr(music_chatbot, 'device') else "Unknown"
        conversation_count = len(music_chatbot.conversation_history) if hasattr(music_chatbot, 'conversation_history') else 0
        
        return jsonify({
            "status": "success",
            "model_loaded": is_model_loaded,
            "device": device_info,
            "conversation_turns": conversation_count // 2,  # 사용자/봇 페어의 수
            "model_name": "Gemma-3-4b-it" if is_model_loaded else "Fallback Mode"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"상태 확인 중 오류: {str(e)}"})

@app.route('/login')
def login():
    """Login request"""
    # Spotify API에 로그인하기 위한 인증 코드를 요청합니다. 사용자는 승인 후 애플리케이션으로 다시 리디렉션
    scope = "user-read-recently-played user-top-read user-library-read user-read-private user-read-email user-follow-read"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': 'https://127.0.0.1:5000/callback',
        'show_dialog': 'True'
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

    # http://localhost:5000/callback?error=access_denied경우 index.html로 이동
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """로그인 응답 처리"""
    # 콜백에서 오류가 있는지 확인
    if 'error' in request.args:
        # 오류 처리 (예: 사용자가 승인을 거부한 경우)
        return flask.render_template("start.html", error="Authorization failed.")

    # 사용자가 로그인한 후 응답 처리
    if 'code' in request.args:
        body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://127.0.0.1:5000/callback',
            'client_id': client_id,
            'client_secret': client_secret
        }

        # 코드를 액세스 토큰으로 교환
        url = "https://accounts.spotify.com/api/token"
        response = post(url, data=body)
        token_info = response.json()

        # 토큰과 만료 시간을 세션에 저장
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires'] = datetime.datetime.now().timestamp() + token_info['expires_in']

        # Spotify로부터 사용자 정보 가져오기
        user_info = get_user_info()

        # 구독자 여부 확인
        return verify_subscription(user_info)

    return redirect('/')


def get_user_info():
    """Spotify로부터 사용자 정보 가져오기"""
    if 'access_token' not in session or datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/login')

    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = get("https://api.spotify.com/v1/me", headers=headers)
    return response.json()


def verify_subscription(user_info):
    """로그인한 사용자가 유료 구독자인지 확인"""
    if 'access_token' not in session or datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/login')

    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
    data = response.json()

    # 데이터에 상위 트랙이 있는지 확인하여 유료 구독자인지 확인
    if not data.get('items'):
        # 상위 트랙이 없으면 사용자가 유료 구독자가 아닐 수 있음
        session['is_subscriber'] = False
    else:
        # 데이터가 있으면 사용자가 유료 구독자임
        session['is_subscriber'] = True

    # 사용자가 관리자(admin)인지 확인 (예: 이메일로 확인)
    if user_info['email'] == 'a01079072289@gmail.com':  # 관리자 이메일로 변경
        session['is_admin'] = True
    else:
        session['is_admin'] = False

    return redirect('/home')

@app.route('/home')
def home_page():
    # 세션에 access_token이 없거나 만료되었으면 로그인 페이지로 리디렉션
    if 'access_token' not in session or datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/login')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # 인기곡 - 대한 민국 (주간)
    try:
        response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd/tracks?limit=20',
                                headers=headers)
        response_data = response.json()
        print(f"Korean tracks API response: {response_data}")  # 디버깅용
        top_tracks_kr = response_data.get('items', [])
        
        # 데이터가 없으면 샘플 데이터 사용 (Free 계정용)
        if not top_tracks_kr:
            print("No global tracks found, using sample data for Free account")
            top_tracks_kr = [
                {'track': {'name': 'Blinding Lights', 'artists': [{'name': 'The Weeknd'}], 'album': {'images': [{'url': 'https://via.placeholder.com/300', 'height': 300}], 'release_date': '2019-11-29'}, 'preview_url': None}},
                {'track': {'name': 'Shape of You', 'artists': [{'name': 'Ed Sheeran'}], 'album': {'images': [{'url': 'https://via.placeholder.com/300', 'height': 300}], 'release_date': '2017-01-06'}, 'preview_url': None}},
                {'track': {'name': 'Someone Like You', 'artists': [{'name': 'Adele'}], 'album': {'images': [{'url': 'https://via.placeholder.com/300', 'height': 300}], 'release_date': '2011-01-24'}, 'preview_url': None}},
                {'track': {'name': 'Uptown Funk', 'artists': [{'name': 'Mark Ronson'}, {'name': 'Bruno Mars'}], 'album': {'images': [{'url': 'https://via.placeholder.com/300', 'height': 300}], 'release_date': '2014-11-10'}, 'preview_url': None}}
            ]
    except Exception as e:
        print(f"Error fetching Korean tracks: {e}")
        top_tracks_kr = []

    # 국내외 신곡들 (매주 업데이트)
    try:
        response_2 = requests.get('https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd/tracks?limit=20',
                                  headers=headers)
        response_2_data = response_2.json()
        print(f"Global tracks API response: {response_2_data}")  # 디버깅용
        recent_tracks = response_2_data.get('items', [])
        
        # 데이터가 없으면 샘플 데이터 사용
        if not recent_tracks:
            print("No global tracks found, using sample data")
            recent_tracks = [{
                'track': {
                    'name': 'Sample Global Song',
                    'artists': [{'name': 'Sample Global Artist'}],
                    'album': {
                        'images': [{'url': 'https://via.placeholder.com/300', 'height': 300}],
                        'release_date': '2024-01-01'
                    },
                    'preview_url': None
                }
            }]
    except Exception as e:
        print(f"Error fetching global tracks: {e}")
        recent_tracks = []

    top_tracks_kr_info = []
    recent_tracks_info = []
    review_list = []
    try:
        for i in review_collection.find():
            review_list.append(i)
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        review_list = []

    for track in top_tracks_kr:
        # 트랙 세부 정보 추출
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        album_images = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
        preview_url = track['track']['preview_url']
        release_date = track['track']['album']['release_date']

        data_kr = {
            'track_name': track_name,
            'artists': artists,
            'album_image': album_images,
            'preview_url': preview_url,
            'release_date': release_date
        }
        # MongoDB에 중복 삽입 방지
        try:
            if not kr_top_collection.find_one({'track_name': track_name, 'artists': artists}):
                kr_top_collection.insert_one(data_kr)
        except Exception as e:
            print(f"Error inserting Korean track to MongoDB: {e}")
        # 추천 정보 목록에 추가
        top_tracks_kr_info.append(data_kr)

    for track in recent_tracks:
        # 트랙 세부 정보 추출
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        album_images = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
        preview_url = track['track']['preview_url']
        release_date = track['track']['album']['release_date']

        data_recent_tracks = {
            'track_name': track_name,
            'artists': artists,
            'album_image': album_images,
            'preview_url': preview_url,
            'release_date': release_date
        }
        # MongoDB에 중복 삽입 방지
        try:
            if not global_latest_tracks_collection.find_one({'track_name': track_name, 'artists': artists}):
                global_latest_tracks_collection.insert_one(data_recent_tracks)
        except Exception as e:
            print(f"Error inserting global track to MongoDB: {e}")
        # 추천 정보 목록에 추가
        recent_tracks_info.append(data_recent_tracks)

    # 관리자인 경우 main.html 렌더링
    if session.get('is_admin', False):
        return flask.render_template("admin_main.html", top_tracks_kr_info=top_tracks_kr_info,
                                     recent_tracks_info=recent_tracks_info, reviews=review_list)

    """유료 구독자 상태를 확인하는 랜딩 페이지"""
    if not session.get('is_subscriber', False):
        # 사용자가 구독자가 아닌 경우, 특정 기능에 대한 접근 제한
        return render_template("mainUnauthorized.html", message="This feature is available for paid subscribers only.",
                               top_tracks_kr_info=top_tracks_kr_info, recent_tracks_info=recent_tracks_info,
                               reviews=review_list)


    # 사용자가 구독자이면서, 관리자가 아닌 경우 mainUnauthorized.html 렌더링
    return render_template("main.html", message="You do not have access to this page.",
                           top_tracks_kr_info=top_tracks_kr_info, recent_tracks_info=recent_tracks_info,
                           reviews=review_list)


@app.route('/playlist')
def get_playlists():
    """Get playlists"""
    #사용자의 플레이리스트를 가져와 템플릿에 표시
    if not session.get('is_subscriber', False):
        return render_template("mainUnauthorized.html")

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
    return render_template("features/playlist.html", playlists=p)

@app.route('/songs')
def get_songs():
    """Get top songs"""
    # 사용자의 인기 트랙을 가져와 템플릿에 표시
    if not session.get('is_subscriber', False):
        return render_template("mainUnauthorized.html")

    # error checking
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    # url = "https://api.spotify.com/v1/me/top/tracks"

    try:
        response = get("https://api.spotify.com/v1/me/top/tracks", headers=headers, timeout=10)
        data = response.json()
        print(f"User top tracks API response: {data}")  # 디버깅용
        items = data.get('items', [])
    except Exception as e:
        print(f"Error fetching user top tracks: {e}")
        items = []
    
    # Extract information for each track and store in MongoDB
    tracks_info = []
    for item in items:  # Iterate over the 'items' key in 'data'
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
            try:
                user_most_listened_to_songs_collection.insert_one(track_info)
            except Exception as e:
                print(f"Error inserting track to MongoDB: {e}")

        # Append track_info to tracks_info list
        tracks_info.append(track_info)

    return render_template("features/songs.html", tracks_info=tracks_info)

@app.route('/artists')
def get_artists():

    """Get top artists"""
    # 사용자의 인기 아티스트를 가져와 템플릿에 표시
    if not session.get('is_subscriber', False):
        return render_template("mainUnauthorized.html")

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
    return render_template("features/artists.html", artists_info=artists_info)

@app.route('/recommendation')
def get_recommendations():
    """Get recommended songs"""
    # Check for access token in session
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.datetime.now().timestamp() > session['expires']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Get seed artist IDs
    try:
        response = get("https://api.spotify.com/v1/me/top/artists?limit=5", headers=headers, timeout=10)
        data = response.json()
        print(f"User top artists API response: {data}")  # 디버깅용
        total = data.get('total', 0)
    except Exception as e:
        print(f"Error fetching user top artists: {e}")
        total = 0
        data = {'items': []}

    if total == 0:  # Check if no artists were found
        try:
            response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks?limit=10',
                                    headers=headers)
            response_data = response.json()
            print(f"Recommendation fallback API response: {response_data}")  # 디버깅용
            top_tracks = response_data.get('items', [])
        except Exception as e:
            print(f"Error fetching recommendation fallback tracks: {e}")
            top_tracks = []
        recommend_info = []

        for track in top_tracks:
            track_name = track['track']['name']
            artists = [artist['name'] for artist in track['track']['artists']]
            album_image_url = [image['url'] for image in track['track']['album']['images'] if image['height'] == 300]
            release_date = track['track']['album']['release_date']

            recommendation_data = {
                "artist_name": artists,
                "track_name": track_name,
                "album_image_url": album_image_url,
                "release_date": release_date,
            }

            existing_data = top_tracks_collection.find_one({
                "artist_name": recommendation_data["artist_name"],
                "track_name": recommendation_data["track_name"]
            })

            if existing_data is None:
                top_tracks_collection.insert_one(recommendation_data)

            recommend_info.append(recommendation_data)

        return render_template("features/global_top_tracks.html", recommend_info=recommend_info)

    ids = [item["id"] for item in data["items"]]
    artist_ids = ','.join(ids)

    try:
        response = get(f"https://api.spotify.com/v1/recommendations?seed_artists={artist_ids}&limit=100", headers=headers,
                       timeout=10)
        recommendations = response.json()
        print(f"Recommendations API response: {recommendations}")  # 디버깅용
        tracks = recommendations.get('tracks', [])
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        tracks = []
    
    recommend_info = []

    for track in tracks:
        artists = ", ".join([artist['name'] for artist in track['artists']])
        track_name = track['name']
        preview_url = track['preview_url']
        album_image_url = track['album']['images'][1]['url']

        if preview_url is not None:
            recommendation_data = {
                "artist_name": artists,
                "track_name": track_name,
                "preview_url": preview_url,
                "album_image_url": album_image_url
            }
            recommend_info.append(recommendation_data)
            recommendations_collection.insert_one(recommendation_data)

    return render_template("features/recommendation.html", recommend_info=recommend_info)

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
    try:
        response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks?limit=10',
                                headers=headers)
        response_data = response.json()
        print(f"Global top tracks API response: {response_data}")  # 디버깅용
        top_tracks = response_data.get('items', [])
    except Exception as e:
        print(f"Error fetching global top tracks: {e}")
        top_tracks = []
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

    return render_template("features/global_top_tracks.html", recommend_info=recommend_info)

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
    try:
        response = requests.get('https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd/tracks?limit=20', headers=headers)
        response_data = response.json()
        print(f"Global and KR tendency - Korean tracks API response: {response_data}")  # 디버깅용
        top_tracks_kr = response_data.get('items', [])
    except Exception as e:
        print(f"Error fetching Korean tracks in global_and_kr_tendency: {e}")
        top_tracks_kr = []

    # 국내외 신곡들 (매주 업데이트)
    try:
        response_2 = requests.get('https://api.spotify.com/v1/playlists/37i9dQZF1DX4sIVfz61Q23/tracks?limit=20', headers=headers)
        response_2_data = response_2.json()
        print(f"Global and KR tendency - Global tracks API response: {response_2_data}")  # 디버깅용
        recent_tracks = response_2_data.get('items', [])
    except Exception as e:
        print(f"Error fetching global tracks in global_and_kr_tendency: {e}")
        recent_tracks = []

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

    return render_template("features/global_and_kr_tendency.html", recent_tracks_info=recent_tracks_info, top_tracks_kr_info=top_tracks_kr_info)



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

@app.route("/song")
def songlist():
    return render_template("songlist.html")

'''@app.route("/reviewList")
def reviewList():
    return render_template("reviewList.html")'''
@app.route("/reviewList", methods=['GET','POST'])
def reviewList():
    review_list=[]
    for i in review_collection.find():
        review_list.append(i)

    if request.method == 'POST':
        if request.form['id']:
            id = request.form['id']
            id = ObjectId(id)
            query = {
                '_id': id
            }
            review_collection.delete_one(query)
            return redirect('/reviewList')

    return render_template("reviewList.html", reviews = review_list)


'''@app.route("/review")
def review():
    return render_template("review.html")'''
@app.route("/review", methods=['GET','POST'])
def review():
    if request.method == 'POST':
        writer_name = request.form['writer_name']
        content = request.form['content']


        if writer_name and content:

            review_data = {
                'writer_name': writer_name,
                'content': content
            }

            review_collection.insert_one(review_data)

            return redirect('/home')

    return render_template("review.html")


@app.route('/review_edit/<id>', methods=['GET','POST'])
def review_edit(id):
    if request.method == 'POST':
        if request.form['id']:
            id = request.form['id']
            id = ObjectId(id)
            if request.form['writer_name_edit'] and request.form['content_edit']:
                writer_name = request.form['writer_name_edit']
                content = request.form['content_edit']
                query = {
                    '_id': id
                }
                review_data = {
                    "$set": {
                        'writer_name': writer_name,
                        'content': content
                    }
                }
                review_collection.update_one(query,review_data)
                return redirect('/home')
            else:
                return render_template("review_edit.html", id = id)

    # get details data
    data = ""
    try:
        _id_converted = ObjectId(id)
        search_filter = {"_id": _id_converted}  # _id is key and _id_converted is the converted _id
        data = review_collection.find_one(search_filter)  # get one data matched with _id
    except:
        print("ID is not found/invalid")

    return render_template("review_edit.html", data=data)


if __name__ == '__main__':
    # HTTPS를 위한 SSL 설정 (개발환경용)
    app.run(host='0.0.0.0', debug=True, port=5000, ssl_context='adhoc')
