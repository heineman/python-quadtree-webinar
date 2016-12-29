"""
    Non-balanced Binary Search Tree.
    
    This class is not to be used in production code. Shown here to demonstrate the
    simple logic yet drastic inefficiencies when tree degenerates. 
    
    Find full details on balanced BSTs in "Algorithms in a Nutshell, 2ed", 
    http://shop.oreilly.com/product/0636920032885.do
"""

class BinaryNode:

    def __init__(self, value = None):
        """Create Binary Node."""
        self.value = value
        self.left = None
        self.right = None

    def add(self, val):
        """Add a new node to BST with this value."""
        pass

    def inorder(self):
        """In-order traversal of tree rooted at given node."""
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
        pass
            
    def __contains__(self, target):
        """Check whether BST contains target value."""
        pass

    def __iter__(self):
        """In order traversal of elements in the tree."""
        if self.root:
            return self.root.inorder()
                                
    