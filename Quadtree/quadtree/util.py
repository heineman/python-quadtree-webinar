"""
Utility functions for quadtrees.
"""
import math
from adk.region import X, Y

# Attributes for Circle
# 0 (X) is its x-coordinate
# 1 (Y) is its y-coordinate
# 2 (RADIUS) is its radius
# 3 (HIT) records whether involved in a collision
# 4 (MULTIPLE) records whether circle is too big to fit in leaf node in quadtree
# 5 (DX) records velocity in x-axis for moving shape
# 6 (DY) records velocity in y-axis for moving shape
# 7 (ID) records canvas ID once circle has been drawn (defaults to None if not drawn).
RADIUS   = 2 
HIT      = 3 
MULTIPLE = 4
DX       = 5
DY       = 6
ID       = 7

# Each node can be subdivided into four quadrants.
NE = 0
NW = 1
SW = 2
SE = 3

# Associated tags for canvas items: LINES for quadtree structure, CIRCLES for circles
LINE='line'


def distance(p, pt):
    """Compute distance from p to pt."""
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

def containsPoint(region, point):
    """Returns True if point contained in region, closed on min and open on max."""
    if point[X] <  region.x_min: return False
    if point[X] >= region.x_max: return False
    if point[Y] <  region.y_min: return False
    if point[Y] >= region.y_max: return False
    
    return True

def completelyContains(region, circle):
    """Determine if region completely contains circle, closed on min, open on max."""
    if circle[X] - circle[RADIUS] <  region.x_max: return False
    if circle[X] + circle[RADIUS] >= region.x_max: return False
    if circle[Y] - circle[RADIUS] <  region.y_min: return False
    if circle[Y] + circle[RADIUS] >= region.y_max: return False

    return True

def listContainsCircle(collection, circle):
    """
    Check if (x,y,radius) of circle already in collection.
    Ignores other attributes (MULTIPLE and HIT in particular).
    """
    if collection is None:
        return False
    
    c = circle[0:3]
    for idx in range(len(collection)):
        if collection[idx][0:3] == c:
            return True
    return False

def deleteIfExists(collection, circle):
    """
    Remove (x,y,radius) circle from collection if it already exists and return True.
    If not in collection, returns False. Ignores other circle attributes. 
    """
    if collection is None:
        return False
    
    for idx in range(len(collection.circles)):
        if collection.circles[idx][0:3] == circle[0:3]:
            del collection.circles[idx]
            return True
    
    return False

def intersectsCircle(region, circle):
    """Returns True if circle intersects region, based on geometry. Be careful of open-ended regions."""
    rectOrigin = [(region.x_min + region.x_max)//2, (region.y_min + region.y_max)//2]
    halfSize   = [(region.x_max - region.x_min)//2, (region.y_max - region.y_min)//2]
    distCenter = [abs(circle[X] - rectOrigin[X]), abs(circle[Y] - rectOrigin[Y])]
    
    if distCenter[X] > circle[RADIUS] + halfSize[X] or distCenter[Y] > circle[RADIUS] + halfSize[Y]:
        return False 
    if distCenter[X] <= halfSize[X] or distCenter[Y] <= halfSize[Y]:
        return True 
    
    corner = [distCenter[X] - halfSize[X], distCenter[Y] - halfSize[Y]]
    
    return (corner[X] ** 2 + corner[Y] ** 2) <= circle[RADIUS] ** 2
    # http://www.reddit.com/r/pygame/comments/2pxiha/rectanglar_circle_hit_detection

def defaultCollision(c1, c2):
    """
    Two circles intersect if distance between centers is between the sum and the 
    difference of radii.
    """
    centerDistance = (c1[X] - c2[X])**2 + (c1[Y] - c2[Y])**2
    sumSquared = (c1[RADIUS]+c2[RADIUS])**2
    if centerDistance > sumSquared: return False
    return True
    