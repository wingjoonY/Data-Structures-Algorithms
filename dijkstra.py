from typing import List, Tuple, TypeVar
Vertex = TypeVar("Vertex")
Edge = TypeVar("Edge")

class TreeMap:
    def __init__(self, roads: List[Tuple[int, int, int]], solulus: List[Tuple[int, int, int]]):
        """
        Function description:
        Constructor for TreeMap
        Creates a graph of size |T| * 2, creates and adds trees to the graph and connects all regular roads and solulu roads 
        correspondingly
        
        Approach description:
        First to obtain the number of trees, we find the maximum in roads between roads[i][0] and roads [i][1] and increase by 1 since 
        tree IDs start from 0. Create the tree graph with double the number of trees so that we can differentiate the Delulu Forest and 
        after the forest after the seal is undone. Next we create each Tree from range i...|T| * 2 and add the corresponding roads for 
        the Delulu Forest. For the roads in the unsealed forest, the tree IDs are the original tree IDs + the number of trees to again 
        differentiate the trees from the original graph. As for the Solulu Trees, we swap the time taken to claw the tree and the tree ID
        of the teleportation destination to allow creation of edges with the same 'add_roads' function. The tree ID of the TP destination
        is added with the number of trees so we are taken to the second graph once we use one of the Solulu trees.
        
        
        Input:
        roads - a list of tuples of three integers representing the start, destination and time taken for travel respectively
        solulus -  a list of tuples of three integers representing the start, time taken to claw a tree, and the destination of teleportation
        
        Output:
        No output lmao
        
        
        Time complexity: O(|T| + |R|)
        Aux space complexity: O(|T| + |R|)
        """
    # ToDo: Initialize the graph data structure here.
        self.roads = roads
        self.solulus = [None] * len(solulus) 
       
        self.trees_count = 0
        
        for i in range(len(roads)): #O(|R|)
            
            if self.trees_count < roads[i][0]:
                self.trees_count = roads[i][0]
            if self.trees_count < roads[i][1]:
                self.trees_count = roads[i][1]
                
        self.trees_count += 1
        
        self.trees = [None] * self.trees_count * 2
        for i in range(self.trees_count * 2): #O(|T|)
            
            self.trees[i] = Vertex(i)
        
        self.add_roads(self.roads)
        
        self.seal_undone_roads = [None] * len(self.roads)
        for i in range(len(self.seal_undone_roads)):
            
            self.seal_undone_roads[i] = (self.roads[i][0] + self.trees_count, self.roads[i][1] + self.trees_count, self.roads[i][2])
            
        self.add_roads(self.seal_undone_roads)
    
        # solulus: [(Start: 0, Time: 5, Dest: 1)]
        
        for i in range(len(self.solulus)):
            self.solulus[i] = (solulus[i][0], solulus[i][2] + self.trees_count, solulus[i][1])

        
        self.add_roads(self.solulus)
        
        

    def escape(self, start: int, exits: List[int]):
        """
        
        Function description:
        
        Uses Dijkstra to find the shortest path from start to one of the exits after traversing through a Solulu Tree
        
        Approach description:
        
        First set isExit attributes to True for all trees with an exit. Exits are only found on the second graph which acts like the forest
        when the seal is undone thus we have to add the number of trees to the Tree IDs of the exits. After doing so we run dijkstra on the
        double-sized graph which gives us the exit tree. The idea is that dijkstra will find the shortest path from start to all solulu 
        trees first which leads to the second graph which contains all the exits and eventually find the one of the exits when the isExit
        atrribute is true. After using dijkstra, we backtrack using the exit tree and start tree only if the exit we found is not None
        otherwise we return None. Backtracking is done by retracing all prior trees from the exit tree until we reach the starting tree. 
        We use the time attribute from exit tree accumulated from dijkstra to get our total_time and return the list resulting from the
        backtracking function and return both the total_time and route list.
        
        Input:
        start - integer representing the tree ID of where the bear starts its escape
        exits - a list of integers representing all exits in the forest
        
        Output:
        result - a tuple containing the total time taken during the escape and the route taken to escape
        OR
        None
        
        Time complexity: O(|T| + |R|)
        Aux space complexity: O(|T| + |R|)
        """
        
        for i in exits: #O(T)

            self.trees[i + self.trees_count].isExit = True
        
        exit_found = self.dijkstra(start) 
        if exit_found != None:
            total_time = exit_found.time
            optimal_route = self.dijkstra_backtracking(self.trees[start], exit_found)
            result = (total_time, optimal_route)
            self.reset()
            return result
        
        else:
            self.reset()
            return exit_found
        
    def dijkstra(self, source: int):
        """
        Function description:
        
        Dijkstra's algorithm using a Minimum Heap which finds the shortest path from the source to every other vertex until it finds the
        exit of the forest.
        Terminates when a tree with an exit is found
        
        Input:
        
        source - an integer representing where the bear starts its escape
        
        Output: 
        
        The vertex/ tree at which is an exit
        
        Time complexity: O(|R|log|T|)
        Space aux complexity: O(|T|), since MinHeap takes in |L| number of locations
        
        """
        
        start = self.trees[source]
        start.time = 0
    
        self.discovered = MinHeap(len(self.trees))
        self.discovered.insert(start)
   
        while self.discovered.length > 0:
            
            current_tree = self.discovered.serve()
        
            current_tree.visit_node()
         
            if current_tree.isExit == True:
                    
                return current_tree
            
            
            for edge in current_tree.edges:
                
                adj_tree = self.trees[edge.v]
            
                
                if adj_tree.visited == True:
                    
                    pass
                
                else:
                    
                    if adj_tree.discovered == False:
                        
                        adj_tree.time = current_tree.time + edge.w
                        adj_tree.previous = current_tree
                        adj_tree.discover_node()
                        self.discovered.insert(adj_tree)
                        
                    else:
                        
                        if adj_tree.time > current_tree.time + edge.w:
                            adj_tree.time = current_tree.time + edge.w
                            adj_tree.previous = current_tree
                            self.discovered.rise(self.discovered.array_index[adj_tree.id])
                            
                            
                            
    def dijkstra_backtracking(self, start: Vertex, end: Vertex):
        
        """
        Function descripton: 
            Backtracking to get the shortest route after reaching the destination vertex.
            Checking each vertex's previous starting from the destination vertex until the starting vertex is retrieved
            
        Input:
        
            start - starting vertex
            end - end vertex
            
        Output:
        
            A list of integers representing the optimal path
        
        Time complexity: O(V)
        Aux space complexity: O(V)
        
        """
        
        route = []
        current_tree = end
        while current_tree != start: # loop until we find the starting location
            
            current_location = current_tree.id
            
            # check if the tree id is on the second graph if so we need to subtract with the tree count to convert back to original tree id
            if current_tree.id >= self.trees_count:
                current_location -= self.trees_count

            if current_tree.previous.id == current_location:
                pass
            else:
                route.append(current_location)
                
            # sets current to its previous to keep tracing back each location previously visited to get the route
            current_tree = current_tree.previous
        
        # appending starting locaation
        route.append(current_tree.id)
        
        # route is originally in reverse order so:
        route.reverse() 
        return route 
                        
            
    
    def add_roads(self, roads: List[Tuple[int,int,int]]): 
        """
        Function description:
            Adds all edges to their respective trees in the graph
            
        Input:
            
            roads - a list of tuples containing the (starting vertex, ending vertex, time taken)
            
        Time complexity: O(|R|)
        Aux space complexity: O(1), constant time
            
        """
        for edge in roads:
            u = edge[0]
            v = edge[1]
            w = edge[2]
            

            current_edge = Edge(u,v,w)
            current_tree = self.trees[u]
            
            current_tree.add_edge(current_edge)
            
    def reset(self):
        
        for tree in self.trees:
            
            tree.discovered = False
            tree.visited = False
            tree.isExit = False
            tree.previous = False
        


class Vertex:
    def __init__(self, id) -> None:
        """
            Function description: 
            Constructor for Vertex class
            Has a list containing the egdes connecting it to other trees
            Has 3 boolean variables to check if the vertex has been discovered and visited and if the vertex is an exit
            Time for the time taken to reach this vertex
            Previous for the vertex prior before arriving to this vertex
        
        Input:
        
            id - number representing the vertex
        
            
        Time complexity: O(1), constant time
        """
        
        self.id = id
        self.edges = []
        self.visited = False
        self.discovered = False
        self.previous = None
        self.time = float("inf")
        self.isExit = False
        
        
    def add_edge(self, edge: Edge):
        """
        Function description: 
            To add an edge to list of edges of vertex
        
        Input:
        
            edge - an Edge object to be added to the edges list
        
            
        Time complexity: O(n), where n is the number of edges in the list if the list needs to be resized 
        """
        self.edges.append(edge)
        
    def discover_node(self):
        """
        Function description: 
            Sets discovered to true
            
        Time complexity: O(1)
        """
        self.discovered = True
    
    def visit_node(self):
        """
        Function description: 
            Sets visited to true
            
        Time complexity: O(1)
        """
        self.visited = True
    
        
    def __str__(self) -> str:
        """
        Function descripton: 
            String representation for Vertex
        
        Time complexity: O(n), where n is the number of edges
        """
        edge_string = ""
        for edge in self.edges:
            edge_string += str(edge)
            
        string = "Vertex {id}, Edges: {edges}".format(id = self.id, edges = edge_string)
        return string


class Edge:
    
    def __init__(self, source, dest, time):
        """
        Function description: 
            Constructor for Edge class
        
        Input:
            source - starting vertex of edge
            dest - ending vertex of edge
            time - time taken to get from start to dest
            
        Time complexity: O(1), constant time
        """
        self.u = source
        self.v = dest
        self.w = time
        
        
    def __str__(self) -> str:
        """
        Function descripton: 
            String representation for Edge
        
        Time complexity: O(1), constant time
        """
        string = "({start},{dest},{weight})".format(start = self.u,dest = self.v,weight = self.w)
        return string
        


class MinHeap():
    def __init__(self,size):
        """
        Constructor for MinHeap
        """
        self.array = [None] * (size + 1)
        self.array_index = [0] * (size + 1)
        self.length = 0 
    
    def insert(self, element: Vertex):
        """
        Add an element to MinHeap's array
        Time Complexity: O(log V), where V is the number of elements in the MinHeap
        """
        self.length += 1 
        self.array[self.length] = element
        self.array_index[element.id] = self.length
        self.rise(self.length)
    
    def serve(self):
        """
        Removes and returns the smallest number in the MinHeap's array
        Time Complexity: O(log V), where V is the number of elements in the MinHeap
        """
        self.swap(1, self.length)
        pop = self.array[self.length]
        self.length -= 1 
        self.sink(1)
        return pop

    def swap(self, x, y):
        """
        Swap two number's position in the minheap array
        Time Complexity: O(1)
        """
        self.array[x], self.array[y] = self.array[y], self.array[x]
        self.array_index[self.array[x].id], self.array_index[self.array[y].id] = self.array_index[self.array[y].id], self.array_index[self.array[x].id]
    
    def rise(self, element):
        """
        Adjusts the position of the element accordingly
        Time Complexity: O(log V), where V is the number of elements in the MinHeap
        """
        parent = element // 2 
        while parent >= 1:
            if self.array[parent].time > self.array[element].time:
                self.swap(parent, element)
                element = parent 
                parent = element // 2
            else:
                break
    
    def sink(self, element):
        """
        Adjusts the position of the element accordingly
        Time Complexity: O(log V), where V is the number of elements in the MinHeap
        """
        child = 2*element 
        while child <= self.length: 
            if child < self.length and self.array[child+1].time < self.array[child].time:
                child += 1 
            if self.array[element].time > self.array[child].time:
                self.swap(element, child)
                element = child 
                child = 2*element 
            else:
                break


# roads = [(0,1,4), (1,2,2), (2,3,3), (3,4,1), (1,5,2),
# (5,6,5), (6,3,2), (6,4,3), (1,7,4), (7,8,2),
# (8,7,2), (7,3,2), (8,0,11), (4,3,1), (4,8,10)]
# solulus = [(5,10,0), (6,1,6), (7,5,7), (0,5,2), (8,4,8)]

# myforest = TreeMap(roads, solulus)
# start = 1
# exits = [7, 2, 4]
# q2_result = myforest.escape(start,exits) # result = (9, [1, 7])