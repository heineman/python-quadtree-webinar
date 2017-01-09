"""
    Quadtree implementation.
    
    Every Quad Node has four children, partitioning space accordingly based on NE, NW, 
    SW, SE quadrants. Each Node evenly divides quadrants and stores circles that are 
    wholly contained by its rectangular region. 
    
    Two or more identical circles can exist.
    
    Because the circles are two-dimensional, they may intersect two (or more) of the 
    subregions in the quadtree. Therefore, each circle is stored in the highest node in 
    the tree whose associated region fully encloses the circle.
    
    When the circles are large, this means the resulting quadtree might be skewed with 
    far too many circles stored in upper nodes. 
   
"""

from adk.region import Region, X, Y
from quadtree.util import intersectsCircle, listContainsCircle, defaultCollision
from quadtree.util import NE, NW, SW, SE, MULTIPLE
from quadtree.util import smaller2k, larger2k

class QuadNode:
    
    def __init__(self, region):
        """Create QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None] * 4
        self.circles = []
    
    def collide(self, circle):
        """Yield circles that intersect with circle."""
        
        # Circle must intersect
        if intersectsCircle (self.region, circle):
            # if we have circles, must check them
            for c in self.circles:
                if QuadTree.collision(c, circle):
                    yield c
            
            # If subquadrants, find quadrant(s) into which to check further 
            if self.children[NE] == None: return
            
            for q in self.quadrants(circle):
                for c in self.children[q].collide(circle):
                    yield c
 
    def isLeaf(self):
        """Determine if QuadNode is a leaf node."""
        return self.children == [None] * 4
 
    def add(self, circle):
        """
        Add circle to the QuadNode, subdividing as needed. Returns True if
        not already in collection; False otherwise.
        """
        # Traverse to node whose enclosing region of circle is smallest in tree.
        node = self
        multiple = False
        while not node.isLeaf():
            # Find quadrant(s) into which to add; if intersects two or more
            # then this node keeps it, otherwise we add to that child.
            quads = node.quadrants (circle)
            if len(quads) == 1:
                node = node.children[quads[0]]
            else:
                multiple = True
                break

        # Either reach leaf node or interior node that must store circle. 
        # Check for uniqueness before adding. 
        if listContainsCircle(node.circles, circle):
            return False
         
        node.circles.append(circle) 
        if node.isLeaf() and len(node.circles) > 4:
            node.subdivide()
        elif multiple:
            circle[MULTIPLE] = True   
        return True

    def remove(self, circle):
        """Remove circle from QuadNode. Does not adjust structure. Return True if updated information."""
        if self.circles != None:
            if circle in self.circles:
                idx = self.circles.index(circle)
                del self.circles[idx]
                return True
            
        return False

    def subdivide(self):
        """Add four children nodes to node and reassign existing circles."""
        r = self.region
        self.children[NE] = QuadNode(Region(self.origin[X], self.origin[Y], r.x_max,        r.y_max))
        self.children[NW] = QuadNode(Region(r.x_min,        self.origin[Y], self.origin[X], r.y_max))
        self.children[SW] = QuadNode(Region(r.x_min,        r.y_min,        self.origin[X], self.origin[Y]))
        self.children[SE] = QuadNode(Region(self.origin[X], r.y_min,        r.x_max,        self.origin[Y]))
        
        # go through completely contained circles and try to push to lowest 
        # children. If intersect 2 or more quadrants then we must keep.
        update = self.circles
        self.circles = []
        for circle in update:
            quads = self.quadrants(circle)
            
            # If circle intersects multiple quadrants, must add to self, and mark
            # as MULTIPLE, otherwise only add to that individual quadrant 
            if len(quads) == 1:
                self.children[quads[0]].add(circle)
                circle[MULTIPLE] = False
            else:
                self.circles.append(circle)
                circle[MULTIPLE] = True 
    
    def quadrants(self, circle):
        """Determine quadrant(s) intersecting this circle."""
        quads = []
        if intersectsCircle(self.children[NE].region, circle): quads.append(NE)
        if intersectsCircle(self.children[NW].region, circle): quads.append(NW)
        if intersectsCircle(self.children[SW].region, circle): quads.append(SW)
        if intersectsCircle(self.children[SE].region, circle): quads.append(SE)
        return quads
    
    def quadrant(self, pt):
        """Determine quadrant in which point exists."""
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
        """Pre-order traversal of tree rooted at given node."""
        yield self

        for node in self.children:
            if node:
                for n in node.preorder():
                    yield n

    def __str__(self):
        """toString representation."""
        return "[{} ({}): {},{},{},{}]".format(self.region, self.circles, self.children[NE], self.children[NW], self.children[SW], self.children[SE])

class QuadTree:

    # define default collision which can be replaced. Affects all QuadTree objects
    collision = defaultCollision

    def __init__(self, region):
        """
        Create QuadTree defined over existing rectangular region. Assume that (0,0) is
        the lower left coordinate and the half-length side of any square in quadtree
        is power of 2. If incoming region is too small, this expands accordingly.    
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
        """Add circle to QuadTree."""
        # Return if not within our bounds
        if not intersectsCircle (self.region, circle):
            return False
        
        if self.root is None:
            self.root = QuadNode(self.region)
            self.root.add(circle)
            return True
        
        return self.root.add (circle)
    
    def collide(self, circle):
        """Return collisions to circle within QuadTree."""
        if self.root is None:
            return iter([])
        
        return self.root.collide (circle)
    
    def remove(self, circle):
        """Remove circle should it exist in QuadTree. Return True on success."""
        
        # Find largest node which wholly contains circle
        lastNode = None
        node = self.root
        while node:
            quads = node.quadrants (circle)
            if len(quads) == 1:
                lastNode = node
                node = node.children[quads[0]]
            else:
                lastNode = node
                break
                    
        # lastNode is the only node which could contain circle
        for idx in range(len(lastNode.circles)):
            if lastNode.circles[idx][0:3] == circle[0:3]:
                del lastNode.circles[idx]
                return True
        
        return False
    
    def __contains__(self, circle):
        """Check whether exact circle (x,y,r) appears in QuadTree."""
        if not intersectsCircle (self.region, circle):
            return False
        
        # Find largest node which wholly contains circle
        lastNode = None
        node = self.root
        while node:
            # If leaf node, done
            if node.isLeaf():
                lastNode = node
                break
             
            quads = node.quadrants (circle)
            if len(quads) == 1:
                lastNode = node
                node = node.children[quads[0]]
            else:
                lastNode = node
                break
                    
        # lastNode is the only node which could contain circle
        return listContainsCircle(lastNode.circles, circle)
    
    def __iter__(self):
        """Traverse and emit all circles in the QuadTree."""
        if self.root:
            for n in self.root.preorder():
                if n.circles:
                    for c in n.circles:
                        yield c
