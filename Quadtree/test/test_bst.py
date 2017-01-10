import random
import unittest

from ds.bst import BinaryTree

class TestBSTMethods(unittest.TestCase):

    def setUp(self):
        self.bst = BinaryTree()
        
    def populate(self):
        self.bst.add('answer')
        self.bst.add('trays')
        self.bst.add('ball')
        self.bst.add('teach')
        self.bst.add('brilliant')
        self.bst.add('bright')
        self.bst.add('stray')
        self.bst.add('cheat')
        
    def tearDown(self):
        self.bst = None
        
    def test_basic(self):
        self.populate()
        
        self.assertTrue("teach" in self.bst)
        
    def test_sameStarting(self):
        """Test function that computes words with same starting letters."""
        self.populate()
        
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetter('b'))
        
        # only word starting with 'b'
        self.assertEqual(['ball', 'bright', 'brilliant'], intersections)
        
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetter('t'))
        
        # only word starting with 't'
        self.assertEqual(['teach', 'trays'], intersections)
        
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetter('a'))
        
        # only word starting with 'a'
        self.assertEqual(['answer'], intersections)

    def test_sameStarting_empty(self):
        """Test interesting function that computes words with same starting letters."""
        self.populate()
        
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetter('g'))
        
        # only word starting with 'a'
        self.assertEqual([], intersections)
        
    def test_anagram(self):
        """Validate anagram method."""
        self.populate()
         
        matches = list(self.bst.findAnagrams('labl'))
        self.assertEqual(['ball'], matches)
         
        matches = list(self.bst.findAnagrams('teach'))
        self.assertEqual(['cheat', 'teach'], matches)
        
        matches = list(self.bst.findAnagrams('nothing'))
        self.assertEqual([], matches)
        
    
    def test_adding(self):
        """Work with integers."""
        for _ in range(1000):
            # make sure these are all even numbers
            n = random.randint(1,100000)
            if n % 2 == 1: 
                n += 1
            
            if not n in self.bst:
                self.bst.add(n)
                self.assertTrue(n in self.bst)        # n is there
                self.assertFalse((n+1) in self.bst)   # (n+1) is not since odd
           
    def test_degenerate(self):
        """Demonstrate how BST turns into linear list."""
        for _ in range(500):   # can't be too high otherwise exceed recursion depth
            if not _ in self.bst:
                self.bst.add(_)
                self.assertTrue(_ in self.bst)      
           

if __name__ == '__main__':
    unittest.main()    