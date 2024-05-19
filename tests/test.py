import unittest
from app import app, playlists_collection, user_most_listened_to_songs_collection, user_top_artists_collection
from pymongo import MongoClient

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db_user = self.client['user_spotify_info']
        self.db_recommend = self.client['recommendation_info']

    def tearDown(self):
        # Clear collections after each test
        self.db_user.playlists_collection.delete_many({})
        self.db_user.user_most_listened_to_songs_collection.delete_many({})
        self.db_user.user_top_artists_collection.delete_many({})

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"See Spotify Data", response.data)

    def test_login(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 302)  # Redirects to Spotify login

    def test_home_page(self):
        response = self.app.get('/home')
        self.assertEqual(response.status_code, 302)  # Redirects to login if no access token

    # Add similar test methods for other routes like get_songs, get_artists, etc.

if __name__ == '__main__':
    unittest.main()
