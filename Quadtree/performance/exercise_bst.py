import unittest

from ds.bst0 import BinaryTree

"""
    Test cases that will only pass once bst0 is modified according to exercise.
"""

class TestBSTMethods(unittest.TestCase):

    def setUp(self):
        self.bst = BinaryTree()
        
    def populate(self):
        self.bst.add('seat')
        self.bst.add('sail')
        self.bst.add('east')
        self.bst.add('stir')
        self.bst.add('salt')
        self.bst.add('talk')
        
    def tearDown(self):
        self.bst = None
        
    def test_sameStarting(self):
        """Test function that computes words with same starting letters."""
        self.populate()
        
        # convert to list to use in multiple assertions.
        intersections = list(self.bst.sameStartingLetter('s'))
        
        # only word starting with 's'
        self.assertEqual(['sail', 'salt', 'seat', 'stir'], intersections)
        
    def test_anagram(self):
        """Validate anagram method."""
        self.populate()
         
        matches = list(self.bst.findAnagrams('teas'))
        self.assertEqual(['east', 'seat'], matches)
         
if __name__ == '__main__':
    unittest.main()    