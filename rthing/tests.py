"""Rthing test cases"""
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client

from rthing.utils import rand_str, py2_str
from rthing.templatetags.lformat import lformat

import six

class RthingTestCase(TestCase):
    """Tests for rthing app"""
    def test_rand_str(self):
        """Does rand_str work"""
        self.assertEqual(len(rand_str(5)), 5)
        self.assertEqual(len(rand_str(0)),0)
    
    def test_py2_str(self):
        """Does py2_str work"""
        
        string = u"Hello \u03a8\u03bf\u0393\u03b9\u0394"
        
        @py2_str
        class MyClass:
            def __str__(self):
                return string
        
        my = MyClass()
        
        if six.PY2:
            self.assertEqual(str(my), "Hello ")
            self.assertEqual(unicode(my), string)
        elif six.PY3:
            self.assertEqual(str(my), string)
            self.assertFalse(hasattr(my, "__unicode__"))
    
    
    def test_lformat(self):
        """Test lecturer formatting"""
        self.assertEquals("<div>Hello</div><div>World!</div>", lformat("Hello\n\nWorld!"))
        self.assertEquals("<div>Hello\nWorld!</div>", lformat("Hello\nWorld!"))
        
        self.assertTrue("<img" in lformat("[img]test.png[/img]", 0))
        self.assertFalse("<img" in lformat("[img]test.png[/img]"))
        self.assertTrue("<img" in lformat("[img]http://example.com/test.png[/img]"))
        
        self.assertTrue("<tag" in lformat("[html]<tag>Value</tag>[/html]"))
        
        self.assertFalse("<iframe" in lformat("[youtube]123[/youtube]", print_=True))
        self.assertTrue("<iframe" in lformat("[youtube]123[/youtube]"))
        
        self.assertTrue("<a href='http://example.com'>http://example.com</a>" in lformat("[url]http://example.com[/url]"))
        self.assertTrue("<a href='http://example.com'>Example</a>" in lformat("[url  http://example.com]Example[/url]"))
        
        self.assertTrue("http://example.com" in lformat("[url]http://example.com[/url]", print_=True))
        self.assertTrue("http://example.com" in lformat("[url  http://example.com]Example[/url]", print_=True))
        self.assertFalse("<a" in lformat("[url]http://example.com[/url]", print_=True))
        self.assertFalse("<a" in lformat("[url  http://example.com]Example[/url]", print_=True))
        
        self.assertTrue("l-warning" in lformat("Warning: Test this thing"))
        self.assertTrue("l-warning" in lformat("warning: Test this thing"))
        self.assertFalse("l-warning" in lformat("A word of warning: Test this thing"))
        self.assertTrue("l-note" in lformat("Note: This is a test"))
        self.assertTrue("l-note" in lformat("note: This is a test"))
        self.assertFalse("l-note" in lformat("Take note: This is a test"))
        self.assertTrue("l-info" in lformat("Info: Testing is good"))
        self.assertTrue("l-info" in lformat("info: Testing is good"))
        self.assertFalse("l-info" in lformat("Usefull info: Testing is good"))
        
        self.assertTrue("l-click" in lformat("Click #this# thing!"))
        
