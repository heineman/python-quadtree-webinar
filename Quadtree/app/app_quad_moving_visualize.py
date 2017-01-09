"""
    Demonstration application for collision detection. Each shape
    added is a random circle.
    
    Left mouse adds circle.
    
    Creates movable circles by using a random (dx, dy) velocity with each circle
    that adjusts position every frameDelay milliseconds.
    
    Offers alternative to updating moving circles by taking advantage of ability
    in tk to move items previously drawn to a canvas.
    
"""
import random
from tkinter import Tk, Canvas, ALL

from adk.region import Region, minValue, maxValue, X, Y
from quadtree.quad import QuadTree
from quadtree.util import RADIUS, MULTIPLE, HIT, DX, DY, ID, LINE
from quadtree.visualize import VisualizationWindow

# Refresh every 40 milliseconds
frameDelay = 40

# Parameters for size of random circles       
MaxRadius = 30
MinRadius = 10

def label(node):
    """Return number of circles as integer to display in node."""
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
                      random.randint(4, MaxRadius), False, False, dx, dy, None]
            
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
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), r.x_max, self.toTk(r.y_max), tag=LINE)
         
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), r.x_max, self.toTk(node.origin[Y]),
                                dash=(2, 4), tag=LINE) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), node.origin[X], self.toTk(r.y_max),
                                dash=(2, 4), tag=LINE)
         
#         for circle in node.circles:
#             markColor = 'black'
#             if circle[MULTIPLE]: markColor = 'blue'
#             if circle[HIT]: markColor = 'red'
#             self.canvas.itemconfig(circle[ID], fill=markColor)
        for n in node.children:
            self.visit(n)
            
    def updateLocations(self):
        """Move all circles, reconstruct QuadTree and repaint."""
        if not self.paused:
            self.master.after(frameDelay, self.updateLocations)

        if self.tree.root is None: return
        
        # Destroy tree each time and reinsert all circles, taking care to reset 
        # collision status (HIT) and whether stored by interior node (MULTIPLE).
        nodes = self.tree.root.preorder()
        self.tree = QuadTree(Region(0,0,512,512))
        for n in nodes:
            for c in n.circles:
                c[HIT] = False
                c[MULTIPLE] = False
                
                dx = dy = 0
                if c[X] - c[RADIUS] + c[DX] <= self.tree.region.x_min:
                    c[DX] = -c[DX]
                elif c[X] + c[RADIUS] + c[DX] >= self.tree.region.x_max:
                    c[DX] = -c[DX]
                else:
                    c[X] = c[X] + c[DX]
                    dx = c[DX] 
                    
                if c[Y] - c[RADIUS] + c[DY] <= self.tree.region.y_min:
                    c[DY] = -c[DY]
                elif c[Y] + c[RADIUS] + c[DY] >= self.tree.region.y_max:
                    c[DY] = -c[DY]
                else:
                    c[Y] = c[Y] + c[DY]
                    dy = c[DY]
                    
                # Update hit status for all colliding circles, based on 
                # newly added circle.
                for circ in self.tree.collide(c):
                    circ[HIT] = True
                    self.canvas.itemconfig(circ[ID], fill='red')
                    c[HIT] = True
                    
                self.tree.add(c)
                
                # Update visual for circle, either creating anew or moving. Fill color
                # is based on whether colliding (RED) or stored in interior node (BLUE)
                markColor = 'black'
                if c[MULTIPLE]: markColor = 'blue'
                if c[HIT]: markColor = 'red'
                
                if c[ID] is None:
                    c[ID] = self.canvas.create_oval(c[X] - c[RADIUS], self.toTk(c[Y]) - c[RADIUS], 
                                 c[X] + c[RADIUS], self.toTk(c[Y]) + c[RADIUS],
                                 fill=markColor) 
                else:
                    # dy is Cartesian, but tk is opposite in y-direction 
                    self.canvas.move(c[ID], dx, -dy)
                    self.canvas.itemconfig(c[ID], fill=markColor)
                
        # recreate entire visualization by deleting lines and moving circles
        self.canvas.delete(LINE)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)

if __name__ == '__main__':
    root = Tk()
    app = QuadTreeFixedApp(root)
    app.viz = VisualizationWindow(root, label=label)
    root.mainloop()
