import random
import unittest

from quadtree.quad_point import QuadTree
from adk.region import Region

class TestQuadPointMethods(unittest.TestCase):

    def setUp(self):
        self.qt = QuadTree(Region(0,0,1024,1024))
        
        self.qt.add((22, 40))
        self.qt.add((13, 59))
        self.qt.add((57, 37))
        self.qt.add((43, 21))
        self.qt.add((33, 11))
        
    def tearDown(self):
        self.qt = None
        
    def test_basic(self):
        self.assertTrue((43, 21) in self.qt)
        self.assertFalse((21, 43) in self.qt)
       
    def test_adding(self):
        for _ in range(1000):
            # make sure these are even (within 0..1023, even incremented ones)
            x = random.randint(0,1021)
            if x % 2 == 1: 
                x += 1
            y = random.randint(0,1021)
            if y % 2 == 1: 
                y += 1
                
            pt = (x, y)
            badpt = (x+1, y+1)
            self.qt.add(pt)
            self.assertTrue(pt in self.qt)           # (x,y) is there
            self.assertFalse(badpt in self.qt)       # different indices not present
        
    def test_iteration(self):
        self.qt = QuadTree(Region(0,0,1024,1024))
        points = []
        for _ in range(100):
            x = random.randint(0,1021)
            y = random.randint(0,1021)
            points.append((x,y))
            self.qt.add((x,y))
    
        for pt in self.qt:
            self.assertTrue(pt in points)
        
    
if __name__ == '__main__':
    unittest.main()    