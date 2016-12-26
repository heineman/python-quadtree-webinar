import unittest

from quadtree.quad import defaultCollision

class TestCollisionMethods(unittest.TestCase):

    def setUp(self):
        self.c1 = [20, 20, 20, False, False, 0, 0]
        self.c2 = [40, 40, 1, False, False, 0, 0]
        self.c3 = [18, 18, 1, False, False, 0, 0]
        
    def tearDown(self):
        pass
        
    def test_basic(self):
        self.assertFalse (defaultCollision(self.c1, self.c2));
        self.assertTrue  (defaultCollision(self.c3, self.c1));
        self.assertTrue  (defaultCollision(self.c1, self.c3));
           

if __name__ == '__main__':
    unittest.main()    