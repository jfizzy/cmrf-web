import unittest, re
from flask import url_for
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('Lewis Research Group' in response.get_data(as_text=True))
        
    def test_register_and_login(self):
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'UCID': 11111111,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'helloworld',
            'password_confirm': 'helloworld',
            'lab': 'Somewhere'
        })
        self.assertTrue(response.status_code == 302)

    def test_register_and_login_w_phone(self):
        # register a new account with a phone number
        response = self.client.post(url_for('auth.register'), data={
            'UCID': 11111111,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'helloworld',
            'password_confirm': 'helloworld',
            'lab': 'Somewhere',
            'phone': '1234567890'
        })
        self.assertTrue(response.status_code == 302)