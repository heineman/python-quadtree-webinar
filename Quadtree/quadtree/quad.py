"""
    Quadtree implementation.
    
    Every Quad Node has four children, partitioning space accordingly based on NE, NW, SW, SE quadrants.
    Each Node evenly divides quadrants and stores shapes that are wholly contained by its rectangular
    region. 
    
    Two or more identical shapes can exist
    
    Because the shapes are two-dimensional, they may intersect two (or more) of the subregions in the
    quadtree. Therefore, each shape is stored in the highest node in the tree whose associated 
    region fully encloses the shape.
    
    When the shapes are large, this means the resulting quadtree might be skewed with far too many shapes
    stored in upper nodes. 
   
"""

import math
from adk.region import Region, X, Y

# each point (X,Y,RADIUS) represents a circle.
RADIUS=2

# Not needed, but included for descriptive coloring in GUI
MULTIPLE=4

NE = 0
NW = 1
SW = 2
SE = 3

def distance(p, pt):
    """Compute distance from p to pt."""
    if pt:
        return ((p[X] - pt[X])**2 + (p[Y] - pt[Y])**2) ** 0.5

def smaller2k(n):
    """
    Returns power of 2 which is smaller than n. Handles negative numbers.
    """
    if n == 0: return 0
    if n < 0:
        return -2**math.ceil(math.log2(-n))
    else:
        return 2**math.floor(math.log2(n))
    
def larger2k(n):
    """
    Returns power of 2 which is larger than n. Handles negative numbers.
    """
    if n == 0: return 0
    if n < 0:
        return -2**math.floor(math.log2(-n))
    else:
        return 2**math.ceil(math.log2(n))

def completelyContains(region, circle):
    """Determine if region completely contains the given circle , closed on min and open on max."""
    if circle[X] - circle[RADIUS] <  region.x_max: return False
    if circle[X] + circle[RADIUS] >= region.x_max: return False
    if circle[Y] - circle[RADIUS] <  region.y_min: return False
    if circle[Y] + circle[RADIUS] >= region.y_max: return False

    return True

def intersectsCircle(region, circle):
    """Returns True if circle intersects region, based on geometry. Be careful of open-ended regions."""
    rectOrigin = [ (region.x_min + region.x_max)//2, (region.y_min + region.y_max)//2]
    halfSize = [ (region.x_max - region.x_min)//2, (region.y_max - region.y_min)//2]
    distCenter = [ abs(circle[X] - rectOrigin[X]), abs(circle[Y] - rectOrigin[Y])]
    
    if distCenter[X] > circle[RADIUS] + halfSize[X] or distCenter[Y] > circle[RADIUS] + halfSize[Y]:
        return False 
    if distCenter[X] <= halfSize[X] or distCenter[Y] <= halfSize[Y]:
        return True 
    
    corner = [ distCenter[X] - halfSize[X], distCenter[Y] - halfSize[Y]]
    
    return (corner[X] ** 2 + corner[Y] ** 2) <= circle[RADIUS] ** 2
    ## https://www.reddit.com/r/pygame/comments/2pxiha/rectanglar_circle_hit_detection/
    

def defaultCollision(c1, c2):
    """Two circles intersect if distance between centers is between the sum and the difference of radii."""
    centerDistance = (c1[X] - c2[X])**2 + (c1[Y] - c2[Y])**2
    sumSquared = (c1[RADIUS]+c2[RADIUS])**2
    if centerDistance > sumSquared: return False
    return True
    ###return (c1[RADIUS]-c2[RADIUS])**2 <= centerDistance <= sumSquared 
    

class QuadNode:
    
    def __init__(self, region):
        """Create QuadNode centered on origin of given region"""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None]*4
        self.shapes = []
    
    def collide (self, circle):
        """Yield points in leaf that intersect with circle."""
        
        # Circle must intersect
        if intersectsCircle (self.region, circle):
            # if we have shapes, must check them
            for s in self.shapes:
                if QuadTree.collision(s, circle):
                    yield s
            
            # If subquadrants, find quadrant(s) into which to check further (might be more than one)...
            if self.children[NE] == None: return
            
            for q in self.quadrants(circle):
                for s in self.children[q].collide(circle):
                    yield s
 
    def add (self, circle):
        """Add circle to the QuadNode."""
        node = self
        while node:
            # Not part of this region
            if not intersectsCircle (node.region, circle):
                return False
        
            # Not yet subdivided? Then add to shapes, subdividing once > 4
            if node.children[NE] == None:
                node.shapes.append(circle)
                if len(node.shapes) > 4:
                    node.subdivide()
                return True
            
            # Find quadrant(s) into which to add; if intersects two or more
            # then this node keeps it, otherwise we add to that child.
            quads = node.quadrants (circle)
            if len(quads) == 1:
                node = node.children[quads[0]]
            else:
                self.shapes.append(circle)
                return True
            
        return False

    def remove(self, shape):
        """Remove shape from QuadNode. Does not adjust structure. Return True if updated information."""
        if self.shapes != None:
            if shape in self.shapes:
                idx = self.shapes.index(shape)
                del self.shapes[idx]
                return True
            
        return False

    def subdivide(self):
        """Add four children nodes to node and reassign existing points."""
        region = self.region
        self.children[NE] = QuadNode(Region(self.origin[X], self.origin[Y], region.x_max,   region.y_max))
        self.children[NW] = QuadNode(Region(region.x_min,   self.origin[Y], self.origin[X], region.y_max))
        self.children[SW] = QuadNode(Region(region.x_min,   region.y_min,   self.origin[X], self.origin[Y]))
        self.children[SE] = QuadNode(Region(self.origin[X], region.y_min,   region.x_max,   self.origin[Y]))
        
        # go through shapes we completely contain and try to push to lowest children. If 
        # intersect 2 or more quadrants then we must keep.
        update = self.shapes
        self.shapes = []
        for circle in update:
            quads = self.quadrants(circle)
            
            # If circle intersects multiple quadrants, must break structure and
            # add to self, otherwise only add to that individual quadrant 
            if len(quads) == 1:
                self.children[quads[0]].add(circle)
                circle[MULTIPLE] = False
            else:
                self.shapes.append(circle)
                circle[MULTIPLE] = True 
    
    
    def quadrants(self, circle):
        """Determine quadrants in which point exists. Closed intervals on quadrants I (NE) and III (SW)."""
        quads = []
        if intersectsCircle(self.children[NE].region, circle): quads.append(NE)
        if intersectsCircle(self.children[NW].region, circle): quads.append(NW)
        if intersectsCircle(self.children[SW].region, circle): quads.append(SW)
        if intersectsCircle(self.children[SE].region, circle): quads.append(SE)
        return quads
    
    def quadrant(self, pt):
        """Determine quadrant in which point exists. Closed intervals on quadrants I (NE) and III (SW)."""
        if pt[X] >= self.origin[X]:
            if pt[Y] >= self.origin[Y]:
                return NE
            else:
                return SE
        else:
            if pt[Y] >= self.origin[Y]:
                return NW
            else:
                return SW
     
    def preorder(self):
        """Preorder traversal of tree rooted at given node."""
        yield self

        for node in self.children:
            if node:
                for n in node.preorder():
                    yield n

    def __str__(self):
        """toString representation."""
        return "[{} ({}): {},{},{},{}]".format(self.region, self.shapes, self.children[NE], self.children[NW], self.children[SW], self.children[SE])

class QuadTree:

    # define default collision which can be set. Affects all QuadTree objects
    collision = defaultCollision

    def __init__(self, region):
        """
        Create Quadtree defined over existing rectangular region. Assume that (0,0) is the center
        and half-length side of any square in quadtree is power of 2. If incoming region is too small, then
        this expands accordingly.    
        """
        self.root = None
        self.region = region.copy()
        
        xmin2k = smaller2k(self.region.x_min)
        ymin2k = smaller2k(self.region.y_min)
        xmax2k = larger2k(self.region.x_max)
        ymax2k = larger2k(self.region.y_max)
        
        self.region.x_min = self.region.y_min = min(xmin2k, ymin2k)
        self.region.x_max = self.region.y_max = max(xmax2k, ymax2k)
        
    def add(self, circle):
        """Add circle to Quadtree."""
        if self.root is None:
            self.root = QuadNode(self.region)
            self.root.add(circle)
            return True
        
        return self.root.add (circle)
    
    def collide(self, circle):
        """Return collisions to circle within Quadtree."""
        if self.root is None:
            return iter([])
        
        return self.root.collide (circle)
    
    def remove(self, circle):
        """Remove circle should it exist in Quadtree."""
        node = self.root
        while node:
            quads = node.quadrants (circle)
            if len(quads) == 1:
                node = node.children[quads[0]]
            else:
                for i in range(len(node.shapes)):
                    if node.shapes[i] == circle:
                        del node.shapes[i]
                        return True
    
        return False
    
    def __iter__(self):
        """Traversal of elements in the tree."""
        if self.root:
            for e in self.root.preorder():
                yield e
        