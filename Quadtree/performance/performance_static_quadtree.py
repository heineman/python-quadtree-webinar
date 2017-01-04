import random
import timeit

def performance():
    """Demonstrate execution performance."""
    n = 16
    numTrials = 10
    maxRadius = 10
     
    print ('n', 'Naive Time', 'Quadtree Time')
    while n <= 1024:
        naive_total = quadtree_total = 0
        
        circles = []
        targets = []
        for _ in range(n):
            circle = [random.randint(0,512), random.randint(0,512), random.randint(4, maxRadius), False, False, 0, 0]
            circles.append(circle)
            
        for _ in range(n):
            target = [random.randint(0,512), random.randint(0,512), random.randint(4, maxRadius), False, False, 0, 0]
            targets.append(target)
            
        # Construct circles as the initial set and a collection of target circles to be
        # used to check for intersections with the original set. 
        setup='''
from quadtree.quad import QuadTree
from adk.region import Region
targets = []
circles = []
'''
        for circle in circles:
            setup = setup + "\ncircles.append([%d,%d,%d,%d,False,False,0,0])" % (circle[0], circle[1], circle[2], circle[3])
        for target in targets:
            setup = setup + "\ntargets.append([%d,%d,%d,%d,False,False,0,0])" % (target[0], target[1], target[2], target[3])
        
        setup = setup + '''
qt = QuadTree(Region(0,0,512,512))
for s in circles:
    qt.add(s)
'''

        # Time naive O(m*n) algorithm for detecting collisions between m targets and n circles. 
        naive_total += min(timeit.Timer(
'''
from quadtree.quad import defaultCollision
collisions = []
for i in range(len(targets)):
    for j in range(len(circles)):
         if defaultCollision(targets[i], circles[j]):
             collisions.append([targets[i], circles[j]])
#print ("numCol:" + str(len(collisions)))''', setup=setup).repeat(5,numTrials))
           
        # Time algorithm using Quadtree of n circles against which m targets are checked.
        quadtree_total += min(timeit.Timer(
'''
from quadtree.quad import defaultCollision
collisions = []
for target in targets:
    for s in qt.collide(target):
        collisions.append([target, s])
#print ("numCol:" + str(len(collisions)))''', setup=setup).repeat(5,numTrials))
            
        print ("%d %5.4f %5.4f" % (n, 1000*naive_total/numTrials, 1000*quadtree_total/numTrials))
        n *= 2
        
if __name__ == '__main__':
    performance()

# Sample Run:
"""
n Naive Time Quadtree Time
16 0.6529 0.5322
32 1.6690 1.2049
64 6.6617 2.8688
128 26.5539 8.7543
256 106.1730 21.5697
512 430.5385 74.9178
1024 1710.8403 252.3014
"""