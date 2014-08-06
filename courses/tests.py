from django.contrib.auth.models import User, Permission
from django.test import TestCase

from courses.models import Course, Lesson, Section, Task

class CoursesTestCase(TestCase):
    def test_autoslug(self):
        """Is the slug field set correctly"""
        # Courses...
        c = Course(title="Hello World!")
        c.save()
        self.assertEqual(c.slug, "hello-world")
        
        # Lessons...
        l = Lesson(title="Hello World!", course=c)
        l.save()
        self.assertEqual(l.slug, "hello-world")
        
        # And sections
        s = Section(title="Hello World!", lesson=l)
        s.save()
        self.assertEqual(s.slug, "hello-world")
        
        # And check if changing the value works
        s.title = "Goodbye World!"
        s.save()
        self.assertEqual(s.slug, "goodbye-world")
    
    def test_slug_duplication(self):
        """Slugs should be unique"""
        c = Course(title="Test Course")
        c.save()
        
        d = Course(title="Test Course!")
        d.save()
        
        self.assertNotEqual(c.slug, d.slug)
        self.assertEqual(c.slug, "test-course")
        self.assertEqual(d.slug, "test-course-1")
    
    
    def test_can_see(self):
        """Test the can_see function"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        c = Course(title="Test Course")
        c.save()
        
        self.assertFalse(c.can_see(u))
        c.published = True
        self.assertFalse(c.can_see(u))
        c.users.add(u)
        self.assertTrue(c.can_see(u))
        c.published = False
        self.assertFalse(c.can_see(u))
        
        # Check to see if permissions work
        u.user_permissions.add(Permission.objects.get(codename="read_all").pk)
        u.save()
        
        # Need to get the user again to reflect permission change
        u = User.objects.get(pk=u.pk)
        
        self.assertTrue(c.can_see(u))
    
    
    def test_get_courses(self):
        """Test the get_courses function"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        c = Course(title="Test Course")
        c.save()
        
        self.assertEqual(len(Course.get_courses(u)), 0)
        c.published = True
        c.save()
        self.assertEqual(len(Course.get_courses(u)), 0)
        c.users.add(u)
        c.save()
        self.assertEqual(len(Course.get_courses(u)), 1)
        c.published = False
        c.save()
        self.assertEqual(len(Course.get_courses(u)), 0)
        c.published = True
        c.save()
        
        # Check to see if having more than one course works
        d = Course(title="Test Course 2")
        d.save()
        
        self.assertEqual(len(Course.get_courses(u)), 1)
        self.assertEqual(Course.get_courses(u)[0], c)
        d.published = True
        d.save()
        self.assertEqual(len(Course.get_courses(u)), 1)
        self.assertEqual(Course.get_courses(u)[0], c)
        d.users.add(u)
        d.save()
        self.assertEqual(len(Course.get_courses(u)), 2)
        d.published = False
        d.save()
        self.assertEqual(len(Course.get_courses(u)), 1)
        self.assertEqual(Course.get_courses(u)[0], c)
        
        # Check to see if permissions work
        u.user_permissions.add(Permission.objects.get(codename="read_all").pk)
        u.save()
        
        # Need to get the user again to reflect permission change
        u = User.objects.get(pk=u.pk)
        
        self.assertEqual(len(Course.get_courses(u)), 2)
        
