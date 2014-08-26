from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client

from courses.models import Course, Lesson, Section, Task
from stats import utils
from stats.models import UserOnTask

class StatsTestCase(TestCase):
    f = None
    m = None
    t = None
    muot = None
    fuot = None
    
    def setUp(self):
        self.m = User.objects.create_user("Mittens", "mittensthekitten@gmail.com", "meow")
        self.m.save()
        self.f = User.objects.create_user("Fido", "fido@gmail.com", "woof")
        self.f.save()
        
        c = Course()
        c.save()
        l = Lesson(course=c)
        l.save()
        s = Section(lesson=l)
        s.save()
        self.t = Task(section=s, model_answer="replaced", language="dummy")
        self.t.save()
        
        self.muot = self.t.get_uot(self.m)
        self.fuot = self.t.get_uot(self.f)
    
    def test_stats(self):
        """Tests whether the utility functions work"""
        self.assertEqual(utils.attempts(task=self.t), 0)
        self.assertEqual(utils.correct(task=self.t), 0)
        self.assertEqual(utils.revealed(task=self.t), 0)
        self.assertEqual(utils.average_tries_correct(task=self.t), 0.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 0.0)
        self.assertEqual(utils.completion(task=self.t), 0.0)
        
        self.muot.tries += 1
        self.muot.save()
        self.fuot.tries += 5
        self.fuot.save()
        
        self.assertEqual(utils.attempts(task=self.t), 2)
        self.assertEqual(utils.correct(task=self.t), 0)
        self.assertEqual(utils.revealed(task=self.t), 0)
        self.assertEqual(utils.average_tries_correct(task=self.t), 0.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 0.0)
        self.assertEqual(utils.completion(task=self.t), 0.0)
        
        
