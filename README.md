this is spotify recommender webservice

#  Tech(2024/05/07)

1. Recommend system( Based on Multi-Armed Bandit Algorithm)
2. Flask(Backend)
3. MongoDB(Database)
4. HTML, CSS, JS 


#  List of Services:
1. See user's playlists
2. See user's most listened to songs
3. See user's  most listened to artists
4. See recommended songs
5. See recommended top songs
6. See Weekly updated playlist of new domestic and international tracks & South Korea's most played song of the week.


#  List of URLS:

1. http://127.0.0.1:5000/: index
2. https://accounts.spotify.com/ko/authorize: spotify login page
3. http://localhost:5000/home: List of Services
4. http://localhost:5000/playlists: user's Playlists
5. http://localhost:5000/songs: uer's Most Listened To Songs
6. http://localhost:5000/artists: user's Most Listened To Artists
7. http://localhost:5000/recommendations: Recommended user songs
8. http://localhost:5000/top_tracks_recommendations: Recommended Top tracks
9. http://localhost:5000/global_and_kr_tendency : Recent Tracks vs. Top Tracks in Korea



#  Flow 

1. http://127.0.0.1:5000/
![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/c889990e-80be-4239-b7bd-7ee0790ebeaf)
![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/5a30d3d6-4d42-4998-97cf-cc4c231ddc84)
![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/4d9f9fa3-11ae-485a-8c2f-5f212ada6ec8)


2. https://accounts.spotify.com/ko/authorize: spotify login page  ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/edcc3246-a8d5-4547-901b-a5fee120f129)


3. http://localhost:5000/home: List of Servicesc ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/f5c4fb81-2772-480d-8a70-bf762e76fdd6)

List of Servicesc(not subscriber) ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/a0c3d130-7108-41b9-9cf0-027619870efe)


4. http://localhost:5000/playlists: user's Playlists ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/701fccf2-a3bb-40ab-85f7-32011bf80d45)

5. http://localhost:5000/songs: uer's Most Listened To Songs ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/68c599bc-67e3-4b55-96f8-e1a5b2fc6303)

6. http://localhost:5000/artists: user's Most Listened To Artists ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/3206f2c1-cad1-4148-a851-f5b6d43d0859)

7. http://localhost:5000/recommendations: Recommended user songs ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/fc22e3a0-9658-4233-a9f7-ecc823651055)

8. http://localhost:5000/top_tracks_recommendations: Recommended Top tracks ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/f7558469-bf71-415e-ae72-70747fdf1458)

9. http://localhost:5000/global_and_kr_tendency : Recent Tracks vs. Top Tracks in Korea ![image](https://github.com/Hamseungjin/WEB_PROJECT/assets/109064686/4f04d9a8-6987-4090-92c7-3f9baa94f5fa)


#  RESTful API

- to be continue

#  Spotfity API 

1. **GET Spotify Token**
   - Endpoint: `https://accounts.spotify.com/api/token`
   - Purpose: This endpoint is used to authenticate and obtain an access token for making subsequent requests to the Spotify API.

2. **GET User's Playlists**
   - Endpoint: `https://api.spotify.com/v1/me/playlists`
   - Purpose: Fetches a list of playlists owned or followed by the current Spotify user.

3. **GET User's Most Listened Songs**
   - Endpoint: `https://api.spotify.com/v1/me/top/tracks`
   - Purpose: Retrieves the user's most listened to tracks.

4. **GET User's Most Listened to Artists**
   - Endpoint: `https://api.spotify.com/v1/me/top/artists`
   - Purpose: Retrieves the user's most listened to artists.

5. **GET 인기곡 - 대한 민국 (주간)**
   - Endpoint: `https://api.spotify.com/v1/playlists/37i9dQZEVXbJZGli0rRP3r/tracks?limit=20`
   - Purpose: Fetches tracks from the "인기곡 - 대한 민국 (주간)" playlist on Spotify, limited to 20 tracks.

6. **GET 국내외 신곡들 (매주 업데이트)**
   - Endpoint: `https://api.spotify.com/v1/playlists/37i9dQZF1DXdlsL6CGuL98/tracks?limit=20`
   - Purpose: Retrieves tracks from the "국내외 신곡들 (매주 업데이트)" playlist, limited to 20 tracks.

7. **GET Global Top Tracks**
   - Endpoint: `https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks?limit=10`
   - Purpose: Retrieves tracks from the "Global top tracks" playlist, limited to 10 tracks.

8. **GET Spotfit Recommend Algorithm (Multi-Arm-Bandit) API**
   - Endpoint: `https://api.spotify.com/v1/recommendations?seed_artists`
   - Purpose: This endpoint likely generates personalized music recommendations using a recommendation algorithm (potentially a multi-armed bandit approach) based on provided seed artists.

#  Recommend system( Based on Multi-Armed Bandit Algorithm)

1. [멀티 암드 밴딧.pdf](https://github.com/Hamseungjin/WEB_PROJECT/files/15261867/default.pdf)

REFERENCE, 
1. https://dl.acm.org/doi/abs/10.1145/3240323.3240354
2. https://brunch.co.kr/@albthere4u/244

#  database, collection structure

database 2 (user_spotify_info, recommendation_info) + collection 7

# 1. user_spotify_info
 1. playlists_collection
 2. user_most_listened_to_songs_collection
 3. user_top_artists_collection

# 2. recommendation_info
 1. recommendations_collection
 2. top_tracks_collection
 3. kr_top_collection
 4. global_latest_tracks_collection

#  Data overview

1 "https://api.spotify.com/v1/me/playlists"

REFERENCE, https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists

2 "https://api.spotify.com/v1/me/top/tracks"

REFERENCE, https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks

3 "https://api.spotify.com/v1/me/top/artists"

REFERENCE, https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks

4 "https://api.spotify.com/v1/recommendations"

REFERENCE, https://developer.spotify.com/documentation/web-api/reference/get-recommendations

# Contributor

- [Seung Jin HAM](https://github.com/Hamseungjin)
- [Ji Won BANG](https://github.com/banxzxx)
- [Florian](https://github.com/Florian-Fogliani)
- [Doh yun KIM](https://github.com/neeewbieee)

