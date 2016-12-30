"""
    Demonstration application for collision detection. Each shape
    added is a random circle.
    
    Left mouse adds circle.
    
    Assumes you have python-igraph and plotly installed. Assumes you have
    stored your API credentials locally to work.
    
"""

from tkinter import Tk, Canvas, ALL
import random

from quadtree.quad import QuadTree, RADIUS, MULTIPLE
from adk.region import Region, minValue, maxValue, X, Y

from quadtree.visualize import VisualizationWindow

# Attributes for Circle
# 0 (X) is its x-coordinate
# 1 (Y) is its y-coordinate
# 2 (RADIUS) is its radius
# 3 (HIT) records whether involved in a collision
# 4 (MULTIPLE) records whether circle is too big to fit in leaf node in quadtree
HIT = 3      

# Parameters for size of random circles       
MaxRadius = 30
MinRadius = 10

class QuadTreeFixedApp:
    
    def __init__(self, master):
        """App for creating Quad tree dynamically with fixed circles that detect collisions."""
        
        master.title("Click to add fixed circles for QuadTree collision detection.") 
        self.master = master 
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0,512,512))
        
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
        """Add circle to QuadTree with random radius."""
        circle = [event.x, self.toCartesian(event.y), random.randint(MinRadius, MaxRadius), False, False]
        
        # Mark these circles to have their HIT status set to True
        for circ in self.tree.collide(circle):
            circ[HIT] = True
            circle[HIT] = True
        
        self.tree.add(circle)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)
            
    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0,512,512))
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.clear()
        
    def visit (self, node):
        """ Visit nodes recursively."""
        if node == None: 
            return

        # draw rectangular region with criss-crossed hashed lines 
        r = node.region
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), r.x_max, self.toTk(r.y_max))
         
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), r.x_max, self.toTk(node.origin[Y]),
                                fill='black', dash=(2, 4)) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), node.origin[X], self.toTk(r.y_max),
                                fill='black', dash=(2, 4))
         
        for shape in node.shapes:
            markColor = 'Black'
            if shape[MULTIPLE]: markColor = 'Blue'
            if shape[HIT]: markColor = 'Red'
            self.canvas.create_oval(shape[X] - shape[RADIUS], self.toTk(shape[Y]) - shape[RADIUS], 
                                 shape[X] + shape[RADIUS], self.toTk(shape[Y]) + shape[RADIUS], 
                                 fill=markColor)
        for n in node.children:
            self.visit(n)
            
if __name__ == "__main__":
    root = Tk()
    app = QuadTreeFixedApp(root)
    app.viz = VisualizationWindow(root)
    root.mainloop()
