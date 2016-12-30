import unittest

from tkinter import Tk
from quadtree.quad import QuadTree
from quadtree.visualize import VisualizationWindow
from adk.region import Region

class TestBSTMethods(unittest.TestCase):

    def setUp(self):
        self.qt = QuadTree(Region(0,0,512,512))
        self.root = Tk()
        
        # This still causes problems with layout algorithm.
        self.qt.add([355, 394, 28, False, False])
        self.qt.add([125, 419, 28, False, False])
        self.qt.add([200, 459, 14, False, False])
        self.qt.add([38, 475, 13, False, False])
        self.qt.add([61, 330, 30, False, False])
        self.qt.add([199, 320, 24, False, False])
        self.qt.add([127, 152, 13, False, False])
        self.qt.add([397, 129, 27, False, False])
        
        self.window = VisualizationWindow(self.root)
        
    def tearDown(self):
        self.qt = None
        self.window.destroy()
        
    def test_basic(self):
        self.window.plot(self.qt.root)
        self.root.mainloop()
        
    
if __name__ == '__main__':
    unittest.main()    