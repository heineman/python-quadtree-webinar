import unittest

from quadtree.quad import QuadTree
from adk.region import Region

class TestQuadMethods(unittest.TestCase):

    def setUp(self):
        self.qt = QuadTree(Region(0,0,1024,1024))
        
        self.qt.add([22, 40, 10, False, False])
        self.qt.add([13, 59, 20, False, False])
        self.qt.add([57, 37, 30, False, False])
        self.qt.add([43, 21, 20, False, False])
        self.qt.add([33, 11, 10, False, False])
        
        
    def tearDown(self):
        self.qt = None
        
    def test_basic(self):
        self.assertTrue([43, 21, 20] in self.qt)
        self.assertFalse([21, 43, 11] in self.qt)
    
        # already present.
        self.assertFalse(self.qt.add([33, 11, 10, False, False]))
    
    def test_remove_less_than_four(self):
        self.qt = QuadTree(Region(0,0,1024,1024))
        
        self.qt.add([22, 40, 10, False, False])
        self.qt.add([13, 59, 20, False, False])
        self.qt.add([57, 37, 30, False, False])
        
        self.assertTrue(self.qt.remove([57, 37, 30]))
        self.assertTrue(self.qt.remove([13, 59, 20]))
        self.assertTrue(self.qt.remove([22, 40, 10]))
        
        self.assertFalse(self.qt.remove([57, 37, 30]))
        self.assertFalse(self.qt.remove([13, 59, 20]))
        self.assertFalse(self.qt.remove([22, 40, 10]))
        
    def test_remove(self):
        self.assertTrue (self.qt.remove([57, 37, 30]))
        ct = 0
        for _ in self.qt:
            ct += 1 
        self.assertEqual(4, ct)
        
        self.assertTrue(self.qt.remove([13, 59, 20]))
    
    def test_iteration(self):
        ct = 0
        for _ in self.qt:
            ct += 1 
        self.assertEqual(5, ct)
    
if __name__ == '__main__':
    unittest.main()    