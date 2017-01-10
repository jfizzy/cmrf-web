import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        self.assertTrue(u.pw_hash is not None)

    def test_no_password_getter(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        u2 = User(UCID=11111111, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        self.assertTrue(u.pw_hash != u2.pw_hash)

    def test_valid_confirmation_token(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm_email(token))

    def test_invalid_confirmation_token(self):
        u1 = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        u2 = User(UCID=11111111, first_name='Someone', last_name='Else', password='dog', email='someoneelse@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm_email(token))

    def test_expired_confirmation_token(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expiration=1)
        time.sleep(2)
        self.assertFalse(u.confirm_email(token))

    def test_valid_reset_token(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u1 = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='someone@example.com')
        u2 = User(UCID=11111111, first_name='Someone', last_name='Special', password='dog', email='someoneelse@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'horse'))
        self.assertTrue(u2.verify_password('dog'))

    def test_valid_email_change_token(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='john@example.com')
        u2 = User(UCID=11111111, first_name='Someone', last_name='Special', password='dog', email='susan@example.org')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='john@example.com')
        u2 = User(UCID=11111111, first_name='Someone', last_name='Special', password='dog', email='susan@example.org')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_roles_and_permissions(self):
        u = User(UCID=00000000, first_name='Someone', last_name='Special', password='cat', email='john@example.com')
        self.assertTrue(u.can(Permission.ALL_R))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.MAKE_R))
