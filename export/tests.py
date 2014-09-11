"""Unit tests for export system"""
from django.test import TestCase, Client
from django.contrib.auth.models import User

from export.parse import encode, decode
from export.forms import ImportForm
from courses.models import Course, Lesson, Section, Task

class ExportTestCase(TestCase):
    """Test case for exporting and importing"""
    def test_symmetry(self):
        """Test that encoding and decoding results in the same object"""
        self.assertEqual(decode(encode({})), {})
        self.assertEqual(decode(encode([])), [])
        
        self.assertEqual(decode(encode([1, 2, 3])), [1, 2, 3])
        self.assertEqual(decode(encode([[1, 2, 3], ["a", "b", "c"]])), [[1, 2, 3], ["a", "b", "c"]])
        self.assertEqual(decode(encode([[1, 2, 3], "multiline\nstring"])), [[1, 2, 3], "multiline\nstring"])
        self.assertEqual(decode(encode([{"list":[1, 2, 3]}])), [{"list":[1, 2, 3]}])
        
        self.assertEqual(decode(encode({"hello":"Hello", "world":"World"})), {"hello":"Hello", "world":"World"})
        self.assertEqual(decode(encode({"hello":"Hello", "world":["World"]})), {"hello":"Hello", "world":["World"]})
        self.assertEqual(decode(encode({"hello":"He\nllo", "world":["World"]})),{"hello":"He\nllo", "world":["World"]})
        self.assertEqual(decode(encode({"hello":"Hello: World"})),{"hello":"Hello: World"})
        
        self.assertEqual(decode(encode([None])), [None])
    
    
    def test_comments(self):
        """Test if the "comment type" works"""
        self.assertEqual(decode("""
        dict holder {a{
          comment lucky: This is a lucky number
          int mynum: 7
        }a}
        """), {"mynum":7})
        
        self.assertEqual(decode("""
        dict holder {a{
          comment lucky {b{
            No, seriously. Very lucky.
          }b}
          int mynum: 7
        }a}
        """), {"mynum":7})
    
    def test_blocks(self):
        """Test if block things {code{ work properly"""
        self.assertEqual(decode("""
        dict holder {{
          int mynum: 7
        }}
        """), {"mynum":7})
        
        self.assertEqual(decode("""
        dict holder {abcABC123{
          int mynum: 7
        }abcABC123}
        """), {"mynum":7})
        
        self.assertEqual(decode("""
        dict holder {abcABC123{
          dict nested {abcABC123{
            int yournum: 6
          }abcABC123}
          int mynum: 7
        }abcABC123}
        """), {"mynum":7, "nested":{"yournum":6}})
    
    def test_submit(self):
        """Test if submiting the course through the view actually works"""
        c = Course.objects.create(title="Test Course")
        c.save()
        l = Lesson.objects.create(course=c, title="Test Lesson")
        l.save()
        ol = Lesson.objects.create(course=c, title="Other Lesson")
        ol.save()
        a = Section.objects.create(lesson=l, title="Section 1")
        a.save()
        b = Section.objects.create(lesson=l, title="Section 2")
        b.save()
        ta = Task.objects.create(section=a, description="Task of a")
        ta.save()
        tb = Task.objects.create(section=b, description="Task of b")
        tb.save()
        
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        u.is_staff = True
        u.save()
        client = Client()
        client.login(username="Mittens", password="meow")
        
        # Export
        resp = client.get("/io/test-course/export")
        content = resp.content.decode("ascii")
        
        # Delete the course
        c.delete()
        
        self.assertFalse(Course.objects.filter(title="Test Course").exists())
        
        # Import it again
        client.post("/io/import",
            {"text":content, "mode":ImportForm.MODE_UPDATE, "user_mode":ImportForm.USER_MODE_NONE}
        )
        
        self.assertTrue(Course.objects.filter(title="Test Course").exists())
        self.assertTrue(Lesson.objects.filter(title="Test Lesson", course__title="Test Course").exists())
        self.assertTrue(Lesson.objects.filter(title="Other Lesson", course__title="Test Course").exists())
        self.assertTrue(Section.objects.filter(title="Section 1", lesson__title="Test Lesson").exists())
        self.assertTrue(Section.objects.filter(title="Section 2", lesson__title="Test Lesson").exists())
        self.assertTrue(Task.objects.filter(description="Task of a", section__title="Section 1").exists())
        self.assertTrue(Task.objects.filter(description="Task of b", section__title="Section 2").exists())
