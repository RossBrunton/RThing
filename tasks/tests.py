from django.test import TestCase

from django.contrib.auth.models import User
from courses.models import Course, Lesson, Section, Task
from tasks import utils

class TasksTestCase(TestCase):
    lang = "dummy"
    
    def test_perform_execute(self):
        """Minimum functionality of utils.perform_execute"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        
        c = Course()
        l = Lesson(course=c)
        s = Section(lesson=l)
        t = Task(section=s, model_answer="replaced", language=self.lang)
        
        # Remember dummy replaces "replace_me" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, u)
        
        self.assertEqual(out, "replaced")
        self.assertTrue(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, u)
        
        self.assertEqual(out, "nope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("replace_me", t, u)
        
        self.assertEqual(out, "replaced")
        self.assertTrue(is_correct)
        self.assertFalse(is_error)
    
    
    def test_no_automark(self):
        """Test tasks with automark being false"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        
        c = Course()
        l = Lesson(course=c)
        s = Section(lesson=l)
        t = Task(section=s, model_answer="replaced", language=self.lang, automark=False)
        
        # Remember dummy replaces "replace_me" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, u)
        
        self.assertEqual(out, "replaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, u)
        
        self.assertEqual(out, "nope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("replace_me", t, u)
        
        self.assertEqual(out, "replaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
    
    
    def test_pre_post(self):
        """Test to see if pre/post code is handled correctly"""
        u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        
        c = Course()
        l = Lesson(course=c)
        s = Section(lesson=l)
        t = Task(section=s, model_answer="replaced", language=self.lang, automark=False,
            hidden_pre_code="A", visible_pre_code="B", post_code="Z"
        )
        
        # Remember dummy replaces "replace_me" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, u)
        
        self.assertEqual(out, "A\nB\nreplaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, u)
        
        self.assertEqual(out, "A\nB\nnope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("replace_me", t, u)
        
        self.assertEqual(out, "A\nB\nreplaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        
