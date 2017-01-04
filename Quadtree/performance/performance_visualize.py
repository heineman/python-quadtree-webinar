"""
    Visualizes point-based QuadTree structures.
    
    Left mouse adds point or removes it.
    
    Max tree size is 512x512 and scale factor determines the size of
    the individual points in the tree in pixels. For example, factor=64
    means that there are 8x8 points.
"""

from tkinter import Tk, ALL
from quadtree.visualize import VisualizationWindow
from app.app_point_visualize import QuadTreePointApp, label

# During testing, it was convenient to visualize a specific quad-tree, carefully
# designed to test edge cases. I've left the skeleton code here

def addPoints():
    """
    Add points which caused layout to become criss-crossed. This case identified
    a key step in the algorithm, namely to update the 'nexts' placemenet of 
    child nodes once the self.mod was computed.
    """
    app.tree.add([0,7])
    app.tree.add([4,7])
    
    for x in range(2, 8):
        for y in range(0, 4):
            app.tree.add([x,y])
    
    app.canvas.delete(ALL)
    app.visit(app.tree.root)
    app.viz.plot(app.tree.root)

if __name__ == '__main__':
    root = Tk()
    app = QuadTreePointApp(root, 64)     # pixels are 8x8 in size (or 512/64)
    app.viz = VisualizationWindow(root, label)
    root.after(250, addPoints)
    root.mainloop()
