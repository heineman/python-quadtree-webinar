import unittest

from ds.bst import BinaryTree
import random

class TestBSTMethods(unittest.TestCase):

    def setUp(self):
        self.bst = BinaryTree()
        
    def populate(self):
        self.bst.add("answer")
        self.bst.add("ball")
        self.bst.add("center")
        self.bst.add("brilliant")
        self.bst.add("bright")
        self.bst.add("delay")
        self.bst.add("crazy")
        
    def tearDown(self):
        self.bst = None
        
    def test_basic(self):
        self.populate()
        
        self.assertTrue("center" in self.bst)
        
        
    def test_sameStarting(self):
        """Test interesting function that computes words with same starting letters."""
        self.populate()
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetters())
        print (intersections)
        # only word starting with 'a'
        self.assertTrue(['answer'] in intersections)
        
        # these words all start with 'c'; because traversal is inorder, words are in sorted order.
        self.assertTrue(['center', 'crazy'] in intersections)
        
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