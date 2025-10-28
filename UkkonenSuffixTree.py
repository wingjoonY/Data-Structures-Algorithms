"""
FIT3155 Assignment 2   
Name: Yap Wing Joon
StudentID: 31862527
    
DL-distance ≤ 1 multiple pattern matching within a collection of texts using suffix tree
Ukkonen's Algorithm for suffix tree construction
"""

import sys


ALPHABET_SIZE = 127

class Node:
    
    def __init__(self, index: int = None, leaf: bool = False, link: "Node" = None):
        
        self.index = index # index of -1 means the root
        self.isLeaf = leaf
        self.edges = [None] * ALPHABET_SIZE 
        self.suffix_link = link
        self.suffix_index = None
        
    def add_edge(self, edge: "Edge", char: str):
        
        self.edges[ord(char)] = edge
        
    def search_edge(self, char: str):

        return self.edges[ord(char)]
    
    @property
    def removed_none_edges(self):
        
        return [edge for edge in self.edges if edge is not None]
    
    
    def __str__(self):
        return f"Node({self.index})"


class Edge:
    
    def __init__(self, start: int, end: int, origin: "Node", dest: "Node", text: str):
        
        # honestly did not need to implement an edge class but i was already to deep in to realize and i just rolled with it
        self.start_idx = start
        self.end_idx = end
        self.origin = origin
        self.destination = dest
        self.text = text 
      
    def split_edge(self, index:int, new_node: "Node", text: str):
        """
        Split the edge at an index to insert a new internal node
        Current edge's destination is updated to the new node
        """
        new_edge = Edge(
            self.start_idx + index,
            self.end_idx,
            new_node,
            self.destination,
            self.text
        )
        
        self.end_idx = self.start_idx + index - 1

        self.destination = new_node
        new_node.add_edge(new_edge, text[self.start_idx + index])
        
    @property
    def label(self):
        return self.text[self.start_idx : int(self.end_idx) + 1]  
    
    def __len__(self):
        return int(self.end_idx) - self.start_idx + 1
    
    def __str__(self):
        origin_str = f"Node({self.origin.index if self.origin else 'None'})"
        destination_str = f"Node({self.destination.index if self.destination else 'None'})"
        edge_str = f"Edge({self.start_idx}, {self.end_idx})[{self.label}]"
        
        return f"{origin_str} -- {edge_str} -> {destination_str}"

class GlobalEnd:
    
    def __init__(self):
        """
        GlobalEnd class since a global end attribute in the SuffixTree class does not update the end index in each edge dynamically.
        """
        self.end = -1
        
    def increment(self):
        self.end += 1
    
    def __str__(self):
        return "%d" % self.end
    
    def __int__(self):
        return self.end
       
       
       
class SuffixTree:
    
    def __init__(self, data: str):
        
        self.text: str = data
        self.root: Node | None = None
        self.active_node: Node | None = None
        self.active_length: int = 0
        self.active_edge: int = -1
        self.remainder: int = 0
        self.global_end = GlobalEnd() # for rapid leaf extension (trick 4)
        self.leaf_counter: int = 0
        self.build_suffix_tree()

        
    def traverse(self, edge: "Edge"):
        """
        Applies skip/count trick
        Updates the active point when the active length is greater or eq to the length of the given edge
        """
        if edge is not None and self.active_length >= len(edge):
            # update active point
            self.active_edge += len(edge) 
            self.active_length -= len(edge) 
            self.active_node = edge.destination
            
            return True
        return False
    

    def extend_suffix_tree(self, i: int):
        """
        Extend the suffix tree using the 3 Extension Rules
        """
        
        self.remainder += 1
        self.global_end.increment()
        last_internal_node: "Node" = None
        
        while self.remainder > 0:
            
            if self.active_length == 0:
      
                self.active_edge = i
                
            edge: "Edge" = self.active_node.search_edge(self.text[self.active_edge])

            # when inserting a new character in the string
            if edge is None: # Rule 2 (alt)
                
                self.leaf_counter += 1
                leaf_node = Node(self.leaf_counter, leaf= True)
                
                new_edge = Edge(i, self.global_end, self.active_node, leaf_node, self.text)

                self.active_node.add_edge(new_edge, self.text[i])

                self.remainder-= 1
                
                # if an internal node was created in the previous extension, link it to the current active node
                if last_internal_node is not None:
                    
                    last_internal_node.suffix_link = self.active_node
                    last_internal_node = None
        
            else:
                
                edge: "Edge" = self.active_node.search_edge(self.text[self.active_edge]) 

                if self.traverse(edge): # skip/count
                    continue
                
                # Rule 3: if current character already exist: no further action necessary
                # just increment active_length and break (showstopper)
                if self.text[edge.start_idx + self.active_length] == self.text[i]:
                    
                    self.active_length += 1 

                    # link internal node made from last extension to active node if its not the root
                    if last_internal_node is not None and self.active_node != self.root:
                        last_internal_node.suffix_link = self.active_node
                        last_internal_node = None

                    break # Showstopper
                
                # Rule 2: Split edge, create internal and leaf node
         
                internal_node = Node(link = self.root)

                edge.split_edge(self.active_length, internal_node, self.text)

                self.leaf_counter += 1
                leaf_node = Node(self.leaf_counter, leaf= True)
                leaf_edge = Edge(i, self.global_end, internal_node, leaf_node, self.text)

                edge.destination.add_edge(leaf_edge, self.text[i]) # can either use internal_node or like this
                
                self.remainder -= 1
                
                # follow suffix link
                if self.active_node != self.root:
                    self.active_node = self.active_node.suffix_link  
                
                
                elif self.active_node == self.root and self.active_length > 0:
                    self.active_length -= 1
                    self.active_edge += 1
                
                # link previous internal node to current one
                if last_internal_node is not None:
                    last_internal_node.suffix_link = internal_node
                
                last_internal_node = internal_node # update the last_internal_node for next extension
                        
                        
    def build_suffix_tree(self):
        """
        Construct the suffix tree in n phases
        
        """
        self.root = Node(index = -1, leaf = False)
        self.root.suffix_link = self.root
        self.active_node = self.root
        for i in range(len(self.text)):
            self.extend_suffix_tree(i)
        self.set_suffix_indices(self.root)

        
    def set_suffix_indices(self, node=None, label_length=0):
        """DFS for leaf nodes' indidces to represet their corresponding suffixes
        """
        if node is None:
            node = self.root

        if node.isLeaf:
            node.suffix_index = len(self.text) - label_length + 1
            return

        for edge in node.removed_none_edges:
            self.set_suffix_indices(edge.destination, label_length + len(edge))


    def exact_pattern_matching(self, pattern):
        
        matches = self.dfs_pattern_matching(self.root, pattern, 0)
        return matches

    def dfs_pattern_matching(self, node, pattern, index):
        """
        finds and collects all occurrences of the pattern in the suffix tree through recursive dfs
        """
        matches = []
        
        for edge in node.removed_none_edges:
            k = edge.start_idx
            i = index

            # traversing and comparing the edge label to pattern
            while k <= int(edge.end_idx) and i < len(pattern):
                if self.text[k] != pattern[i]:
                    break
                k += 1
                i += 1

            if i == len(pattern): # match found so we traverse down to all leafs to get all other occurrences of pattern
                
                matches += self.get_suffix_indices(edge.destination)

            elif k > int(edge.end_idx): # continue 
                matches += self.dfs_pattern_matching(edge.destination, pattern, i)

        return matches

    def get_suffix_indices(self, node):
        """
        traverse to the leaf nodes from the given node to get the suffix indices for pattern matching
        """
        suffix_indices = []
        if node.isLeaf:
            suffix_indices.append(node.suffix_index)
        else:
            for edge in node.removed_none_edges:
                suffix_indices += self.get_suffix_indices(edge.destination)
        return suffix_indices
    
    def print_tree_dfs(self, node=None):
        
        # for testing and debugging
        if node is None:
            node = self.root

        for edge in node.removed_none_edges:
            print("\n", edge, edge.destination.suffix_index)
            self.print_tree_dfs(edge.destination)


def read_config_file(config_filename):
    with open(config_filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    N = int(lines[0])
    text_filenames = [line.split()[1] for line in lines[1:N+1]]
    M = int(lines[N+1])
    pattern_filenames = [line.split()[1] for line in lines[N+2:N+2+M]]
    
    return text_filenames, pattern_filenames

def read_files(filenames):
    contents = []
    for filename in filenames:
        with open(filename, 'r') as f:
            text = f.read().replace('\n', '')
            contents.append(text)
    return contents

def main():

    config_filename = sys.argv[1]
    text_filenames, pattern_filenames = read_config_file(config_filename)
    
    texts = read_files(text_filenames)
    
    text_trees = [SuffixTree(text + '$') for text in texts]

    patterns = read_files(pattern_filenames)
    
    with open("output_a2.txt", "w") as output_file:
        for pattern_num, pattern in enumerate(patterns, start=1):
            for text_num, tree in enumerate(text_trees, start=1):

                positions = tree.exact_pattern_matching(pattern)
                
                for position in positions:
                    output_file.write(f"{pattern_num} {text_num} {position} 0 \n")

if __name__ == "__main__":
    main()


