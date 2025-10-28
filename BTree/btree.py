import sys
import math

class BTreeNode:
    def __init__(self, t, isLeaf=False):
        self.t = t
        self.keys = [None] * (2 * self.t - 1)
        self.children = [None] * (2 * self.t)
        self.count = 0
        self.leaf = isLeaf

    '''
    Insertion
    '''
    def split(self, index):
        """
        Splits the full child at an index into two nodes and promotes the median key.
        """
        fullChild = self.children[index]
        newRightNode = BTreeNode(self.t, fullChild.leaf)

        # Median key to be promoted
        median = fullChild.keys[self.t - 1]

        # Move the upper half of keys from fullChild into newRightNode
        for i in range(self.t - 1):
            newRightNode.keys[i] = fullChild.keys[i + self.t]

        newRightNode.count = self.t - 1

        # Move the upper half of children (if not leaf)
        if not fullChild.leaf:
            for i in range(self.t):
                newRightNode.children[i] = fullChild.children[i + self.t]

        # Reduce the key count of the full child
        fullChild.count = self.t - 1

        # Shift children of current node to make room for newRightNode
        for i in range(self.count, index, -1):
            self.children[i + 1] = self.children[i]

        self.children[index + 1] = newRightNode

        # Shift keys of current node to make room for median
        for i in range(self.count - 1, index - 1, -1):
            self.keys[i + 1] = self.keys[i]

        # Place median in current node
        self.keys[index] = median
        self.count += 1

    def insertNotFull(self, key):
        """
        Inserts a key into a node that is not full.
        """
        i = self.count - 1

        if self.leaf:
            # Shift greater keys to the right to insert in sorted position
            while i >= 0 and key < self.keys[i]:
                self.keys[i + 1] = self.keys[i]
                i -= 1

            self.keys[i + 1] = key
            self.count += 1

        else:
            # Find child to descend into
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1

            # If the child is full, split first
            if self.children[i].count == 2 * self.t - 1:
                self.split(i)

                # After split, decide which of the two children we actually go into
                if key > self.keys[i]:
                    i += 1

            self.children[i].insertNotFull(key)

    '''
    Deletion
    '''

    def deleteKey(self, key):
        """
        Deletes the specified key from the subtree rooted at this node.
        """
        index = 0
        while index < self.count and self.keys[index] < key:
            index += 1

        # Case 1 / 2: key found in this node
        if index < self.count and self.keys[index] == key:
            if self.leaf:
                # Case 1: remove directly from leaf
                self.removeFromLeaf(index)
            else:
                # Case 2: remove from internal node
                self.removeInternalNode(index)

        else:
            # Key not in the current node
            if self.leaf:
                # Key doesn't exist in tree
                return

            # We are going to recurse into child 'index'
            # Make sure that child has at least t keys
            if self.children[index].count == self.t - 1:
                self.rebalance(index)

                # After rebalancing, if we merged using the left sibling,
                # 'index' may now be off by 1.
                if index > self.count:
                    index -= 1

            self.children[index].deleteKey(key)

    def removeFromLeaf(self, index):
        """
        Removes a key from a leaf node directly.
        """
        for i in range(index, self.count - 1):
            self.keys[i] = self.keys[i + 1]

        self.keys[self.count - 1] = None
        self.count -= 1

    def removeInternalNode(self, index):
        """
        Removes a key from an internal node by replacing it with a predecessor/successor.
        """
        key = self.keys[index]

        # Case 2a: left child has at least t keys
        if self.children[index].count >= self.t:
            predecessor = self.getInOrderPredecessor(index)
            self.keys[index] = predecessor
            self.children[index].deleteKey(predecessor)

        # Case 2b: right child has at least t keys
        elif self.children[index + 1].count >= self.t:
            successor = self.getInOrderSuccessor(index)
            self.keys[index] = successor
            self.children[index + 1].deleteKey(successor)

        # Case 2c: both children have t-1 keys -> merge them with this key
        else:
            self.merge(index)
            self.children[index].deleteKey(key)

    def getInOrderPredecessor(self, index):
        """
        Finds the in-order predecessor of a key at a given index.
        """
        current = self.children[index]
        while not current.leaf:
            current = current.children[current.count]

        return current.keys[current.count - 1]

    def getInOrderSuccessor(self, index):
        """
        Finds the in-order successor of a key at a given index.
        """
        current = self.children[index + 1]
        while not current.leaf:
            current = current.children[0]

        return current.keys[0]

    def merge(self, index):
        """
        Merges the child at index with its right sibling.
        Pulls down self.keys[index] in between them.
        """
        left = self.children[index]
        right = self.children[index + 1]

        # Move the separator key from parent down into left
        left.keys[self.t - 1] = self.keys[index]

        # Copy right's keys into left
        for i in range(right.count):
            left.keys[i + self.t] = right.keys[i]

        # Copy right's children if not leaf
        if not left.leaf:
            for i in range(right.count + 1):
                left.children[i + self.t] = right.children[i]

        # Shift keys and children in the parent left to fill the gap
        for i in range(index + 1, self.count):
            self.keys[i - 1] = self.keys[i]
            self.children[i] = self.children[i + 1]

        # Clear now-unused slots
        self.keys[self.count - 1] = None
        self.children[self.count] = None

        # Update counts
        left.count += right.count + 1
        self.count -= 1

    def borrowLeftSibling(self, index):
        """
        Borrows a key from the left sibling to balance the subtree.
        """
        child = self.children[index]
        left = self.children[index - 1]

        # Shift child's keys and children right by 1
        for i in range(child.count - 1, -1, -1):
            child.keys[i + 1] = child.keys[i]

        if not child.leaf:
            for i in range(child.count, -1, -1):
                child.children[i + 1] = child.children[i]

        # Bring parent's separator key down into child
        child.keys[0] = self.keys[index - 1]

        # If child is not leaf, move left's last child pointer over
        if not child.leaf:
            child.children[0] = left.children[left.count]

        # Move left's last key up into parent
        self.keys[index - 1] = left.keys[left.count - 1]

        # Cleanup left sibling
        left.keys[left.count - 1] = None
        left.children[left.count] = None

        # Update counts
        child.count += 1
        left.count -= 1

    def borrowRightSibling(self, index):
        """
        Borrows a key from the right sibling to balance the subtree.
        """
        child = self.children[index]
        right = self.children[index + 1]

        # Bring parent's separator key down into child's rightmost slot
        child.keys[child.count] = self.keys[index]

        # If child is not leaf, grab right's first child pointer
        if not child.leaf:
            child.children[child.count + 1] = right.children[0]

        # Move right's first key up into parent
        self.keys[index] = right.keys[0]

        # Shift right sibling's keys and children left by 1
        for i in range(1, right.count):
            right.keys[i - 1] = right.keys[i]

        if not right.leaf:
            for i in range(1, right.count + 1):
                right.children[i - 1] = right.children[i]

        # Cleanup right sibling's old last slot
        right.keys[right.count - 1] = None
        right.children[right.count] = None

        # Update counts
        child.count += 1
        right.count -= 1

    def rebalance(self, index):
        """
        Ensures that the child at index has at least t keys before deletion continues.
        """
        # Case 3a: can borrow from left sibling?
        if index != 0 and self.children[index - 1].count >= self.t:
            self.borrowLeftSibling(index)

        # Case 3a: can borrow from right sibling?
        elif index != self.count and self.children[index + 1].count >= self.t:
            self.borrowRightSibling(index)

        # Case 3b: need to merge
        else:
            # If index is not the last child, merge index with index+1
            if index != self.count:
                self.merge(index)
            else:
                # Otherwise merge index-1 with index, and update index
                self.merge(index - 1)

    '''
    Traversal
    '''
    def traverse(self):
        """
        Performs an in-order traversal and returns a list of all keys in the subtree.
        """
        result = []
        for i in range(self.count):
            if not self.leaf:
                result += self.children[i].traverse()
            result.append(self.keys[i])

        if not self.leaf:
            result += self.children[self.count].traverse()

        return result


class BTree:

    def __init__(self, t):
        self.root = None
        self.t = t

    def insert(self, key):
        if self.root is None:
            self.root = BTreeNode(self.t, True)
            self.root.keys[0] = key
            self.root.count = 1
        else:
            if self.root.count == 2 * self.t - 1:
                # Root is full -> grow tree height
                newNode = BTreeNode(self.t, False)
                newNode.children[0] = self.root
                newNode.split(0)

                # Pick correct child for insertion
                i = 0
                if newNode.keys[0] < key:
                    i += 1
                newNode.children[i].insertNotFull(key)

                self.root = newNode
            else:
                self.root.insertNotFull(key)

    def delete(self, key):
        if not self.root:
            return

        self.root.deleteKey(key)

        # Shrink height if root got empty
        if self.root.count == 0:
            if self.root.leaf:
                self.root = None
            else:
                self.root = self.root.children[0]

    def select(self, k):
        """
        Returns the k-th smallest key (1-indexed), or -1 if invalid.
        """
        if self.root is None:
            return -1
        result = self.root.traverse()
        return result[k - 1] if 1 <= k <= len(result) else -1

    def rank(self, key):
        """
        Returns the 1-indexed position of `key` in sorted order if it exists,
        otherwise -1.
        """
        if self.root is None:
            return -1
        result = self.root.traverse()
        if key in result:
            return result.index(key) + 1
        return -1

    def keysInRange(self, x, y):
        """
        Returns all keys k such that x <= k <= y in ascending order,
        or -1 if none.
        """
        if self.root is None:
            return -1
        result = [k for k in self.root.traverse() if x <= k <= y]
        return result if result else -1

    def isPrime(self, n):
        """
        Returns True if n is prime, else False.
        """
        n = int(n)
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        # trial division up to sqrt(n), skipping evens
        limit = int(math.sqrt(n)) + 1
        for i in range(3, limit, 2):
            if n % i == 0:
                return False
        return True

    def primesInRange(self, x, y):
        """
        Returns all prime keys k such that x <= k <= y,
        or -1 if none.
        """
        keys = self.keysInRange(x, y)
        if keys == -1:
            return -1
        primes = [k for k in keys if self.isPrime(k)]
        return primes if primes else -1


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python btree.py <t> <keystoinsert.txt> <keystodelete.txt> <commands.txt>")
        sys.exit(1)

    t = int(sys.argv[1])
    insert_file = sys.argv[2]
    delete_file = sys.argv[3]
    command_file = sys.argv[4]

    tree = BTree(t)

    # Insert all keys (as INT)
    with open(insert_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            key = int(line)
            tree.insert(key)

    # Delete all keys (as INT)
    with open(delete_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            key = int(line)
            tree.delete(key)

    # Process commands and write results
    with open(command_file, 'r') as cmd_file, open("btree_output.txt", 'w') as out_file:
        for line in cmd_file:
            parts = line.strip().split()
            if not parts:
                continue

            cmd = parts[0]

            if cmd == "select" and len(parts) == 2:
                k = int(parts[1])
                result = tree.select(k)
                out_file.write(f"{result}\n")

            elif cmd == "rank" and len(parts) == 2:
                x = int(parts[1])
                result = tree.rank(x)
                out_file.write(f"{result}\n")

            elif cmd == "keysInRange" and len(parts) == 3:
                x, y = int(parts[1]), int(parts[2])
                result = tree.keysInRange(x, y)
                if result == -1:
                    out_file.write("-1\n")
                else:
                    out_file.write(" ".join(map(str, result)) + "\n")

            elif cmd == "primesInRange" and len(parts) == 3:
                x, y = int(parts[1]), int(parts[2])
                result = tree.primesInRange(x, y)
                if result == -1:
                    out_file.write("-1\n")
                else:
                    out_file.write(" ".join(map(str, result)) + "\n")

#Run: py btree.py 2 keystoinsert.txt keystodelete.txt commands.txt

    
