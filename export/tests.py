"""Unit tests for export system"""
from django.test import TestCase

from export.parse import encode, decode

class ExportTestCase(TestCase):
    """Test case for exporting and importing"""
    def test_symmetry(self):
        """Test that encoding and decoding results in the same object"""
        self.assertEquals(decode(encode({})), {})
        self.assertEquals(decode(encode([])), [])
        
        self.assertEquals(decode(encode([1, 2, 3])), [1, 2, 3])
        self.assertEquals(decode(encode([[1, 2, 3], ["a", "b", "c"]])), [[1, 2, 3], ["a", "b", "c"]])
        self.assertEquals(decode(encode([[1, 2, 3], "multiline\nstring"])), [[1, 2, 3], "multiline\nstring"])
        self.assertEquals(decode(encode([{"list":[1, 2, 3]}])), [{"list":[1, 2, 3]}])
        
        self.assertEquals(decode(encode({"hello":"Hello", "world":"World"})), {"hello":"Hello", "world":"World"})
        self.assertEquals(decode(encode({"hello":"Hello", "world":["World"]})), {"hello":"Hello", "world":["World"]})
        self.assertEquals(decode(encode({"hello":"He\nllo", "world":["World"]})),{"hello":"He\nllo", "world":["World"]})
        self.assertEquals(decode(encode({"hello":"Hello: World"})),{"hello":"Hello: World"})
        
        self.assertEquals(decode(encode([None])), [None])
    
    
    def test_comments(self):
        """Test if the "comment type" works"""
        self.assertEquals(decode("""
        dict holder {a{
          comment lucky: This is a lucky number
          int mynum: 7
        }a}
        """), {"mynum":7})
        
        self.assertEquals(decode("""
        dict holder {a{
          comment lucky {b{
            No, seriously. Very lucky.
          }b}
          int mynum: 7
        }a}
        """), {"mynum":7})
    
    def test_blocks(self):
        """Test if block things {code{ work properly"""
        self.assertEquals(decode("""
        dict holder {{
          int mynum: 7
        }}
        """), {"mynum":7})
        
        self.assertEquals(decode("""
        dict holder {abcABC123{
          int mynum: 7
        }abcABC123}
        """), {"mynum":7})
        
        self.assertEquals(decode("""
        dict holder {abcABC123{
          dict nested {abcABC123{
            int yournum: 6
          }abcABC123}
          int mynum: 7
        }abcABC123}
        """), {"mynum":7, "nested":{"yournum":6}})
