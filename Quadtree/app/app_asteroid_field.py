"""
    Sample Game in which a triangular ship navigates amongst a collection of
    moving asteroids, trying to shoot and destroy all asteroids before 
    colliding with one of them. There are some quirks, but after all, this
    is just a fun demo of the application of collisions.
    
    Actions:
      A      -- rotate left
      D      -- rotate right
      L      -- engage thrust
      SPACE  -- fire
      
    Asteroids are randomly formed and move throughout the region; when an 
    edge is reached, an asteroid appears on the other edg (i.e., wraps around)
    
    Collision detection appears in four places:
       1. When initializing the field of play, must make sure randomly
          placed asteroids do not appear within region around ship (uses defaultCollision)
       2. When a bullet is fired, it divides an asteroid that it intersects with
       3. When the ship hits an asteroid, the game is over

"""
import random
from math import pi, sin, cos
from tkinter import Tk, Canvas

from adk.region import Region, minValue, maxValue, X, Y
from quadtree.quad import QuadTree
from quadtree.util import RADIUS, DX, DY, defaultCollision

# Refresh every 40 milliseconds
frameDelay = 40

# Parameters for size of random circles       
MaxRadius = 32

# Index into Ship
ANGLE = 3

# Reuse RADIUS attribute for LIFE
LIFE = RADIUS

# Constants for game
NumAsteroids = 4
NumBullets   = 6
BulletLife   = 30
ShipRadius   = 10
MaxVelocity  = 5
SHIP         = 'ship'
ASTEROID     = 'asteroid'
BULLET       = 'bullet'

# Game Status
NEUTRAL   = 0
WON       = 1
DESTROYED = 2
PLAYING   = 3

class AsteroidsApp:
    
    def __init__(self, master):
        """App for detect collisions between moving circles using QuadTree."""
        
        master.title('Asteroid playing field. Click to restart game.') 
        self.master = master 
        
        # QuadTree holds the events
        self.tree = None
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.start)
        
        master.bind("<Key>", self.action)
        master.bind("<KeyRelease>", self.clear)
        self.canvas.pack()
        self.ship = None
        self.bullets = []
        self.thrust = False
        self.status = NEUTRAL

    def init(self):
        """
        Initialize by placing a number of random asteroids and put ship in
        middle, facing up. Clear all asteroids around the ship
        """
        self.tree = QuadTree(Region(0,0,512,512))
        clearZone = [256, 256, MaxRadius*2]
        numAdded = 0
        while numAdded < NumAsteroids:
            dx = random.randint(1,4)*(2*random.randint(0,1)-1)
            dy = random.randint(1,4)*(2*random.randint(0,1)-1)
            circle = [random.randint(0,512), random.randint(0,512), MaxRadius, False, False, dx, dy, None]
            if not defaultCollision(clearZone, circle):
                self.tree.add(circle)
                numAdded += 1
        
        # place ship in center and clear bullets. [3] is orientation, [DX,DY] are velocity
        self.ship = [256, 256, ShipRadius, pi/2, None, 0, 0]
        self.bullets = []
        self.status = PLAYING
        self.visit(self.tree.root)
         
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
    
    def clear(self, key):
        """
        React to key up events by turning off thruster. Behaves differently on Mac
        than on PC.
        """
        if key.char == 'l':
            self.thrust = False
    
    def action(self, key):
        """
        Detect Thrust (L), Turn Right (D), Turn Left (A) and Fire (SPACE).
        """
        if self.ship is None:
            return
        
        if key.char == 'l':
            self.thrust = True
            newdy = self.ship[DY] + sin(self.ship[ANGLE])
            if abs(newdy) > MaxVelocity:
                return
            newdx = self.ship[DX] + cos(self.ship[ANGLE])
            if abs(newdx) > MaxVelocity:
                return
            
            self.ship[DX] = newdx
            self.ship[DY] = newdy
        elif key.char == 'd':
            self.ship[ANGLE] = self.ship[ANGLE] - pi/18
            if self.ship[ANGLE] < 0:
                self.ship[ANGLE] += 2*pi
        elif key.char == 'a':
            self.ship[ANGLE] = self.ship[ANGLE] + pi/18
            if self.ship[ANGLE] > 2*pi:
                self.ship[ANGLE] -= 2*pi
        elif key.char == ' ':
            # If we have more bullets, create a new one with our current orientation.
            if len(self.bullets) < NumBullets:
                angle = self.ship[ANGLE]
                dx = cos(angle)*ShipRadius
                dy = sin(angle)*ShipRadius
                self.bullets.append([self.ship[X], self.ship[Y], BulletLife, None, None, dx, dy])
        
    def updateBullets(self):
        """Update location of bullets, and remove those that have expired."""
        self.canvas.delete(BULLET)
        for idx in range(len(self.bullets)-1, -1, -1):
            b = self.bullets[idx]
            self.updateShape(b)
            b[LIFE] -= 1
            if b[LIFE] <= 0:
                del self.bullets[idx]
            else: 
                self.canvas.create_oval(b[X] - 2, self.toTk(b[Y] - 2),
                                    b[X] + 2, self.toTk(b[Y] + 2),
                                    fill='black', tag=BULLET)
                
    def updateShip(self):
        """Draw ship and orientation, and the exhaust thrust if in use."""
        self.canvas.delete(SHIP)
        self.updateShape(self.ship)
        x = self.ship[X]
        y = self.ship[Y] 
        
        angle = self.ship[ANGLE]
        size = 2*pi/3
        color = 'black'
        if self.status == DESTROYED: color = 'red'
        if self.status == WON: color = 'green'
        self.canvas.create_line(x + cos(angle)*ShipRadius, self.toTk(y + sin(angle)*ShipRadius),
                                x + cos(angle+size)*ShipRadius, self.toTk(y + sin(angle+size)*ShipRadius),
                                fill=color, tag=SHIP)
        self.canvas.create_line(x + cos(angle+size)*ShipRadius, self.toTk(y + sin(angle+size)*ShipRadius),
                                x, self.toTk(y),
                                fill=color, tag=SHIP)
        self.canvas.create_line(x + cos(angle-size)*ShipRadius, self.toTk(y + sin(angle-size)*ShipRadius),
                                x, self.toTk(y),
                                fill=color, tag=SHIP)
        self.canvas.create_line(x + cos(angle-size)*ShipRadius, self.toTk(y + sin(angle-size)*ShipRadius),
                                x + cos(angle)*ShipRadius, self.toTk(y + sin(angle)*ShipRadius),
                                fill=color, tag=SHIP)
        
        # On Mac, thrust won't appear because of difference in key released events.
        if self.thrust:
            self.canvas.create_oval(x - 2, self.toTk(y - 2),
                                x + 2, self.toTk(y + 2),
                                fill='black', tag=SHIP)
                
    def updateShape(self, shape):
        """Move a given shape based on velocity and move shapes through boundaries."""
        if shape[X] <= self.tree.region.x_min:
            shape[X] = self.tree.region.x_max + shape[DX]
        elif shape[X]  >= self.tree.region.x_max:
            shape[X] = self.tree.region.x_min + shape[DX]
        else:
            shape[X] = shape[X] + shape[DX]
            
        if shape[Y]  <= self.tree.region.y_min:
            shape[Y] = self.tree.region.y_max + shape[DY]
        elif shape[Y]  >= self.tree.region.y_max:
            shape[Y] = self.tree.region.y_min + shape[DY]
        else:
            shape[Y] = shape[Y] + shape[DY]

    def start(self, event):
        """Restart."""
        # If we have won or lost, need to re-register timed handler
        if not self.status == PLAYING:
            self.master.after(frameDelay, self.updateLocations)
        self.init()

    def visit(self, node):
        """Visit nodes recursively."""
        if node == None: 
            return

        # Draw each circle, colored appropriately
        for circle in node.circles:
            self.canvas.create_oval(circle[X] - circle[RADIUS], self.toTk(circle[Y]) - circle[RADIUS], 
                                 circle[X] + circle[RADIUS], self.toTk(circle[Y]) + circle[RADIUS],
                                 tag=ASTEROID)
                        
        for n in node.children:
            self.visit(n)
            
    def updateLocations(self):
        """Move all circles, reconstruct QuadTree and repaint."""
        if self.ship is None:
            self.init()
            
        # schedule next update if we are still playing
        if self.status == PLAYING:
            self.master.after(frameDelay, self.updateLocations)

        if self.tree.root is None:
            self.bullets = []
            self.status = WON
            self.canvas.delete(BULLET)
            self.updateShip()
            return

        # check if any bullet has hit an asteroid. If so, remove and add two
        for idx in range(len(self.bullets)-1, -1, -1):
            b = self.bullets[idx]
            for c in self.tree.collide(b):
                if b:
                    del self.bullets[idx]
                    b = None
                    self.tree.remove(c)
                    c[RADIUS] = c[RADIUS] // 2
                    if c[RADIUS] >= 8:
                        # perturb to avoid unique coordinates
                        c2 = [c[X]+c[DY], c[Y], c[RADIUS], False, False, c[DY], c[DX]]
                        c3 = [c[X]-c[DY], c[Y], c[RADIUS], False, False, -c[DY], c[DX]]
                        self.tree.add(c2)
                        self.tree.add(c3)
        
        # Destroy tree each time and reinsert all circles with new locations
        nodes = self.tree.root.preorder()
        self.tree = QuadTree(Region(0,0,512,512))
        for n in nodes:
            for c in n.circles:
                
                # Move from one side to the other, top and bottom
                self.updateShape(c)
                self.tree.add(c)

        # Update our location and the bullets                
        self.updateShip()
        self.updateBullets()      
         
        # Final check to see if any asteroid intersects our ship
        for c in self.tree.collide(self.ship):
            self.status = DESTROYED
        
        # Redraw all asteroids
        self.canvas.delete(ASTEROID)
        self.visit(self.tree.root)

if __name__ == '__main__':
    root = Tk()
    app = AsteroidsApp(root)
    root.mainloop()
