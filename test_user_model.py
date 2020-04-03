"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)

        self.client = app.test_client()

    def tearDown(self):
        """ clean slate each time"""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):
        """ Does is_following actually detect follows? """
        u1 = User.query.filter(User.username == 'testuser1').first()
        u2 = User.query.filter(User.username == 'testuser2').first()

        new_follow = Follows(user_being_followed_id=u1.id,
                             user_following_id=u2.id)

        db.session.add(new_follow)
        db.session.commit()

        # u1 is actually being followed by u2, but not the reverse
        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_following(u1), True)

    def test_is_followed_by(self):
        """ Does is_followed_by actually detect follows? """
        u1 = User.query.filter(User.username == 'testuser1').first()
        u2 = User.query.filter(User.username == 'testuser2').first()

        new_follow = Follows(user_being_followed_id=u1.id,
                             user_following_id=u2.id)

        db.session.add(new_follow)
        db.session.commit()

        # u1 is actually being followed by u2, but not the reverse
        self.assertEqual(u1.is_followed_by(u2), True)
        self.assertEqual(u2.is_followed_by(u1), False)


    def test_user_signup_valid(self):
        """ test User.create with valid credentials """

        u_valid = User.signup("validUser", "unique@email.edu", "cleverpassword", None)
        u_valid.id = 9999
        db.session.commit()

        valid_test = User.query.get(9999)

        self.assertEqual(valid_test.username, 'validUser')
        self.assertEqual(valid_test.email, "unique@email.edu")
        self.assertNotEqual(valid_test.password, "cleverpassword")
        self.assertTrue(valid_test.password.startswith("$2b$"))

    def test_user_signup_null(self):
        """ test User.create with nulled credentials """
        u_null = User.signup('testuser_null', None, "cleverpassword", None)

        self.assertRaises(exc.IntegrityError)



    # def test_user_signup(self):
    #     """ test User.create with valid credentials and invalid credentials """        user_null = User.signup(*u_null)
    #     user_not_unique = User.signup(*u_email_not_unique)

    #     db.session.commit()

    #     user_nullinstance = User.signup(*u_null)
    #     user_not_uniqueinstance = User.signup(*u_email_not_unique)

    #     self.assertRaises(exc.IntegrityError, User.signup(*u_null))
    #     self.assertRaises(exc.IntegrityError, User.signup(*u_email_not_unique))


    #     valid_test_user_instance = User.query.filter_by(username='validUser').first()
    #     self.assertTrue(valid_test_user_instance.email == 'unique@email.edu')

    # # def test_user_authenticate(self):
