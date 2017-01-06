import random
import unittest

from quadtree.quad_region import QuadTree, NE, NW, SW, SE
from adk.region import Region

class TestQuadRegionMethods(unittest.TestCase):

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
        self.assertTrue (self.qt.root is None)
        
    def test_presentation(self):
        self.qt.add((7,4))
        self.qt.add((3,4))
        self.qt.add((4,6))
        self.qt.add((6,6))
        self.qt.add((5,1))
        self.qt.add((4,3))
        self.qt.add((7,7))
        self.qt.add((2,5))
        self.qt.add((5,3))
        self.qt.add((4,5))
        self.qt.add((7,6))
        self.qt.add((5,2))
        self.qt.add((7,5))
        self.qt.add((4,4))
        self.qt.add((5,4))
        self.qt.add((4,7))
        self.qt.add((5,7))
        self.qt.add((5,6))
        self.qt.add((6,5))
        self.qt.add((2,4))
        self.qt.add((3,5))
        self.qt.add((6,7))
        self.qt.add((6,4))
        self.qt.add((5,5))
        self.qt.add((4,2))
        
        # Top-level
        self.assertTrue(self.qt.root.children[SW] == None)
        self.assertTrue(self.qt.root.children[NE].full)
        
        # second level
        self.assertTrue(self.qt.root.children[NW].children[SE].full)
        self.assertTrue(self.qt.root.children[SE].children[NW].full)
        
        # third level
        self.assertTrue(self.qt.root.children[SE].children[SW].children[NE].isPoint())
        self.assertTrue(self.qt.root.children[SE].children[SW].children[NE].full)
        
    def test_presentation_odd(self):
        self.qt.add((3,4))
        self.qt.add((4,3))
        
        # Top-level
        self.assertTrue(self.qt.root.children[NE] == None)
        self.assertTrue(self.qt.root.children[SW] == None)
        
        # last level
        self.assertTrue(self.qt.root.children[NW].children[SE].children[SE].isPoint())
        self.assertTrue(self.qt.root.children[NW].children[SE].children[SE].full)
        
        self.assertTrue(self.qt.root.children[SE].children[NW].children[NW].isPoint())
        self.assertTrue(self.qt.root.children[SE].children[NW].children[NW].full)
        
    def test_checkerboard(self):
        for i in range(8):
            for j in range(8):
                if (i+j) %2 == 0:
                    self.assertTrue(self.qt.add((i,j)))
                    
        for i in range(8):
            for j in range(8):
                if (i+j) %2 == 0:
                    self.assertTrue((i,j) in self.qt)

        # now fill in others.
        for i in range(8):
            for j in range(8):
                if (i+j) %2 == 1:
                    self.assertTrue(self.qt.add((i,j)))
        
        self.assertTrue (self.qt.root.full)
        for i in range(8):
            for j in range(8):
                self.assertTrue((i,j) in self.qt)
    
    def test_createFull(self):
        """Randomly add all points and validate root node is full. Then remove one and validate not full."""
        toAdd = []
        for i in range(8):
            for j in range(8):
                toAdd.append((i,j))
                
        random.shuffle(toAdd)
        for pt in toAdd:
            self.assertTrue (self.qt.add(pt))
        
        self.assertTrue (self.qt.root.full)
        
        random.shuffle(toAdd)
        for pt in toAdd:
            self.assertTrue (self.qt.remove(pt))
            
        self.assertTrue (self.qt.root == None)
        
    def test_iteration(self):
        
        self.qt.add((0, 0))
        
        grab = list(self.qt.__iter__())
        
        self.assertEquals ([(0,0)], grab)
        
    def test_iteration_with_full(self):
        
        self.qt.add((0, 0))
        self.qt.add((1, 1))
        self.qt.add((1, 0))
        self.qt.add((0, 1))
        
        grab = list(self.qt.__iter__())
        
        self.assertEquals ([(0,0),(0,1),(1,0),(1,1)], grab)
    
    def test_checkerboard_iterator(self):
        actual = []
        for i in range(8):
            for j in range(8):
                if (i+j) %2 == 0:
                    actual.append((i,j))
                    self.assertTrue(self.qt.add((i,j)))
                    
        grab = list(self.qt.__iter__())
        
        # validate all points are there.
        for pt in actual:
            self.assertTrue(pt in grab)
        for pt in grab:
            self.assertTrue(pt in actual)

    def test_iteration_more(self):
        self.qt = QuadTree(Region(0,0,1024,1024))
        points = []
        for _ in range(100):
            x = random.randint(0,1021)
            y = random.randint(0,1021)
            points.append((x,y))
            self.qt.add((x,y))
    
        for pt in self.qt:
            self.assertTrue(pt in points)

    def test_cleanup(self):
        self.qt = QuadTree(Region(0,0,128,128))
        actual = []
        for i in range(128):
            for j in range(128):
                actual.append((i,j))
        
        # For five times, add all randomly and remove randomly until
        # tree is entirely empty
        for i in range(5):
            random.shuffle(actual)
           
            for pt in actual:
                self.assertTrue(self.qt.add(pt))             
            
            random.shuffle(actual)
            
            for pt in actual:
                self.assertTrue(self.qt.remove(pt))     
                
            self.assertTrue(self.qt.root == None)

if __name__ == '__main__':
    unittest.main()    