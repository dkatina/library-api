from app import create_app
from app.models import Users, db
import unittest
from werkzeug.security import check_password_hash, generate_password_hash
from app.util.auth import encode_token


#Run Script: python -m unittest discover tests

class TestUsers(unittest.TestCase):

    #Runs before each test_method
    def setUp(self): 
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.user = Users(email="tester@email.com", username="tester", password=generate_password_hash('123'), role='user') #Creating a starter user, to test things like get, login, update, and delete
        with self.app.app_context(): 
            db.drop_all() #removing any lingering table
            db.create_all() #creating fresh for another round of testing
            db.session.add(self.user)
            db.session.commit()
        self.token = encode_token(1, 'user') #encoding a token for my starter User defined above ^
        self.client = self.app.test_client() #creates a test client that will send requests to our API

    
    #test creating a user (IMPORTANT all test functions need to start with test)
    def test_create_user(self):
        user_payload = {
            "email": "test@email.com",
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }


        response = self.client.post('/users', json=user_payload) #sending a test POST request using our test_client, and including the JSON body
        self.assertEqual(response.status_code, 201) #checking if I got a 201 status
        self.assertEqual(response.json['username'], "test_user") #Checking to make sure the data that I sent in, is apart of the response.
        self.assertTrue(check_password_hash(response.json['password'], "123"))


    #Negative check: See what happens when we intentially try and break an endpoint
    def test_invalid_create(self):
        user_payload = { #Missing email which should be required
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }

  
        response = self.client.post('/users', json=user_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json) #Membership check that email is in the response json

    def test_nonunique_email(self):
        user_payload = { 
            "email": "tester@email.com",
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }

        response = self.client.post('/users', json=user_payload)
        self.assertEqual(response.status_code, 400)


    def test_get_users(self):
    
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['username'], 'tester')

    def test_login(self):
        login_creds = {
            "email": "tester@email.com",
            "password": "123"
        }

        response = self.client.post('/users/login', json=login_creds)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)


    def test_delete(self):
        headers = {"Authorization": "Bearer " + self.token}

        response = self.client.delete("/users", headers=headers) #Sending delete request to /users with my Authorization headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted user 1')


    def test_unauthorized_delete(self):

        response = self.client.delete("/users") #Sending delete request to /users without token
        self.assertEqual(response.status_code, 401) #Should get an error response

    
    def test_update(self):
        headers = {"Authorization": "Bearer " + self.token}

        update_payload = {
            "email": "NEW_EMAIL@email.com",
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }

        response = self.client.put('/users', headers=headers, json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'NEW_EMAIL@email.com')




       

    
   

 

