"""
    Demonstration application that ALMOST solves case with circles of fixed radius.
    The problem is that it only identifies collisions between circles IN THE
    SAME LEAFE NODE, since that is where a point-based quadtree stores its points.
    
    The other problem is that when it comes to collision detection, we can't
    represent a 2D-circle by a single point. And don't even get started on 
    trying to find neighbor regions based on the fixed Radius size, since that
    leads to more complicated inefficiencies.
    
    Left mouse adds circle. All collisions remain with each mouse click which 
    means we only need to check for collisions against the newly added circle.
"""

from tkinter import Tk, Canvas, ALL

from quadtree.quad_point import QuadTree, RADIUS
from adk.region import Region, minValue, maxValue, X, Y

# Attributes for Circle
# 0 (X) is its x-coordinate
# 1 (Y) is its y-coordinate
# 2 (RADIUS) is its radius
# 3 (HIT) records whether involved in a collision
HIT = 3      

# All circles have radius of 10 pixels
Radius = 10

def defaultCollision(c1, c2):
    """Two circles intersect if distance between centers is between the sum and the difference of radii."""
    centerDistance = (c1[X] - c2[X])**2 + (c1[Y] - c2[Y])**2
    sumSquared = (c1[RADIUS]+c2[RADIUS])**2
    if centerDistance > sumSquared: return False
    return True
 
def collide(node, circle):
    """Yield circles in point quadtree that intersect with circle."""
    if node != None:
        # if we have circles, must check them
        if node.points:
            for c in node.points:
                if defaultCollision(c, circle):
                    yield c
        
        # Find sub-quadrant into which to check further 
        q = node.quadrant(circle)
        for c in collide(node.children[q], circle):
            yield c

class QuadTreeInvalidApp:
    
    def __init__(self, master):
        """App for creating Quad tree dynamically with fixed circles that ALMOST ALWAYS detect collisions."""
        
        master.title("Click to add fixed circles for ALMOST detecting collisions.") 
        self.master = master 
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0,512,512))
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-2>", self.reset)      # needed for Mac
        self.canvas.bind("<Button-3>", self.reset)      # this is PC
        self.canvas.pack()

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
        circle = [event.x, self.toCartesian(event.y), Radius, False, False]
        
        # To find all collisions, take advantage of the fact that circles
        # can neither be modified nor deleted, so any new collisions are 
        # solely between the new circle and existing circles in the QuadTree.
        for circ in collide(self.tree.root, circle):
            circ[HIT] = 1
            circle[HIT] = 1
                
        self.tree.add(circle)
        self.canvas.delete(ALL)
        self.visit(self.tree.root)

    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0,512,512))
        self.canvas.delete(ALL)
        self.visit(self.tree.root)

    def visit (self, node):
        """Visit nodes recursively."""
        if node == None: 
            return

        # draw rectangular region with criss-crossed hashed lines 
        r = node.region
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), 
                                     r.x_max, self.toTk(r.y_max))
         
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), 
                                r.x_max, self.toTk(node.origin[Y]),
                                dash=(2, 4)) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), 
                                node.origin[X], self.toTk(r.y_max),
                                dash=(2, 4))
        
        if node.points: 
            for circle in node.points:
                markColor = 'black'
                if circle[HIT]: markColor = 'red'
                self.canvas.create_oval(circle[X] - circle[RADIUS], self.toTk(circle[Y]) - circle[RADIUS], 
                                        circle[X] + circle[RADIUS], self.toTk(circle[Y]) + circle[RADIUS], 
                                        fill=markColor)
        
        for n in node.children:
            self.visit(n)
            
if __name__ == '__main__':
    root = Tk()
    app = QuadTreeInvalidApp(root)
    root.mainloop()