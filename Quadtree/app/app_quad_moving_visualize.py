"""
    Demonstration application for collision detection. Each shape
    added is a random circle.
    
    Left mouse adds circle.
    
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
DX = 5
DY = 6

# With each passing frame, decrease by one to allow human-perception of collision
MaxHit = 3

# Refresh every 40 milliseconds
frameDelay = 40

# Parameters for size of random circles       
MaxRadius = 30
MinRadius = 10

def label(node):
    """Return integer to display in node."""
    if node.circles:
        return len(node.circles)
    else:
        return 0

class QuadTreeFixedApp:
    
    defaultTitle = 'Left-Click adds circle. Right click pauses motion.'
    pausedTitle  = 'Left-Click resumes. Right-click resets.'
    
    def __init__(self, master):
        """App for creating QuadTree with moving circles that detect collisions."""
        
        master.title(QuadTreeFixedApp.defaultTitle) 
        self.master = master 
        self.paused = False
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0,512,512))
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-2>", self.pause)      # Needed for Mac
        self.canvas.bind("<Button-3>", self.pause)      # This is PC
        self.master.after(frameDelay, self.updateLocations)
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
         
    def restart(self):
        """Restart motion."""
        self.master.after(frameDelay, self.updateLocations)
        self.master.title(QuadTreeFixedApp.defaultTitle) 
        self.paused = False
    
    def click(self, event):
        """Add circle to QuadTree with random radius and direction."""
        if self.paused:
            self.restart()
        else:
            dx = random.randint(1,4)*(2*random.randint(0,1)-1)
            dy = random.randint(1,4)*(2*random.randint(0,1)-1)
            circle = [event.x, self.toCartesian(event.y), 
                      random.randint(4, MaxRadius), False, False, dx, dy]
        
            self.tree.add(circle)

    def pause(self, event):
        """Pause or Reset to start state (if already paused)."""
        if self.paused:
            self.tree = QuadTree(Region(0,0,512,512))
            self.canvas.delete(ALL)
            self.visit(self.tree.root)
            self.viz.clear()
            self.restart()
        else:
            self.paused = True
            self.master.title(QuadTreeFixedApp.pausedTitle) 

    def visit(self, node):
        """Visit nodes recursively."""
        if node == None: 
            return

        # draw rectangular region with criss-crossed hashed lines 
        r = node.region
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), r.x_max, self.toTk(r.y_max))
         
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), r.x_max, self.toTk(node.origin[Y]),
                                dash=(2, 4)) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), node.origin[X], self.toTk(r.y_max),
                                dash=(2, 4))
         
        for circle in node.circles:
            markColor = 'black'
            if circle[MULTIPLE]: markColor = 'blue'
            if circle[HIT]: markColor = 'red'
            self.canvas.create_oval(circle[X] - circle[RADIUS], self.toTk(circle[Y]) - circle[RADIUS], 
                                 circle[X] + circle[RADIUS], self.toTk(circle[Y]) + circle[RADIUS], 
                                 fill=markColor)
        for n in node.children:
            self.visit(n)
            
    def updateLocations(self):
        """Move all circles, reconstruct QuadTree and repaint."""
        if not self.paused:
            self.master.after(frameDelay, self.updateLocations)

        if self.tree.root is None: return
        
        # Destroy tree each time and reinsert all circles
        nodes = self.tree.root.preorder()
        self.tree = QuadTree(Region(0,0,512,512))
        for n in nodes:
            if n.circles is None: 
                continue
            
            circles = list(n.circles)
            for idx in range(len(circles)):
                c = circles[idx]
                
                c[HIT] = max(0, c[HIT]-1)     # update hit status
                
                if c[X] - c[RADIUS] + c[DX] <= self.tree.region.x_min:
                    c[DX] = -c[DX]
                elif c[X] + c[RADIUS] + c[DX] >= self.tree.region.x_max:
                    c[DX] = -c[DX]
                else:
                    c[X] = c[X] + c[DX]
                    
                if c[Y] - c[RADIUS] + c[DY] <= self.tree.region.y_min:
                    c[DY] = -c[DY]
                elif c[Y] + c[RADIUS] + c[DY] >= self.tree.region.y_max:
                    c[DY] = -c[DY]
                else:
                    c[Y] = c[Y] + c[DY]
                    
                # Update hit status for all colliding circles
                for circ in self.tree.collide(c):
                    circ[HIT] = MaxHit
                    c[HIT] = MaxHit
                self.tree.add(c)
                
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)

if __name__ == '__main__':
    root = Tk()
    app = QuadTreeFixedApp(root)
    app.viz = VisualizationWindow(root, label=label)
    root.mainloop()
