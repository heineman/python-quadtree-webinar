import unittest

from quadtree.quad_region import QuadTree
from adk.region import Region
import random

class TestBSTMethods(unittest.TestCase):

    def setUp(self):
        self.qt = QuadTree(Region(0,0,8,8))
        
        
    def tearDown(self):
        self.qt = None
        
    def test_basic(self):
        
        self.qt.add((0, 0))
        
        self.assertTrue((0, 0) in self.qt)
        self.assertFalse((0, 1) in self.qt)
        
    def test_convertFull(self):
        
        self.qt.add((0, 0))
        self.qt.add((1, 1))
        self.qt.add((1, 0))
        
        self.assertTrue((0, 0) in self.qt)
        self.assertFalse((0, 1) in self.qt)
        self.assertTrue((1, 1) in self.qt)
        self.assertTrue((1, 0) in self.qt)
        
        # now make full
        self.qt.add((0, 1))
        
        self.assertTrue((0, 0) in self.qt)
        self.assertTrue((0, 1) in self.qt)
        self.assertTrue((1, 1) in self.qt)
        self.assertTrue((1, 0) in self.qt)
        
    def test_degradeFull(self):
        
        self.qt.add((0, 0))
        self.qt.add((1, 1))
        self.qt.add((1, 0))
        
        self.assertTrue((0, 0) in self.qt)
        self.assertFalse((0, 1) in self.qt)
        self.assertTrue((1, 1) in self.qt)
        self.assertTrue((1, 0) in self.qt)
        
        # now make full
        self.qt.add((0, 1))
        
        self.assertTrue((0, 0) in self.qt)
        self.assertTrue((0, 1) in self.qt)
        self.assertTrue((1, 1) in self.qt)
        self.assertTrue((1, 0) in self.qt)
        
        # now remove from full
        self.assertTrue(self.qt.remove((0,1)))
        
        # validate others are there
        self.assertTrue((0, 0) in self.qt)
        self.assertFalse((0, 1) in self.qt)
        self.assertTrue((1, 1) in self.qt)
        self.assertTrue((1, 0) in self.qt)

    def test_prune(self):
        
        self.qt.add((0, 0))
        self.assertTrue((0, 0) in self.qt)
        
        # now clear
        self.qt.remove((0, 0))
        
        self.assertFalse((0, 0) in self.qt)
        
    
    def test_createFull(self):
        """Randomly add all points and validate root node is full. Then remove one and validate not full."""
        toAdd = []
        for i in range(8):
            for j in range(8):
                toAdd.append((i,j))
                
        random.shuffle(toAdd)
        for pt in toAdd:
            self.assertTrue (self.qt.add(pt))
        
        self.assertTrue (self.qt.root.isFull())
        
        random.shuffle(toAdd)
        for pt in toAdd:
            self.assertTrue (self.qt.remove(pt))
            
        self.assertTrue (self.qt.root == None)

if __name__ == '__main__':
    unittest.main()    