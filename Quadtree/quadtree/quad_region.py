"""
    Quadtree implementation for storing points using integer-coordinate regions.
    
    Every Quad Node has four children, partitioning space accordingly based on NE, NW, SW, SE quadrants.
    Each Node evenly divides quadrants. Each node represents a square collection of points,
    evenly subdivided into four children nodes, until leaf nodes representing an individual point. 
    
    The Quadtree implements set-semantics. This means there are no duplicate (x, y) points in a quadtree.
    
    Actual point objects only exist within the leaf nodes.
    
    Note that this data structure is not suitable for collision detection of
    two-dimensional shapes. It offers an alternative approach for decomposing
    collection of points in two-dimensional region. This structure has been used
    for data compression of black/white pixel-based images, where a pixel is 
    either on (black) or off (white).
"""

import math
from adk.region import X, Y, Region

NE = 0
NW = 1
SW = 2
SE = 3

# status for a node.
FULL = 1
NEUTRAL = 0
DELETED = -1

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

def containsPoint(region, point):
    """Returns True if point contained in rectangle, closed on min and open on max."""
    if point[X] < region.x_min: return False
    if point[X] >= region.x_max: return False
    if point[Y] < region.y_min: return False
    if point[Y] >= region.y_max: return False
    
    return True

class QuadNode:
    """
    When a QuadNode has status set to DELETED then its parent can delete it at any time
    by replacing with None. The prune() operation cleans up recursively.
    """
    
    def __init__(self, region, status = NEUTRAL):
        """Create empty QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None] * 4
        self.status = status
       
    def isFull(self):
        """Determine if node is full."""
        return self.status == FULL
    
    def setFull(self):
        """Mark node as full."""
        self.status = FULL
    
    def isDeleted(self):
        """Determine if node is full."""
        return self.status == DELETED

    def setDeleted(self):
        """Mark node as deleted."""
        self.status = DELETED

    def setNeutral(self):
        """Mark node as neither Full nor Deleted."""
        self.status = NEUTRAL

    def isPoint(self):
        """Determine if associated region is a single point. Region is closed on min, open on max."""
        return self.region.x_min + 1 == self.region.x_max and self.region.y_min + 1 == self.region.y_max
    
    def add (self, pt):
        """Add pt to the QuadNode, creating and merging QuadNodes as needed."""
         
        # Find quadrant into which point is to be inserted and create if empty
        q = self.quadrant (pt)
        
        if self.children[q] == None:
            self.children[q] = QuadNode(self.computeQuadrant(q))
            if self.children[q].isPoint():
                self.children[q].setFull()
            else:
                self.children[q].add(pt)
        else:
            # If we cannot add point to child, we are done
            if not self.children[q].add(pt):
                return False  
            
        # At this point, we have added pt to one of node's children. Perhaps we are full?
        if self.childrenFull():
            self.setFull()
            self.children = [None] * 4   
        
        return True

    def remove(self, pt):
        """
        Remove pt from QuadNode. Eventually get to single point node or a full node that
        contains this point.
        """
        if self.isPoint():
            self.setDeleted()
            return True
        
        q = self.quadrant(pt)
        if self.isFull():
            self.subdivide()
            self.setNeutral()
            
            
        return self.children[q].remove(pt)
        
    def prune(self, pt):
        """Pt has been removed from one of our children. Clean up nodes marked deleted."""
        newRoot = self
        
        if self.isDeleted():
            newRoot = None
        else:
            q = self.quadrant (pt)
            self.children[q] = self.children[q].prune(pt)
            if self.childrenNull():
                newRoot = None
         
        return newRoot

    def childrenFull(self):
        """Determine if all children are full.""" 
        if self.children[NE] is None or not self.children[NE].isFull(): return False
        if self.children[NW] is None or not self.children[NW].isFull(): return False
        if self.children[SW] is None or not self.children[SW].isFull(): return False
        if self.children[SE] is None or not self.children[SE].isFull(): return False
        
        return True
    
    def childrenNull(self):
        """Determine if all children are None.""" 
        if self.children[NE] is not None: return False
        if self.children[NW] is not None: return False
        if self.children[SW] is not None: return False
        if self.children[SE] is not None: return False
        
        return True
    
    def computeQuadrant(self, q):
        """Return region associated with given quadrant."""
        region = self.region
        if q is NE:
            return Region(self.origin[X], self.origin[Y], region.x_max,   region.y_max)
        if q is NW:
            return Region(region.x_min,   self.origin[Y], self.origin[X], region.y_max)
        if q is SW:
            return Region(region.x_min,   region.y_min,   self.origin[X], self.origin[Y])
        if q is SE:
            return Region(self.origin[X], region.y_min,   region.x_max,   self.origin[Y])
        
    
    def subdivide(self):
        """Add four children nodes to node, and retain status of parent node."""
        region = self.region
        self.children[NE] = QuadNode(Region(self.origin[X], self.origin[Y], region.x_max,   region.y_max), self.status)
        self.children[NW] = QuadNode(Region(region.x_min,   self.origin[Y], self.origin[X], region.y_max), self.status)
        self.children[SW] = QuadNode(Region(region.x_min,   region.y_min,   self.origin[X], self.origin[Y]), self.status)
        self.children[SE] = QuadNode(Region(self.origin[X], region.y_min,   region.x_max,   self.origin[Y]), self.status)
    
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
        """Pre order traversal of tree rooted at given node."""
        yield self

        for node in self.children:
            if node:
                for n in node.preorder():
                    yield n

    def __str__(self):
        """toString representation."""
        return "[{} ({}): {},{},{},{}]".format(self.region, self.status, self.children[NE], self.children[NW], self.children[SW], self.children[SE])

class QuadTree:

    def __init__(self, region):
        """
        Create Quad Tree defined over existing rectangular region. Assume that (0,0) is the center
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
        
    def add(self, pt):
        """Add point to Quad Tree. Returns False if outside potential region or already exists."""
        # Doesn't belong in this region, leave now
        if not containsPoint (self.region, pt):
            return False
        
        if self.root is None:
            self.root = QuadNode(self.region)
            
        return self.root.add (pt)
    
    def remove(self, pt):
        """Remove pt should it exist in tree. With second traversal prunes deleted nodes."""
        if not containsPoint (self.region, pt):
            return False
        
        n = self.root
        if n.isFull():
            n.subdivide()
    
        if self.root.remove(pt):
            self.root = self.root.prune(pt)
            return True
        else:
            return False
    
    def __contains__(self, pt):
        """Check whether exact point appears in Quadtree."""
        if not containsPoint (self.region, pt):
            return False
        
        n = self.root
        while n:
            if n.isFull():
                return True

            q = n.quadrant(pt)
            if n.children[q] is None:
                return False
            else:
                n = n.children[q]
    
        return False
    
    def __iter__(self):
        """In order traversal of elements in the tree."""
        if self.root:
            for e in self.root.preorder():
                yield e
        