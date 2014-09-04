"""Unit tests for tasks app"""
from django.test import TestCase

from django.contrib.auth.models import User
from courses.models import Course, Lesson, Section, Task
from tasks import utils

class TasksTestCase(TestCase):
    """Test case for tasks"""
    lang = "dummy"
    s = None
    u = None
    
    def setUp(self):
        """Sets up the test case by creating a sample text and user"""
        self.u = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        self.u.save()
        
        c = Course()
        c.save()
        l = Lesson(course=c)
        l.save()
        self.s = Section(lesson=l)
        self.s.save()
    
    def test_perform_execute(self):
        """Minimum functionality of utils.perform_execute"""
        t = Task(section=self.s, model_answer="replaced", language=self.lang)
        t.save()
        
        # Remember dummy replaces "replace_me" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, self.u)
        
        self.assertEqual(out, "replaced")
        self.assertTrue(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, self.u)
        
        self.assertEqual(out, "nope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", t, self.u)
        
        self.assertEqual(out, "replaced")
        self.assertTrue(is_correct)
        self.assertFalse(is_error)
    
    
    def test_no_automark(self):
        """Test tasks with automark being false"""
        t = Task(section=self.s, model_answer="replaced", language=self.lang, automark=False)
        t.save()
        
        # Remember dummy replaces "%replace" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, self.u)
        
        self.assertEqual(out, "replaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, self.u)
        
        self.assertEqual(out, "nope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", t, self.u)
        
        self.assertEqual(out, "replaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
    
    
    def test_pre_post(self):
        """Test to see if pre/post code is handled correctly"""
        t = Task(section=self.s, model_answer="replaced", language=self.lang, automark=False,
            hidden_pre_code="A", visible_pre_code="B", post_code="Z"
        )
        t.save()
        
        # Remember dummy replaces "%replace" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("replaced", t, self.u)
        
        self.assertEqual(out, "ABreplaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("nope", t, self.u)
        
        self.assertEqual(out, "ABnope")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", t, self.u)
        
        self.assertEqual(out, "ABreplaced")
        self.assertFalse(is_correct)
        self.assertFalse(is_error)

    def test_random(self):
        """Test to see if uses_random tasks are handled correctly"""
        t = Task(section=self.s, model_answer="%seed", language=self.lang, uses_random=True)
        t.save()
        
        # Remember dummy replaces "%replace" with "replaced"
        
        (out, media, is_error, is_correct) = utils.perform_execute("%seed", t, self.u)
        
        self.assertTrue(is_correct)
    
    def test_takes_prior(self):
        """Test to see if takes_prior tasks are handled correctly"""
        a = Task(section=self.s, model_answer="replaced", hidden_pre_code="a", language=self.lang)
        a.save()
        b = Task(section=self.s, model_answer="replaced", language=self.lang, takes_prior=True)
        b.save()
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", a, self.u)
        self.assertEqual(out, "areplaced")
        self.assertTrue(is_correct)
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", b, self.u)
        self.assertEqual(out, "replaced")
        self.assertTrue(is_correct)
        
    def test_takes_prior_random(self):
        """Test to see if takes_prior tasks with random seeds are handled correctly"""
        a = Task(section=self.s, model_answer="replaced", hidden_pre_code="%seed", language=self.lang, uses_random=True)
        a.save()
        b = Task(section=self.s, model_answer="replaced", language=self.lang, takes_prior=True)
        b.save()
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", a, self.u)
        self.assertTrue(is_correct)
        
        (out, media, is_error, is_correct) = utils.perform_execute("%replace", b, self.u)
        self.assertTrue(is_correct)
