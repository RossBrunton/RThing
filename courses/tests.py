from django.test import TestCase

from .models import Course, Lesson, Section, Task

class CoursesTestCase(TestCase):
    def test_autoslug(self):
        """Is the slug field set correctly"""
        c = Course(title="Hello World!")
        c.save()
        self.assertEqual(c.slug, "hello-world")
        
        l = Lesson(title="Hello World!", course=c)
        l.save()
        self.assertEqual(l.slug, "hello-world")
        
        s = Section(title="Hello World!", lesson=l)
        s.save()
        self.assertEqual(s.slug, "hello-world")
        
        s.title = "Goodbye World!"
        s.save()
        self.assertEqual(s.slug, "goodbye-world")
