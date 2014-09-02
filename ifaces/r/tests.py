from django.test import TestCase

from ifaces import r

class RTestCase(TestCase):
    def test_equivalence(self):
        """Test that is_equivilant works"""
        self.assertTrue(r.is_equivalent("", ""))
        
        self.assertTrue(r.is_equivalent("1 + 1", "1 + 1"))
        self.assertTrue(r.is_equivalent("1+1", "1 + 1"))
        self.assertTrue(r.is_equivalent("1 + 1", "1+1"))
        
        self.assertTrue(r.is_equivalent("   1 + 1", "1 + 1"))
        self.assertTrue(r.is_equivalent("1 + 1", "     1 + 1"))
        self.assertTrue(r.is_equivalent("1 + 1     ", "1 + 1"))
        self.assertTrue(r.is_equivalent("1 + 1", "1 + 1    "))
        
        self.assertTrue(r.is_equivalent("print()", "print()"))
        self.assertTrue(r.is_equivalent("print ()", "print()"))
        self.assertTrue(r.is_equivalent("print()", "print ()"))
        
        self.assertTrue(r.is_equivalent("print()", "print()"))
        self.assertTrue(r.is_equivalent("print( )", "print()"))
        self.assertTrue(r.is_equivalent("print()", "print( )"))
        
        self.assertFalse(r.is_equivalent("pr int()", "print()"))
        self.assertFalse(r.is_equivalent("print()", "pr int()"))
        
        self.assertFalse(r.is_equivalent("print('Hello World!')", "print('Hello  World!')"))
        self.assertFalse(r.is_equivalent("print('Hello  World!')", "print('Hello World!')"))
        self.assertTrue(r.is_equivalent("print('Hello World!')", "print('Hello World!')"))
        
        self.assertFalse(r.is_equivalent("print('Hello \\'World!')", "print('Hello \\'   World!')"))
        self.assertTrue(r.is_equivalent("print('Hello \\'World!')", "print('Hello \\'World!')"))
        
        self.assertTrue(r.is_equivalent("print( 'Hello World!')", "print('Hello World!')"))
        self.assertTrue(r.is_equivalent("print('Hello World!')", "print( 'Hello World!')"))
        self.assertTrue(r.is_equivalent("print('Hello World!' )", "print('Hello World!')"))
        self.assertTrue(r.is_equivalent("print('Hello World!')", "print('Hello World!' )"))
        
        self.assertTrue(r.is_equivalent("1.5", "1.5"))
        self.assertFalse(r.is_equivalent("1. 5", "1.5"))
        self.assertFalse(r.is_equivalent("1.5", "1. 5"))
        self.assertFalse(r.is_equivalent("1 .5", "1.5"))
        self.assertFalse(r.is_equivalent("1.5", "1 .5"))
        
        self.assertTrue(r.is_equivalent("1.5e+12", "1.5e+12"))
        self.assertTrue(r.is_equivalent("1.5e-12", "1.5e-12"))
        
        self.assertFalse(r.is_equivalent("1.5e +12", "1.5e+12"))
        self.assertFalse(r.is_equivalent("1.5e+12", "1.5e +12"))
        self.assertFalse(r.is_equivalent("1.5e+ 12", "1.5e+12"))
        self.assertFalse(r.is_equivalent("1.5e+12", "1.5e+ 12"))
        self.assertFalse(r.is_equivalent("1.5e +12", "1.5e+12"))
        self.assertFalse(r.is_equivalent("1.5e+12", "1.5e +12"))
        
        self.assertFalse(r.is_equivalent("1.5e -12", "1.5e-12"))
        self.assertFalse(r.is_equivalent("1.5e-12", "1.5e -12"))
        self.assertFalse(r.is_equivalent("1.5e- 12", "1.5e-12"))
        self.assertFalse(r.is_equivalent("1.5e-12", "1.5e- 12"))
        self.assertFalse(r.is_equivalent("1.5e -12", "1.5e-12"))
        self.assertFalse(r.is_equivalent("1.5e-12", "1.5e -12"))
        
        self.assertTrue(r.is_equivalent("0xff", "0xff"))
        self.assertFalse(r.is_equivalent("0xff", "0x ff"))
        self.assertFalse(r.is_equivalent("0x ff", "0xff"))
        self.assertFalse(r.is_equivalent("0xff", "0 xff"))
        self.assertFalse(r.is_equivalent("0 xff", "0xff"))
        
        self.assertTrue(r.is_equivalent("plot(1:10, 1:10)", "plot(1:10, 1:10)"))
        self.assertTrue(r.is_equivalent("plot(1:10, 1:10)", "plot(1:10,1:10)"))
        self.assertTrue(r.is_equivalent("plot(1:10,1:10)", "plot(1:10, 1:10)"))
        self.assertTrue(r.is_equivalent("plot(1:10, 1:10)", "plot(1:10 ,1:10)"))
        self.assertTrue(r.is_equivalent("plot(1:10 , 1:10)", "plot(1:10, 1:10)"))
