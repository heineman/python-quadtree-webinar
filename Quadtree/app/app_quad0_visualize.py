"""
    Prototype app for adding points to an 8x8 quadtree with quad0 initial implementation.
"""

from tkinter import Tk, Canvas, ALL
from quadtree.quad0 import QuadTree
from adk.region import Region, minValue, maxValue, X, Y

from quadtree.visualize import VisualizationWindow

def label(node):
    """Show number of points as label."""
    if node.points is None:
        return 0
    return len(node.points)

class QuadTreePointApp:
    
    def __init__(self, master):
        """App for creating point-based quadtree dynamically."""
        
        master.title("Click to add points: [0,0] - (8,8)") 
        self.master = master 
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0, 8,8))
        
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
        """Add point to quadtree."""
        pt = [event.x // 64, self.toCartesian(event.y) // 64]
        self.tree.add(pt)

        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)
            
    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0, 8,8))
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.clear()
        
    def visit (self, node):
        """ Visit nodes recursively."""
        if node == None: 
            return

        # draw rectangular region with criss-crossed hashed lines 
        r = node.region
        self.canvas.create_rectangle(64 * r.x_min,
                                     64 * self.toTk(r.y_min),
                                     64 * r.x_max, 
                                     64 * self.toTk(r.y_max))
         
        self.canvas.create_line(64 * r.x_min,
                                self.toTk(64 * node.origin[Y]),
                                64 * r.x_max,
                                self.toTk(64 * node.origin[Y]),
                                dash=(2,4)) 
        self.canvas.create_line(64 * node.origin[X],
                                self.toTk(64 * r.y_min),
                                64 * node.origin[X],
                                self.toTk(64 * r.y_max),
                                dash=(2,4))
         
        if node.points:
            for pt in node.points:
                self.canvas.create_rectangle(64 * pt[X],
                                             self.toTk(64 * pt[Y]),
                                             64 * (pt[X]+1),
                                             self.toTk(64 * (pt[Y]+1)),
                                             fill='black')
        for n in node.children:
            self.visit(n)
            
if __name__ == '__main__':
    root = Tk()
    app = QuadTreePointApp(root)
    app.viz = VisualizationWindow(root, label)
    root.mainloop()
