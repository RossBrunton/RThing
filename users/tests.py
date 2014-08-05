from django.contrib.auth.models import User
from django.test import TestCase, Client

from users import views

class UsersTestCase(TestCase):
    def test_login(self):
        """Does logging in and logging out work"""
        User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        
        c = Client()
        
        self.assertTrue("_auth_user_id" not in c.session)
        c.post("/users/login", {"username":"Mittens", "password":"meow"})
        self.assertTrue("_auth_user_id" in c.session)
        c.post("/users/logout", {})
        self.assertTrue("_auth_user_id" not in c.session)
    
    def test_invalid_login(self):
        """Does logging in as an invalid user cause problems"""
        User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        
        c = Client()
        
        self.assertTrue("_auth_user_id" not in c.session)
        
        resp = c.post("/users/login", {"username":"Mittens", "password":"woof"})
        self.assertTrue("_auth_user_id" not in c.session)
        self.assertTrue("users/login.html" in map(lambda t : t.name, resp.templates))
        
        resp = c.post("/users/login", {"username":"Fido", "password":"meow"})
        self.assertTrue("_auth_user_id" not in c.session)
        self.assertTrue("users/login.html" in map(lambda t : t.name, resp.templates))
