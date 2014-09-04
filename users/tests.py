"""Unit tests for the users app"""
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.test.utils import override_settings

from users import views

from django.conf import settings

class UsersTestCase(TestCase):
    """Test case for the users app"""
    remote_settings = {
        "USE_REMOTE_USER":True,
        "AUTHENTICATION_BACKENDS":('users.backends.CustomRemoteUserBackend',),
        "MIDDLEWARE_CLASSES":settings.MIDDLEWARE_CLASSES + ('django.contrib.auth.middleware.RemoteUserMiddleware',)
    }
    
    def setUp(self):
        """Set up; create a user named mittensthekitten"""
        self.u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
    
    def test_login(self):
        """Does logging in and logging out work"""
        c = Client()
        
        self.assertTrue("_auth_user_id" not in c.session)
        c.post("/users/login", {"username":"Mittens", "password":"meow"})
        self.assertTrue("_auth_user_id" in c.session)
        c.post("/users/logout", {})
        self.assertTrue("_auth_user_id" not in c.session)
    
    def test_invalid_login(self):
        """Does logging in as an invalid user cause problems"""
        c = Client()
        
        self.assertTrue("_auth_user_id" not in c.session)
        
        resp = c.post("/users/login", {"username":"Mittens", "password":"woof"})
        self.assertTrue("_auth_user_id" not in c.session)
        self.assertTrue("users/login.html" in map(lambda t : t.name, resp.templates))
        
        resp = c.post("/users/login", {"username":"Fido", "password":"meow"})
        self.assertTrue("_auth_user_id" not in c.session)
        self.assertTrue("users/login.html" in map(lambda t : t.name, resp.templates))

    def test_password_force(self):
        """Does forcing their user to check their password work"""
        c = Client()
        self.u.extra.password_forced = True
        
        
        resp = c.post("/users/login", {"username":"Mittens", "password":"meow"}, follow=True)
        self.assertTrue("users/edit.html" in map(lambda t : t.name, resp.templates))
        
        resp = c.post(
            "/users/edit", {"old_password":"meow", "new_password1":"meow2", "new_password2":"meow2"},
            follow=True
        )
        self.assertTrue("users/password_changed.html" in map(lambda t : t.name, resp.templates))
        
        resp = c.get("/", follow=True)
        self.assertTrue("courses/index.html" in map(lambda t : t.name, resp.templates))
        
    
    @override_settings(**remote_settings)
    def test_remote_reject(self):
        """Testing if a remote user request without a remote user doesn't work"""
        c = Client()
        
        resp = c.post("/users/login", {"username":"Mittens", "password":"meow"})
        self.assertFalse("courses/index.html" in map(lambda t : t.name, resp.templates))
    
    @override_settings(**remote_settings)
    def test_remote_accept(self):
        """Testing if a remote user request with a remote user works"""
        c = Client()
        
        resp = c.get("/courses/", REMOTE_USER="Mittens")
        self.assertTrue("courses/index.html" in map(lambda t : t.name, resp.templates))
    
    
    @override_settings(**remote_settings)
    def test_remote_unknown(self):
        """Testing if a remote user request with an unknown user works"""
        c = Client()
        
        resp = c.get("/courses/", REMOTE_USER="EvilSteve")
        self.assertFalse("courses/index.html" in map(lambda t : t.name, resp.templates))
    
    
    @override_settings(**remote_settings)
    def test_remote_email(self):
        """Testing if a remote user request works with cleaning"""
        c = Client()
        
        resp = c.get("/courses/", REMOTE_USER="Mittens@cats.ac.uk")
        self.assertTrue("courses/index.html" in map(lambda t : t.name, resp.templates))
