"""
    Demonstration application for collision detection. Each shape added is a 
    circle with given (x,y) point, random radius, and an initial random
    velocity (dx,dy). Circles bounce around the interior of the window.
    
    Left mouse adds circle.
"""

import random
from tkinter import Tk, Canvas, ALL

from quadtree.quad import QuadTree, RADIUS, MULTIPLE
from adk.region import Region, minValue, maxValue, X, Y

frameDelay = 40

# additional attributes of circle tuple by index
HIT = 3
DX = 5
DY = 6

# With each passing frame, decrease by one to allow human-perception of collision
MaxHit = 3

# Parameters for size of random circles       
MaxRadius = 30
MinRadius = 10

class QuadTreeMovingApp:
    
    def __init__(self, master):
        """App for creating QuadTree with moving circles that detect collisions."""
        
        master.title("Left-click to add moving circles for collision detection. Right-click resets.") 
        self.master = master 
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0,512,512))
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-2>", self.reset)      # needed for Mac
        self.canvas.bind("<Button-3>", self.reset)      # This is PC
        self.master.after(frameDelay, self.updateLocations)
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
        """Add circle to QuadTree with random radius and moving direction."""
        dx = random.randint(1,4)*(2*random.randint(0,1)-1)
        dy = random.randint(1,4)*(2*random.randint(0,1)-1)
        circle = [event.x, self.toCartesian(event.y), 
                  random.randint(4, MaxRadius), False, False, dx, dy]
        self.tree.add(circle)
        
    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0,512,512))
        self.canvas.delete(ALL)

    def visit (self, node):
        """Visit node to paint properly."""
        if node == None: return

        # draw rectangular region and hashed cross-hairs
        r = node.region
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), r.x_max, self.toTk(r.y_max))
        
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), r.x_max, self.toTk(node.origin[Y]),
                                dash=(2, 4)) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), node.origin[X], self.toTk(r.y_max),
                                dash=(2, 4))
        
        # Draw each circle, colored appropriately
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
                    
              
                # Update hit status for all colliding points
                for circ in self.tree.collide(c):
                    circ[HIT] = MaxHit
                    c[HIT] = MaxHit
                self.tree.add(c)
                
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
      
if __name__ == '__main__':
    root = Tk()
    app = QuadTreeMovingApp(root)
    root.mainloop()