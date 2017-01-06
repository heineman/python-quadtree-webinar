import unittest

from quadtree.quad import defaultCollision, intersectsCircle
from adk.region import Region

class TestCollisionMethods(unittest.TestCase):

    def test_basic(self):
        self.c1 = [20, 20, 20, False, False]
        self.c2 = [40, 40, 1, False, False]
        self.c3 = [18, 18, 1, False, False]
        
        self.assertFalse (defaultCollision(self.c1, self.c2))
        self.assertTrue  (defaultCollision(self.c3, self.c1))
        self.assertTrue  (defaultCollision(self.c1, self.c3))
    
        self.assertTrue  (defaultCollision(self.c1, self.c1))
           
    def test_circleInCircle(self):
        self.c1 = [20, 20, 20, False, False]
        self.c2 = [20, 20, 5, False, False]
         
        self.assertTrue (defaultCollision(self.c1, self.c2))
        self.assertTrue (defaultCollision(self.c2, self.c1))
        
    def test_edgeCase(self):
        """Share edge point."""
        self.c1 = [4, 4, 2, False, False]
        self.c2 = [8, 4, 2, False, False]
         
        self.assertTrue (defaultCollision(self.c1, self.c2))
        self.assertTrue (defaultCollision(self.c2, self.c1))
        
    def test_missed(self):
        """Just missing each other."""
        self.c1 = [4, 4, 2, False, False]
        self.c2 = [8.0001, 4, 2, False, False]
         
        self.assertFalse (defaultCollision(self.c1, self.c2))
        self.assertFalse (defaultCollision(self.c2, self.c1))
        
    def test_edgeRegionCase(self):
        """Multiple cases."""
        r = Region(10, 10, 20, 20)
         
        self.assertTrue (intersectsCircle(r, [16, 16, 2, False, False]))  # circle wholly in region
        self.assertTrue (intersectsCircle(r, [8, 10, 2, False, False]))   # left-edge
        self.assertTrue (intersectsCircle(r, [10, 8, 2, False, False]))   # bottom-left corner
        self.assertTrue (intersectsCircle(r, [20, 8, 2, False, False]))   # bottom-right corner
        self.assertTrue (intersectsCircle(r, [14, 6, 5, False, False]))   # bottom-edge
        
        self.assertTrue (intersectsCircle(r, [15, 22, 2, False, False]))  # top-edge
        self.assertTrue (intersectsCircle(r, [22, 16, 2, False, False]))  # right-edge
        self.assertTrue (intersectsCircle(r, [20, 22, 2, False, False]))  # top-right corner
        self.assertTrue (intersectsCircle(r, [10, 22, 2, False, False]))  # top-left corner
        
        self.assertTrue (intersectsCircle(r, [0, 0, 40, False, False]))   # circle consumes r
       
        # fails
        self.assertFalse (intersectsCircle(r, [6, 10, 2, False, False]))   # miss to left
        self.assertFalse (intersectsCircle(r, [26, 10, 2, False, False]))  # miss to right
        self.assertFalse (intersectsCircle(r, [14, 23, 2, False, False]))  # miss to top
        self.assertFalse (intersectsCircle(r, [14, 7, 2, False, False]))   # miss to bottom
       
if __name__ == '__main__':
    unittest.main()    
