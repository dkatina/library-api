from app import create_app
from app.models import Books, db, Users
import unittest
from werkzeug.security import generate_password_hash
from app.util.auth import encode_token
from datetime import date

class TestBooks(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        # Create an admin user for authorization
        self.admin_user = Users(
            email="admin@email.com",
            username="admin",
            password=generate_password_hash('adminpass'),
            role='admin'
        )
        # Create a regular user
        self.user = Users(
            email="user@email.com",
            username="user",
            password=generate_password_hash('userpass'),
            role='user'
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.admin_user)
            db.session.add(self.user)
            db.session.commit()
            # Add a starter book
            self.book = Books(
                title="Test Book",
                genre="Fiction",
                age_category="Adult",
                publish_date=date(2020, 1, 1),
                author="Author Name"
            )
            db.session.add(self.book)
            db.session.commit()
        self.admin_token = encode_token(self.admin_user.id, self.admin_user.role)
        self.user_token = encode_token(self.user.id, self.user.role)

    def test_create_book(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        payload = {
            "title": "New Book",
            "genre": "Nonfiction",
            "age_category": "Teen",
            "publish_date": "2022-05-10",
            "author": "New Author"
        }
        response = self.client.post('/books', json=payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['title'], "New Book")

    def test_create_book_unauthorized(self):
        # Should fail for non-admin
        headers = {"Authorization": "Bearer " + self.user_token}
        payload = {
            "title": "Unauthorized Book",
            "genre": "Fiction",
            "age_category": "Adult",
            "publish_date": "2021-01-01",
            "author": "Someone"
        }
        response = self.client.post('/books', json=payload, headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_create_book_invalid(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        payload = {
            # Missing required fields
            "title": "",
            "genre": "Fiction"
        }
        response = self.client.post('/books', json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_get_books(self):
        response = self.client.get('/books')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(book['title'] == "Test Book" for book in response.json))

    def test_get_books_paginated(self):
        response = self.client.get('/books?page=1&per_page=1')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['items'], list)

    def test_update_book(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        payload = {
            "title": "Updated Book",
            "genre": "Fiction",
            "age_category": "Adult",
            "publish_date": "2020-01-01",
            "author": "Author Name"
        }
        response = self.client.put(f'/books/{self.book.id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], "Updated Book")

    def test_update_book_invalid(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        payload = {
            "title": "",  # Invalid title
            "genre": "Fiction",
            "age_category": "Adult",
            "publish_date": "2020-01-01",
            "author": "Author Name"
        }
        response = self.client.put(f'/books/{self.book.id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_update_book_not_found(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        payload = {
            "title": "Does Not Exist",
            "genre": "Fiction",
            "age_category": "Adult",
            "publish_date": "2020-01-01",
            "author": "Author Name"
        }
        response = self.client.put('/books/9999', json=payload, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_book(self):
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.delete(f'/books/{self.book.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully deleted book", response.json)

    def test_get_popular_books(self):
        response = self.client.get('/books/popularity')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_search_book(self):
        response = self.client.get('/books/search?title=Test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Test Book" in book['title'] for book in response.json))

    def test_search_book_no_results(self):
        response = self.client.get('/books/search?title=Nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)