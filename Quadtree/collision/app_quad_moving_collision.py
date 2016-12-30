"""
    Demonstration application for collision detection. Each shape added is a random circle.
    
    Left mouse adds circle.
    
    Shows no collisions between 'neighboring' nodes in different siblings. Check this by clicking mouse
    on the vertical edge of a region, and then moving just one pixel to the left and clicking. It won't be 
    red. Similarly, do this in a region that has yet to be subdivided and "eyeball" where that point is,
    then click one pixel to the left and the collision will be detected;
    
"""

from tkinter import Tk, Canvas, ALL
import random

from quadtree.quad import QuadTree, RADIUS, MULTIPLE
from adk.region import Region, minValue, maxValue, X, Y

frameDelay = 40

# attributes of circle by position
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
        """App for creating Quad tree dynamically with fixed circles that detect collisions."""
        
        self.tree = QuadTree(Region(0,0,512,512))
        
        master.title("Click to add moving circles for QuadTree collision detection.") 
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
        """Convert tkinter point into Cartesian"""
        return self.canvas.winfo_height() - y

    def toTk(self,y):
        """Convert Cartesian into tkinter point."""
        if y == maxValue: return 0
        tk_y = self.canvas.winfo_height()
        if y != minValue:
            tk_y -= y
        return tk_y
         
    def click(self, event):
        """Add circle to QuadTree with random radius and direction."""
        dx = random.randint(1,4)*(2*random.randint(0,1)-1)
        dy = random.randint(1,4)*(2*random.randint(0,1)-1)
        circle = [event.x, self.toCartesian(event.y), random.randint(4, MaxRadius), False, False, dx, dy]
        self.tree.add(circle)
        
    def reset(self, event):
        """Reset to start state."""
        self.tree = QuadTree(Region(0,0,512,512))
        self.canvas.delete(ALL)

    def visit (self, node):
        """ Visit node to paint properly."""
        if node == None: return

        # draw rectangular region and hashed cross-hairs
        r = node.region
        self.canvas.create_rectangle(r.x_min, self.toTk(r.y_min), r.x_max, self.toTk(r.y_max))
        
        self.canvas.create_line(r.x_min, self.toTk(node.origin[Y]), r.x_max, self.toTk(node.origin[Y]),
                                fill='black', dash=(2, 4)) 
        self.canvas.create_line(node.origin[X], self.toTk(r.y_min), node.origin[X], self.toTk(r.y_max),
                                fill='black', dash=(2, 4))
        
        # Draw each shape, colored appropriately
        for shape in node.shapes:
            markColor = 'Black'
            if shape[MULTIPLE]: markColor = 'Blue'
            if shape[HIT]: markColor = 'Red'
            self.canvas.create_oval(shape[X] - shape[RADIUS], self.toTk(shape[Y]) - shape[RADIUS], 
                                 shape[X] + shape[RADIUS], self.toTk(shape[Y]) + shape[RADIUS], 
                                 fill=markColor)
            
        for n in node.children:
            self.visit(n)
        
    def updateLocations(self):
        """Move all shapes, reconstruct Quadtree and repaint."""
        self.master.after(frameDelay, self.updateLocations)

        if self.tree.root is None: return
        
        # Destroy tree each time and reinsert all shapes
        nodes = self.tree.root.preorder()
        self.tree = QuadTree(Region(0,0,512,512))
        for n in nodes:
            if n.shapes is None: 
                continue
            
            shapes = list(n.shapes)
            for idx in range(len(shapes)):
                s = shapes[idx]
                
                s[HIT] = max(0, s[HIT]-1)     # update hit status
                
                if s[X] - s[RADIUS] + s[DX] <= self.tree.region.x_min:
                    s[DX] = -s[DX]
                elif s[X] + s[RADIUS] + s[DX] >= self.tree.region.x_max:
                    s[DX] = -s[DX]
                else:
                    s[X] = s[X] + s[DX]
                    
                if s[Y] - s[RADIUS] + s[DY] <= self.tree.region.y_min:
                    s[DY] = -s[DY]
                elif s[Y] + s[RADIUS] + s[DY] >= self.tree.region.y_max:
                    s[DY] = -s[DY]
                else:
                    s[Y] = s[Y] + s[DY]
                    
              
                # Update hit status for all colliding points
                for circ in self.tree.collide(s):
                    circ[HIT] = MaxHit
                    s[HIT] = MaxHit
                self.tree.add(s)
                
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
      
if __name__ == "__main__":
    root = Tk()
    app = QuadTreeMovingApp(root)
    root.mainloop()