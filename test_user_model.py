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

        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_user_signup_nonunique_email(self):
        """ test User. Create with non-unique email """
        User.signup('testuser_null', 
                        'test1@test.com', 
                        "cleverpassword", 
                        None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authenticate_valid(self):
        """ Test that a valid user suthentiactes."""
        User.signup('testuser5', 
                    'test5@test.com', 
                    "cleverpassword", 
                    None)

        db.session.commit()

        u = User.authenticate('testuser5','cleverpassword')

        self.assertEqual(u.email, 'test5@test.com')

    def test_authenticate_invalid_password(self):
        User.signup('testuser5', 
                    'test5@test.com', 
                    "cleverpassword", 
                    None)

        db.session.commit()

        u = User.authenticate('testuser5','badpassword')

        self.assertEqual(u, False)

    def test_authenticate_invalid_username(self):
        User.signup('testuser6', 
                    'test6@test.com', 
                    "cleverpassword", 
                    None)

        db.session.commit()

        u = User.authenticate('testuser7','cleverpassword')

        self.assertEqual(u, False)