import unittest
from pymongo import MongoClient
import db
from hashing import Hashing  

class TestDBFunctions(unittest.TestCase):

    def setUp(self):
        # Set up the database connection and create a test instance
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = db.DB()
        self.hashing = Hashing()

    def tearDown(self):
        # Clean up the test database after each test
        self.client.drop_database('p2p-chat')
        

    def test_register_user(self):
        # Test user registration
        username = 'test_user'
        password = 'test_password'

        # Ensure the user does not already exist
        self.assertFalse(self.db.is_account_exist(username))

        # Register the user
        self.db.register(username, password)

        # Check if the user now exists
        self.assertTrue(self.db.is_account_exist(username))


    def test_user_login_logout(self):
        # Test user login and logout
        username = 'test_user'
        ip = '127.0.0.1'
        port = 12345

        # Ensure the user is not initially online
        self.assertFalse(self.db.is_account_online(username))

        # Log in the user
        self.db.user_login(username, ip, port)

        # Check if the user is now online
        self.assertTrue(self.db.is_account_online(username))

        # Log out the user
        self.db.user_logout(username)

        # Check if the user is offline after logout
        self.assertFalse(self.db.is_account_online(username))

    def test_chat_room_management(self):
        # Test chat room creation and user joining
        chat_room_name = 'test_chat_room'
        username = 'test_user'

        # Create a chat room
        self.db.create_ChatRoom(chat_room_name)

        # Check if the chat room exists
        self.assertTrue(self.db.does_ChatRoom_Exists(chat_room_name), "Room was not added correctly!")

        # Join the chat room
        self.db.join_ChatRoom(chat_room_name, username)

        # Check if the user is a participant in the chat room
        participants = self.db.get_ChatRoom_Participants(chat_room_name)
        self.assertIn(username, participants.split(), "User was not added correctly!")

        # Remove the user from the chat room
        self.db.remove_ChatRoom_user(chat_room_name, username)

        # Check if the user is no longer a participant in the chat room
        participants_after_removal = self.db.get_ChatRoom_Participants(chat_room_name)
        self.assertNotIn(username, participants_after_removal.split(), "User was not removed from chatroom!")

    def test_get_password(self):
        # Test getting user password
        username = 'test_user'
        password = 'test_password'

        # Register the user
        self.db.register(username, password)

        # Get the password and compare with the original password
        retrieved_password = self.db.get_password(username)
        self.assertEqual(retrieved_password, self.hashing.encodePassword(password), "Password retrival wrong!")

if __name__ == '__main__':
    unittest.main()


""" import unittest
from pymongo import MongoClient
import db
 """




