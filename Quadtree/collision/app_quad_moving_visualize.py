"""
    Demonstration application for collision detection. Each shape
    added is a random circle.
    
    Left mouse adds circle.
    
    Assumes you have python-igraph and plotly installed. Assumes you have
    stored your API credentials locally to work.
    
"""

from tkinter import Tk, Canvas, ALL, Toplevel, Button
from tkinter.font import Font
import random

from quadtree.quad import QuadTree, RADIUS, MULTIPLE, NE, NW, SW, SE
from adk.region import Region, minValue, maxValue, X, Y

from collections import defaultdict

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

frameDelay = 40

# Parameters for size of random circles       
MaxRadius = 30
MinRadius = 10

def layoutDrawTree(tree):
    setupDrawTree(tree)
    addmodsDrawTree(tree)
    return tree

def setupDrawTree(tree, depth=0, nexts=None, offset=None):
    if nexts is None:  nexts  = defaultdict(lambda: 0)
    if offset is None: offset = defaultdict(lambda: 0)

    countChild = 0
    total = 0
    for quad in [NW, NE, SW, SE]:
        if tree.children[quad] is not None:
            countChild = countChild + 1
            setupDrawTree(tree.children[quad], depth+1, nexts, offset)
            total = total + tree.children[quad].x

    tree.y = depth
    
    if countChild == 0:
        place = nexts[depth]
        tree.x = place
    elif countChild == 1:
        place = tree.children[0].x - 1
    else:
        place = total / countChild

    offset[depth] = max(offset[depth], nexts[depth]-place)

    if len(tree.children):
        tree.x = place + offset[depth]

    nexts[depth] += 2
    tree.mod = offset[depth]

def addmodsDrawTree(tree, modsum=0):
    tree.x = tree.x + modsum
    modsum += tree.mod

    for quad in [NW, NE, SW, SE]:
        if tree.children[quad] is not None:
            addmodsDrawTree(tree.children[quad], modsum)            

# Layout inspired by https://llimllib.github.io/pymag-trees/
class DrawTree(object):
    def __init__(self, qtnode, depth=0):
        self.x = -1
        self.magx = 30
        self.magy = 80
        self.width = 30
        self.height = 30
        self.y = depth
        self.node = qtnode
        self.children = [None] * 4
        for quad in [NW, NE, SW, SE]:
            if qtnode.children[quad] is not None:
                self.children[quad] = DrawTree(qtnode.children[quad], depth+1)
        self.mod = 0

    def middle(self):
        """middle point"""
        return (self.x*self.magx + self.width/2,
                self.y*self.magy + self.height/2)

    def format(self, canvas, font):
        """add to canvas."""
        for quad in [NW, NE, SW, SE]:
            if self.children[quad] is not None:
                mid = self.middle()
                child = self.children[quad].middle()
                canvas.create_line(mid[0], mid[1], child[0], child[1])
                self.children[quad].format(canvas, font)

        colorToUse = 'white'
        if len(self.node.shapes) == 0:
            colorToUse = 'gray'
        canvas.create_rectangle(self.x*self.magx, self.y*self.magy,
                                self.x*self.magx+self.width, self.y*self.magy+self.height, fill=colorToUse);
        canvas.create_text(self.x*self.magx+self.width/2, self.y*self.magy + self.height/2,
                           font=font,
                           width=self.width, text=str(len(self.node.shapes)))


    def prettyPrint(self):
        """pp out the tree"""
        print (str(self.x) + "," + str(self.y) + " " + str(self.node.region))
        for quad in [NW, NE, SW, SE]:
            if self.children[quad] is not None:
                self.children[quad].prettyPrint()

class VisualizationWindow:
    def __init__(self, master):
        self.master = master
        self.frame = Toplevel(width=1024, height=512)

        self.canvas = Canvas(self.frame, width=1024, height=512)        

        self.frame.title("QuadTree Visualization")
        self.canvas.pack()
        self.font = None

    def plot(self, tree):
        """Given DrawTree information, plot the quadtree."""
        dt = DrawTree(tree)
        dt = layoutDrawTree(dt)
        self.canvas.delete(ALL)
        if self.font is None:
            self.font = Font(family='Times', size='24')
        dt.format(self.canvas, self.font)

class QuadTreeFixedApp:
    
    def __init__(self, master):
        """App for creating Quad tree dynamically with fixed circles that detect collisions."""
        
        master.title("Click to add fixed circles for QuadTree collision detection.") 
        self.master = master 
        self.paused = False
        
        # QuadTree holds the events
        self.tree = QuadTree(Region(0,0,512,512))
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-2>", self.pause)
        self.canvas.bind("<Button-3>", self.pause)
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
         
    def click(self, event):
        """Add circle to QuadTree with random radius and direction."""
        if self.paused:
            self.master.after(frameDelay, self.updateLocations)
            self.paused = False
        else:
            dx = random.randint(1,4)*(2*random.randint(0,1)-1)
            dy = random.randint(1,4)*(2*random.randint(0,1)-1)
            circle = [event.x, self.toCartesian(event.y), random.randint(4, MaxRadius), False, False, dx, dy]
        
            self.tree.add(circle)

    def pause(self, event):
        """Pause or Reset to start state (if already paused)."""
        if self.paused:
            self.tree = QuadTree(Region(0,0,512,512))
            self.canvas.delete(ALL)
            self.visit(self.tree.root)
        else:
            self.paused = True

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
            
        
    def updateLocations(self):
        """Move all shapes, reconstruct Quadtree and repaint."""
        if not self.paused:
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
                    
              
                # Suggestive of collision, but might miss outside node range.  
                # Update hit status for all colliding points
                for circ in self.tree.collide(s):
                    circ[HIT] = MaxHit
                    s[HIT] = MaxHit
                self.tree.add(s)
                
        self.canvas.delete(ALL)
        self.visit(self.tree.root)
        self.viz.plot(self.tree.root)

if __name__ == "__main__":
    root = Tk()
    app = QuadTreeFixedApp(root)
    app.viz = VisualizationWindow(root)
    root.mainloop()
