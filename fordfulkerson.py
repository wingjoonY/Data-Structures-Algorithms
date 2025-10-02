from typing import List, Tuple, TypeVar 
Vertex = TypeVar("Vertex")      
Edge = TypeVar("Edge")
from collections import deque
"""
_______________________________________________________________________________________________________________________________________________


QUESTION 1: Fast Backups

_______________________________________________________________________________________________________________________________________________
"""

class Edge:
    def __init__(self, start: int, destination: int, capacity: int):
        self.u = start
        self.v = destination
        self.capacity = capacity
        self.flow = 0
        self.backward_edge = None   
        self.forward_edge = None    

    def __str__(self) -> str:
        return f"({self.u},{self.v},cap={self.capacity},flow={self.flow})"


class Vertex:
    def __init__(self, id: int):
        self.id = id
        self.edges: List[Edge] = []
        self.discovered = False
        self.visited = False
        self.previous_vertex: "Vertex | None" = None
        self.previous_edge: "Edge | None" = None

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def discover_node(self):
        self.discovered = True

    def visit_node(self):
        self.visited = True

    def reset(self):
        self.discovered = False
        self.visited = False
        self.previous_vertex = None
        self.previous_edge = None

    def __str__(self) -> str:
        edges_str = ", ".join(str(edge) for edge in self.edges)
        return f"Vertex {self.id}, Edges: [{edges_str}]"


class Graph:
    def __init__(self, num_vertices: int):
        # IMPORTANT: num_vertices is the exact count. No multiplying here.
        self.data_centres = [Vertex(i) for i in range(num_vertices)]

    def add_edges(self, argv_edges: List[Tuple[int, int, int]]):
        for u, v, capacity in argv_edges:
            forward_edge = Edge(u, v, capacity)
            backward_edge = Edge(v, u, 0)
            forward_edge.backward_edge = backward_edge
            backward_edge.backward_edge = forward_edge
            self.data_centres[u].add_edge(forward_edge)
            self.data_centres[v].add_edge(backward_edge)

    def has_augmenting_path(self, source: int, sink: int) -> bool:
        self.reset()
        q = deque([self.data_centres[source]])
        self.data_centres[source].discover_node()

        while q:
            current_vertex = q.popleft()
            current_vertex.visit_node()

            if current_vertex.id == sink:
                return True

            for edge in current_vertex.edges:
                remaining_capacity = edge.capacity - edge.flow
                if remaining_capacity <= 0:
                    continue

                adjacent_vertex = self.data_centres[edge.v]
                if adjacent_vertex.visited or adjacent_vertex.discovered:
                    continue

                # discover and set predecessor info
                adjacent_vertex.discover_node()
                adjacent_vertex.previous_vertex = current_vertex
                adjacent_vertex.previous_edge = edge
                q.append(adjacent_vertex)

        return False

    def get_augmenting_path(self, source: int, sink: int):
        path = []
        current_vertex = self.data_centres[sink]
        while current_vertex.id != source:
            edge = current_vertex.previous_edge
            if edge is None:
                # no path
                return []
            path.append((edge, edge.backward_edge))
            current_vertex = current_vertex.previous_vertex
        path.reverse()
        return path

    def augment_flow(self, flow_path) -> int:
        bottleneck_capacity = min(edge.capacity - edge.flow for edge, _ in flow_path)
        for edge, backward_edge in flow_path:
            edge.flow += bottleneck_capacity
            backward_edge.flow -= bottleneck_capacity
        return bottleneck_capacity

    def reset(self):
        for vertex in self.data_centres:
            vertex.reset()


def ford_fulkerson(total_vertices, edges, origin, sink):
    residual_network = Graph(total_vertices)  # num vertices is exact
    residual_network.add_edges(edges)
    max_flow = 0
    while residual_network.has_augmenting_path(origin, sink):
        path = residual_network.get_augmenting_path(origin, sink)
        if not path:
            break
        max_flow += residual_network.augment_flow(path)
    return max_flow


def maxThroughput(connections, max_in, max_out, origin, targets) -> int:
    """
    Node-splitting per data centre i:
      - 3*i     : 'in'   node
      - 3*i + 1 : 'mid'  node
      - 3*i + 2 : 'out'  node
    Plus one super sink at index 3*N.

    Edges:
      in -> mid  capacity = max_in[i]
      mid -> out capacity = max_out[i]
      inter-DC connections routed from out(u) to in(v) (or in(u) to out(v))
      target out nodes to super sink
      source is origin's mid node
    """
def maxThroughput(connections, max_in, max_out, origin, targets):
    N = len(max_in)
    super_sink = 3 * N
    total_vertices = 3 * N + 1

    all_connections = []

    # 1) Always u.out -> v.in
    for u, v, capacity in connections:
        all_connections.append((3*u + 2, 3*v, capacity))

    # per-DC gates
    for i in range(N):
        all_connections.append((3*i, 3*i + 1, max_in[i]))     # in  -> mid
        all_connections.append((3*i + 1, 3*i + 2, max_out[i]))  # mid -> out

    # 2) targets: in(target) -> super sink
    for t in targets:
        all_connections.append((3*t, super_sink, max_in[t]))

    new_origin = 3 * origin + 1  # origin.mid
    return ford_fulkerson(total_vertices, all_connections, new_origin, super_sink)

if __name__ == "__main__":
    connections = [(9, 7, 386), (10, 22, 274), (2, 13, 285), (23, 17, 460), (7, 2, 500), (17, 10, 241), (0, 17, 187), (1, 5, 210), (4, 30, 168), (17, 28, 237), (20, 0, 156), (12, 6, 165), (13, 21, 302), (27, 1, 184), (15, 8, 189), (22, 11, 260), (22, 19, 99), (24, 12, 108), (11, 1, 493), (7, 17, 93), (19, 21, 374), (26, 5, 126), (23, 26, 296), (18, 7, 217), (32, 23, 483), (21, 24, 414), (6, 2, 491), (14, 27, 101), (7, 4, 314), (24, 28, 154), (11, 19, 408), (12, 8, 248), (11, 12, 433), (16, 15, 351), (8, 30, 429), (16, 23, 398), (9, 8, 334), (4, 27, 120), (29, 23, 159), (16, 12, 214), (30, 20, 472), (7, 23, 476), (20, 24, 92), (0, 16, 175), (17, 26, 419), (27, 11, 75), (22, 15, 92), (3, 0, 361), (8, 7, 112), (6, 32, 228), (18, 8, 396), (7, 24, 205), (18, 23, 458), (24, 22, 99), (4, 12, 335), (2, 20, 172), (22, 24, 79), (29, 2, 278), (18, 3, 173), (23, 15, 94), (5, 20, 500), (20, 26, 295), (18, 12, 313), (14, 25, 134), (13, 31, 298), (9, 16, 342), (31, 1, 367), (11, 29, 382), (29, 22, 203), (13, 6, 390), (31, 19, 134), (17, 1, 216), (21, 11, 470), (1, 23, 102), (28, 29, 142), (19, 22, 178), (9, 4, 473), (27, 30, 479), (0, 27, 196), (15, 13, 377), (4, 7, 489), (20, 16, 359), (27, 2, 444), (13, 4, 319), (6, 25, 347), (26, 23, 254), (8, 5, 422), (1, 32, 317), (4, 6, 382), (7, 32, 144), (9, 22, 145), (20, 11, 200), (27, 13, 367), (32, 6, 79), (26, 25, 153), (1, 0, 205), (11, 7, 422), (20, 32, 314), (8, 10, 466), (9, 31, 486), (5, 14, 420), (29, 25, 297), (20, 5, 162), (21, 23, 192), (0, 21, 169), (1, 17, 196), (9, 17, 297), (24, 0, 491), (2, 5, 240), (29, 7, 403), (6, 8, 413), (30, 24, 173), (25, 32, 278), (5, 7, 437)]
    maxIn = [523, 903, 696, 663, 624, 872, 713, 747, 828, 828, 560, 761, 889, 712, 500, 595, 561, 752, 540, 543, 581, 879, 918, 550, 520, 899, 925, 578, 660, 763, 873, 634, 605]
    maxOut = [501, 581, 708, 643, 746, 680, 685, 696, 682, 589, 743, 597, 527, 674, 563, 705, 556, 536, 762, 706, 720, 741, 576, 779, 545, 558, 640, 687, 719, 743, 712, 750, 679]
    origin = 16
    targets = [32, 22, 2, 26]
    
    question1 = maxThroughput(connections,maxIn,maxOut,origin,targets) # solution = 5
    print(question1)