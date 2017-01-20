"""
    Non-balanced Binary Search Tree.
    
    This class is not to be used in production code. Shown here to demonstrate
    the simple logic yet drastic inefficiencies when tree degenerates. 

    Find full details on balanced BSTs in "Algorithms in a Nutshell, 2ed" 
    http://shop.oreilly.com/product/0636920032885.do    
"""

class BinaryNode:

    def __init__(self, value = None):
        """Create Binary Node."""
        self.value = value
        self.left  = None
        self.right = None

    def add(self, val):
        """Add a new node to BST with this value."""
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

    def sameStartingLetter(self, letter):
        """Follow in-order template to yield words starting with given letter."""
        if self.left and self.value[0] >= letter[0]:
            for word in self.left.sameStartingLetter(letter):
                yield word

        # yield word if matches target letter
        if self.value[0] == letter[0]:
            yield self.value
            
        if self.right and self.value[0] <= letter[0]:
            for word in self.right.sameStartingLetter(letter):
                yield word    

    def inorder(self):
        """In-order traversal of tree rooted at given node."""
        if self.left:
            for node in self.left.inorder():
                yield node

        yield self.value

        if self.right:
            for node in self.right.inorder():
                yield node

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
        """In-order traversal of elements in the tree."""
        if self.root:
            return self.root.inorder()
                                
    def sameStartingLetter(self, letter):
        """Return iterator of words starting with same given letter."""
        if self.root:
            for word in self.root.sameStartingLetter(letter):
                yield word
                
    def findAnagrams(self, target):
        """Return iterator of words that are anagrams for given target word."""
        if self.root:
            target = ''.join(sorted(target))
            for word in self.root.inorder():
                if target == ''.join(sorted(word)):
                    yield word
