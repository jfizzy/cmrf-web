import re
import threading
import time
import unittest
from selenium import webdriver.Chrome
from app import create_app, db
from app.models import Role, User

class SeleniumTestCase(unittest.TestCase):
    client = None
    
    @classmethod
    def setUpClass(cls):
        # start Chrome
        try:
            cls.client = Chrome()
        except:
            pass
        
        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            
            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            user = User(UCID=11111111, 
                        first_name='Jane', 
                        last_name='Doe', 
                        password='doggy',
                        password_confirm='doggy',
                        email='jane@example.com',
                        lab='Somewhere',
                        confirmed=True)
            db.session.add(user)
            db.session.commit()
            
            # add an administrator user
            admin_role = 4
            admin = User(UCID=99999999, 
                         first_name='Arnold', 
                         last_name='Schwartz', 
                         password='illbeback',
                         password_confirm='illbeback',
                         email='arnold@example.com',
                         lab='Somewhere',
                         confirmed=True,
                         role_id=admin_role)
            db.session.add(admin)
            db.session.commit()
            
            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()
        
    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()
            
            # destroy the database
            db.drop_all()
            db.session.remove()
            
            # remove application context
            cls.app_context.pop()
            
    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')
            
    def teardown(self):
        pass
    
    def test_admin_home_page(self):
        # navigate to home page
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Lewis Research Group', self.client.page_source))
        
        # navigate to login page
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)
        
        # login
        self.client.find_element_by_name('email').send_keys('jane@example.com')
        self.client.find_element_by_name('password').send_keys('doggy')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Jane Doe', self.client.page_source))
        
        # navigate to the user's account details page
        self.client.find_element_by_link_text('userop').click()
        self.client.find_element_by_link_text('accdet').click()
        self.assertTrue('<h1>Account Details</h1>' in self.client.page_source)
        self.assertTrue('Jane Doe' in self.client.page_source)
