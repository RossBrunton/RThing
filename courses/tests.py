from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client

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
        
        # Saving the model should not change it's slug (there was a bug where it would add another number since the slug
        # was already taken by itself)
        c.save()
        self.assertEqual(c.slug, "test-course")
        c.save()
        self.assertEqual(c.slug, "test-course")
        
        d.save()
        self.assertEqual(d.slug, "test-course-1")
        d.save()
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
    
    
    def test_lookup_course(self):
        """Test to see if course lookup works with regards to permissions"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        c = Client()
        c.login(username="Mittens", password="meow")
        
        course = Course(title="Test Course")
        course.save()
        
        self.assertEqual(c.get("/courses/no-such-course/", follow=True).status_code, 404)
        self.assertEqual(c.get("/courses/test-course/", follow=True).status_code, 404)
        course.users.add(u)
        course.published = True
        course.save()
        self.assertEqual(c.get("/courses/test-course/").status_code, 200)
    
    
    def test_lookup_lesson(self):
        """Test to see if lesson lookup works with regards to permissions"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        c = Client()
        c.login(username="Mittens", password="meow")
        
        course = Course(title="Test Course")
        course.save()
        lesson = Lesson(title="Test Lesson", course=course)
        
        self.assertEqual(c.get("/courses/test-course/no-such-lesson", follow=True).status_code, 404)
        self.assertEqual(c.get("/courses/test-course/test-lesson", follow=True).status_code, 404)
        course.users.add(u)
        course.published = True
        course.save()
        self.assertEqual(c.get("/courses/test-course/").status_code, 200)
        self.assertEqual(c.get("/courses/test-course/test-lesson", follow=True).status_code, 404)
        
        lesson.published = True
        lesson.save()
        self.assertEqual(c.get("/courses/test-course/test-lesson", follow=True).status_code, 200)
    
    
    def test_traversable_ordered_model(self):
        """Test to see if traversable ordered model works"""
        c = Course.objects.create()
        l = Lesson.objects.create(course=c)
        s = Section.objects.create(lesson=l)
        a = Task.objects.create(section=s)
        a.save()
        b = Task.objects.create(section=s)
        b.save()
        
        self.assertEqual(a.order, 0)
        self.assertEqual(b.order, 1)
        
        self.assertEqual(a.previous(), None)
        self.assertEqual(b.previous(), a)
        self.assertEqual(a.next(), b)
        self.assertEqual(b.next(), None)
