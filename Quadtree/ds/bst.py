"""
    Non-balanced Binary Search Tree.
    
    This class is not to be used in production code. Shown here to demonstrate the
    simple logic yet drastic inefficiencies when tree degenerates. 

    Find full details on balanced BSTs in "Algorithms in a Nutshell, 2ed", 
    http://shop.oreilly.com/product/0636920032885.do    
"""

class BinaryNode:

    def __init__(self, value = None):
        """Create Binary Node"""
        self.value = value
        self.left = None
        self.right = None

    def add(self, val):
        """Add a new node to BST with this value"""
        if val <= self.value:
            if self.left:
                self.left.add(val)
            else:
                self.left = BinaryNode(val)
        else:
            if self.right:
                self.right.add(val)
            else:
                self.right = BinaryNode(val)

    def sameStartingLetters (self, collection):
        """Follow inorder template to yield collection of words starting with same letter."""
        if self.left:
            for col in self.left.sameStartingLetters(collection):
                yield col

        # yield a copy of the collection and clear values
        if len(collection) != 0 and collection[0][0] != self.value[0]:
            yield collection[:]
            del collection[:]
            
        collection.append(self.value)
        
        if self.right:
            for col in self.right.sameStartingLetters(collection):
                yield col    

    def inorder(self):
        """In order traversal of tree rooted at given node."""
        if self.left:
            for n in self.left.inorder():
                yield n

        yield self.value

        if self.right:
            for n in self.right.inorder():
                yield n

class BinaryTree:

    def __init__(self):
        """Create empty BST."""
        self.root = None

    def add(self, value):
        """Insert value into proper location in BST."""
        if self.root is None:
            self.root = BinaryNode(value)
        else:
            self.root.add(value)
            
    def __contains__(self, target):
        """Check whether BST contains target value."""
        node = self.root
        while node:
            if target < node.value:
                node = node.left
            elif target > node.value:
                node = node.right
            else:
                return True
        return False

    def __iter__(self):
        """In order traversal of elements in the tree"""
        if self.root:
            return self.root.inorder()
                                
    def sameStartingLetters (self):
        """Return iterator of words starting with same letter."""
        if self.root:
            collection = []
            for col in self.root.sameStartingLetters(collection):
                yield col
                
            # Don't forget lingering collection when traversal completes
            if len(collection) > 0:
                yield collection                                           
