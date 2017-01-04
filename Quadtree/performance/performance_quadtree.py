
import random
import timeit

# Uncomment the print ("numCol:" + str(len(collisions))) statements to confirm
# the number of collisions is the same

def performance():
    """Demonstrate execution performance."""
    n = 16
    numTrials = 10
    
    maxRadius = 10
     
    print ('n', 'Naive Time', 'Quadtree Time')
    while n <= 1024:
        naive_total = quadtree_total = 0
        
        circles = []
        for _ in range(n):
            circle = [random.randint(0,512), random.randint(0,512), random.randint(4, maxRadius), False, False, 0, 0]
            circles.append (circle)
            
        setup='''
from quadtree.quad import QuadTree
from adk.region import Region
circles = []'''
        for circle in circles:
            setup = setup + "\ncircles.append([%d,%d,%d,%d,False,False,0,0])" % (circle[0], circle[1], circle[2], circle[3])
        setup = setup + "\nqt = QuadTree(Region(0,0,512,512))"

        naive_total += min(timeit.Timer(
'''
from quadtree.quad import defaultCollision
collisions = []
for i in range(len(circles)):
    for j in range(i+1, len(circles)):
         if defaultCollision(circles[i], circles[j]):
             collisions.append([circles[i], circles[j]])
#print ("numCol:" + str(len(collisions)))
'''
                                        , setup=setup).repeat(5,numTrials))
           
        quadtree_total += min(timeit.Timer(
'''
from quadtree.quad import defaultCollision
collisions = []
qt = QuadTree(Region(0,0,512,512))

for circle in circles:
    for s in qt.collide(circle):
        collisions.append([circle, s])
    qt.add(circle)
#print ("numCol:" + str(len(collisions)))
'''
                                        , setup=setup).repeat(5,numTrials))
            
        print ("%d %5.4f %5.4f" % (n, 1000*naive_total/numTrials, 1000*quadtree_total/numTrials))

        n *= 2

if __name__ == '__main__':
    performance()
        
# Sample Run:
"""
n Naive Time QuadTree Time
16 0.4351 0.6823
32 0.8187 1.6945
64 3.2826 4.2492
128 13.0492 11.6634
256 52.5854 34.9976
512 212.1106 119.8405
1024 852.0942 462.7938
"""