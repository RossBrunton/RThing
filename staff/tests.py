"""Tests for staff features"""
from django.test import TestCase, Client
from django.contrib.auth.models import User

from courses.models import Course

class StaffTestCase(TestCase):
    """Test case for staff features"""
    def test_permission(self):
        """Test to see if normal users can access these pages"""
        a = User.objects.create_user("Albert", "albert@aol.com", "a")
        a.save()
        
        client = Client()
        client.login(username="Albert", password="a")
        
        # It redirects them away from the page, so assume that if we are redirected the page is safe
        self.assertTrue(client.get("/staff/").status_code, 302)
        self.assertTrue(client.get("/staff/course/add_users").status_code, 302)
        self.assertTrue(client.get("/staff/course/lession/files").status_code, 302)
        self.assertTrue(client.get("/staff/course/lession/delete-file").status_code, 302)
        self.assertTrue(client.get("/staff/~strain/1").status_code, 302)
        self.assertTrue(client.get("/staff/help/formatting").status_code, 302)
        self.assertTrue(client.get("/staff/help/general").status_code, 302)
    
    
    def test_add_to_course(self):
        """Tests adding students to courses using the page"""
        a = User.objects.create_user("Albert", "albert@aol.com", "a")
        a.save()
        b = User.objects.create_user("Brian", "brian@bmail.com", "b")
        b.save()
        c = User.objects.create_user("Catlyn", "catlyn@catmail.com", "c")
        c.save()
        s = User.objects.create_user("Super", "root@localhost", "password")
        s.is_staff = True
        s.save()
        
        client = Client()
        client.login(username="Super", password="password")
        
        course = Course(title="Test Course")
        course.save()
        
        # Initial
        self.assertFalse(a in course.users.all())
        self.assertFalse(b in course.users.all())
        self.assertFalse(c in course.users.all())
        
        # Adding users
        client.post("/staff/test-course/add_users", {"users":"Albert\nBrian"})
        
        course = Course.objects.get(pk=course.pk)
        self.assertTrue(a in course.users.all())
        self.assertTrue(b in course.users.all())
        self.assertFalse(c in course.users.all())
        
        # Removing and adding users
        client.post("/staff/test-course/add_users", {"users":"Albert\nCatlyn"})
        
        course = Course.objects.get(pk=course.pk)
        self.assertTrue(a in course.users.all())
        self.assertFalse(b in course.users.all())
        self.assertTrue(c in course.users.all())
        
        # Messy Usernames
        client.post("/staff/test-course/add_users", {"users":"Albert\n      Brian     [aaoceu] a caoe\b"})
        
        course = Course.objects.get(pk=course.pk)
        self.assertTrue(a in course.users.all())
        self.assertTrue(b in course.users.all())
        self.assertFalse(c in course.users.all())
        
        # Create user
        client.post("/staff/test-course/add_users", {"users":"Newton"})
        
        course = Course.objects.get(pk=course.pk)
        self.assertFalse(a in course.users.all())
        self.assertFalse(b in course.users.all())
        self.assertFalse(c in course.users.all())
        self.assertTrue(User.objects.get(username="Newton") in course.users.all())
        
        # Invalid usernames
        client.post("/staff/test-course/add_users", {"users":"HART@()!\b!$"})
        
        course = Course.objects.get(pk=course.pk)
        self.assertFalse(a in course.users.all())
        self.assertFalse(b in course.users.all())
        self.assertFalse(c in course.users.all())
        self.assertFalse(User.objects.filter(username="HART@()!\b!$").exists())
