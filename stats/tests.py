"""Unit tests for the stats app"""
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client

from courses.models import Course, Lesson, Section, Task
from stats import utils
from stats.models import UserOnTask

class StatsTestCase(TestCase):
    """Test case for stats"""
    
    def setUp(self):
        """Set up test cases, this creates users, a task and user on task instances"""
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
    
    def test_utils(self):
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
        
        self.muot.skipped = True
        self.muot.save()
        
        self.assertEqual(utils.attempts(task=self.t), 2)
        self.assertEqual(utils.correct(task=self.t), 0)
        self.assertEqual(utils.revealed(task=self.t), 0)
        self.assertEqual(utils.average_tries_correct(task=self.t), 0.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 0.0)
        self.assertEqual(utils.completion(task=self.t), 0.0)
        
        self.muot.state = UserOnTask.STATE_REVEALED
        self.muot.save()
        
        self.assertEqual(utils.attempts(task=self.t), 2)
        self.assertEqual(utils.correct(task=self.t), 0)
        self.assertEqual(utils.revealed(task=self.t), 1)
        self.assertEqual(utils.average_tries_correct(task=self.t), 0.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 1.0)
        self.assertEqual(utils.completion(task=self.t), 0.0)
        
        self.fuot.state = UserOnTask.STATE_REVEALED
        self.fuot.save()
        
        self.assertEqual(utils.attempts(task=self.t), 2)
        self.assertEqual(utils.correct(task=self.t), 0)
        self.assertEqual(utils.revealed(task=self.t), 2)
        self.assertEqual(utils.average_tries_correct(task=self.t), 0.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 3.0)
        self.assertEqual(utils.completion(task=self.t), 0.0)
        
        self.fuot.state = UserOnTask.STATE_CORRECT
        self.fuot.save()
        
        self.assertEqual(utils.attempts(task=self.t), 2)
        self.assertEqual(utils.correct(task=self.t), 1)
        self.assertEqual(utils.revealed(task=self.t), 1)
        self.assertEqual(utils.average_tries_correct(task=self.t), 5.0)
        self.assertEqual(utils.average_tries_reveal(task=self.t), 1.0)
        self.assertEqual(utils.completion(task=self.t), 0.5)
        
    def test_complete(self):
        """Tests whether the complete method on the Task model works"""
        self.assertEqual(self.t.complete(self.f), "none")
        
        self.fuot.skipped = True
        self.fuot.save()
        self.assertEqual(self.t.complete(self.f), "skipped")
        
        self.fuot.state = UserOnTask.STATE_CORRECT
        self.fuot.save()
        self.assertEqual(self.t.complete(self.f), "complete")
        
        self.fuot.state = UserOnTask.STATE_REVEALED
        self.fuot.save()
        self.assertEqual(self.t.complete(self.f), "revealed")
        
    def test_status(self):
        """Tests whether the status method on the UserOnTask model works"""
        self.assertEqual(self.fuot.status, "Not attempted yet")
        
        self.fuot.skipped = True
        self.assertEqual(self.fuot.status, "Skipped with no attempt")
        
        self.fuot.skipped = False
        self.fuot.state = UserOnTask.STATE_REVEALED
        self.assertEqual(self.fuot.status, "Revealed with no attempt")
        
        self.fuot.state = UserOnTask.STATE_NONE
        self.fuot.skipped = True
        self.fuot.tries += 7
        self.assertEqual(self.fuot.status, "Skipped")
        
        self.fuot.skipped = False
        self.assertEqual(self.fuot.status, "Attempted")
        
        self.fuot.state = UserOnTask.STATE_REVEALED
        self.assertEqual(self.fuot.status, "Revealed")
        
        self.fuot.state = UserOnTask.STATE_CORRECT
        self.assertEqual(self.fuot.status, "Correct")
