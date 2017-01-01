"""
    Visualizes region-based QuadTree structures
    
    Left mouse adds point or removes it.
    
    Max tree size is 512x512 and scale factor determines the size of
    the individual points in the tree in pixels. For example, factor=64
    means that there are 8x8 points.
    
"""

from tkinter import Tk, Canvas, ALL

from quadtree.quad_region import QuadTree
from adk.region import Region, minValue, maxValue, X, Y

from quadtree.visualize import VisualizationWindow

def label(node):
    """return size as label."""
    return node.region.x_max - node.region.x_min

class QuadTreePointApp:
    
    def __init__(self, master, factor):
        """App for creating point-based quadtree dynamically."""
        
        master.title("Click to add/remove points:" + str(factor) + "x" + str(factor)) 
        self.master = master 
        self.factor = factor
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0, 512//factor,512//factor))
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-2>", self.reset)      # Needed for Mac
        self.canvas.bind("<Button-3>", self.reset)      # This is PC
        self.canvas.pack()

        # no visualization just yet
        self.viz = None

    def toCartesian(self, y):
        """Convert tkinter point into Cartesian."""
        return self.canvas.winfo_height() - y

    def toTk(self,y):
        """Convert Cartesian into tkinter point."""
        if y == maxValue: return 0
        tk_y = self.canvas.winfo_height()
        if y != minValue:
            tk_y -= y
        return tk_y
         
    def click(self, event):
        """Add point to quadtree, based on factor."""
        pt = [event.x // self.factor, self.toCartesian(event.y) // self.factor]
        if pt in self.tree:
            self.tree.remove(pt)
        else:
            self.tree.add(pt)

        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)
            
    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0, 512//self.factor,512//self.factor))
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.clear()
        
    def visit (self, node):
        """ Visit nodes recursively."""
        if node == None: 
            return

        # draw rectangular region with criss-crossed hashed lines 
        r = node.region
        self.canvas.create_rectangle(self.factor * r.x_min,
                                     self.factor * self.toTk(r.y_min),
                                     self.factor * r.x_max, 
                                     self.factor * self.toTk(r.y_max))
         
        self.canvas.create_line(self.factor * r.x_min,
                                self.toTk(self.factor * node.origin[Y]),
                                self.factor * r.x_max,
                                self.toTk(self.factor * node.origin[Y]),
                                fill='black', dash=(2, 4)) 
        self.canvas.create_line(self.factor * node.origin[X],
                                self.toTk(self.factor * r.y_min),
                                self.factor * node.origin[X],
                                self.toTk(self.factor * r.y_max),
                                fill='black', dash=(2, 4))
         
        if node.isPoint() or node.isFull():
            pt = [node.region.x_min, node.region.y_min]
            width = node.region.x_max - node.region.x_min
            self.canvas.create_rectangle(self.factor * pt[X],
                                         self.toTk(self.factor * pt[Y]),
                                         self.factor * (pt[X]+width),
                                         self.toTk(self.factor * (pt[Y]+width)),
                                         fill='black')
        for n in node.children:
            self.visit(n)
            
if __name__ == "__main__":
    root = Tk()
    app = QuadTreePointApp(root, 64)
    app.viz = VisualizationWindow(root, label)
    root.mainloop()
