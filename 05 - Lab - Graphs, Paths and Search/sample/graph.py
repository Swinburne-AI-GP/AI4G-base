''' Edge, Node and SparseGraph classes to support navigation graphs and cost
based searches for path between points.

Created for COS30002 AI for Games, Lab,
by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without
permission.

'''

class Edge(object):
    '''A single weighted (has a cost) and directed (has direction) edge. '''
    def __init__(self, from_idx=-1, to_idx=-1, cost=0.0):
        self.from_idx = from_idx
        self.to_idx = to_idx
        self.cost = cost

class Node(object):
    '''Base Node type needed by a sparse graph. This is all that is needed
    to create a sparse graph which can then be searched.
    '''
    def __init__(self, idx=-1):
        self.idx = idx


class SparseGraph(object):
    '''A sparse graph (directed "digraph" or undirected) that contains Nodes.
    Each Node and Edge can be added to define a graph, or an adjacency list of
    lists (or tuple of tuples) can be used to specify the topology all at once.
    '''

    def __init__(self, digraph=True):
        self.nodes = {} # dictionary
        self.edgelist = {} # dictionary of dictionaries
        self.digraph = digraph
        self.next_node_idx = 0
        self.cost_h = None # heuristic cost function reference

    def is_empty(self):
        ''' Return True if graph contains no nodes '''
        return len(self.nodes) == 0

    def is_node(self, idx):
        ''' Returns True if a node with the given idx is in the graph '''
        return idx in self.nodes

    def is_edge(self, from_idx, to_idx):
        ''' Return True if edge exists '''
        if from_idx in self.edgelist:
            return to_idx in self.edgelist[from_idx]
        return False

    def get_node(self, idx):
        ''' Return the node that matches the given index (idx) value.'''
        return self.nodes[idx]

    def get_edge(self, from_idx, to_idx):
        ''' Return the edge that joins the two nodes specified as indexes.
        Returns None if there is no edge. '''
        if from_idx in self.edgelist:
            if to_idx in self.edgelist[from_idx]:
                return self.edgelist[from_idx][to_idx]
        return None

    def get_neighbours(self, node_idx):
        ''' Return a list of the linked nodes as idx (index) values. '''
        keys = list(self.edgelist[node_idx].keys())
        keys.sort() # in-place
        return keys

    def add_node(self, node):
        ''' Add new node and assign it the current next_node_idx. '''
        # It is possible to "jump" index values and leave gaps in the sequence.
        if node.idx < 0:
            node.idx = self.next_node_idx
        self.next_node_idx = node.idx + 1
        # Keep the node, prepare the edgelist for edges
        self.nodes[node.idx] = node
        self.edgelist[node.idx] = {}
        # It can be useful to return the node just added...
        return node

    def remove_node(self, idx):
        ''' remove this node, and any edges to/from other nodes '''
        del self.nodes[idx]
        if idx in self.edgelist:
            del self.edgelist[idx]
        for from_idx, list in self.edgelist.items():
            if idx in list:
                del self.edgelist[from_idx][idx]

    def add_edge(self, edge):
        ''' Adds edge to the graph. Ensures that the nodes are valid.
        If not a digraph then create back edge to match. '''

        assert (edge.from_idx in self.nodes and edge.to_idx in self.nodes), 'invalid node idx'
        self.edgelist[edge.from_idx][edge.to_idx] = edge

        if not self.digraph:
            opp = Edge(edge.to_idx, edge.from_idx, edge.cost)
            self.edgelist[opp.from_idx][opp.to_idx] = opp

    def remove_edge(self, from_idx, to_idx):
        ''' Remove edge. If not a digraph remove back edge also'''
        if from_idx in self.edgelist:
            if to_idx in self.edgelist[from_idx]:
                del self.edgelist[from_idx][to_idx]
        if not self.digraph:
            if to_idx in self.edgelist:
                if from_idx in self.edgelist[to_idx]:
                    del self.edgelist[to_idx][from_idx]

    def num_nodes(self):
        ''' return the number of nodes (active+inactive) '''
        return len(self.nodes)

    def num_edges(self):
        ''' return the total number of edges in the graph '''
        return sum([ len(el) for id, el in list(self.edgelist.items()) ])

    def clear(self):
        ''' clears the graph ready for new nodes and edges '''
        self.next_node_idx = 0
        self.nodes = {}
        self.edgelist = {}

    def path_cost(self, path):
        '''Return the cost of travelling on each node in the path list.'''
        result = 0
        for i,j in zip(path[:-1], path[1:]):
            result += self.get_edge(i, j).cost
        return result


    def summary(self):
        return 'n:%d e:%d (digraph:%d)' % (self.num_nodes(), self.num_edges(), self.digraph)

    def get_adj_list_str(self):
        ''' simple method to pretty-format (sorted) edges as an adjacency list '''
        result = []
        idxlist = list(self.edgelist.keys())
        idxlist.sort()
        for idx in idxlist:
            keys = list(self.edgelist[idx].keys())
            keys.sort()
            result.append('%d->%s' % (idx, keys))
        return '\n'.join(result)

    @classmethod
    def FromAdjacencyList(cls, adjlist, digraph=True, nodecls=Node):
        ''' Build a graph from nested adjacency list ( (0,2,5) ... (7,0) )
            Note: default zero indexed,
            Format: each tuple set of (from, to1, to2, to3...)'''
        g = SparseGraph(digraph)
        # must add all nodes before the edges
        for list in adjlist:
            g.add_node(nodecls(idx=list[0]))
        # add the edges now
        for list in adjlist:
            from_idx = list[0]
            for to_idx in list[1:]: #skip from index
                g.add_edge(Edge(from_idx, to_idx))
        return g


#==============================================================================
# If this file is run directly, it will test the basic Node, Edge and
# SparseGraph functionality, and print some results to screen. A nice and
# simple test process.

if __name__ == '__main__':
    # try a directed graph (with directed edges)
    g = SparseGraph(digraph=True)
    n1 = g.add_node(Node(idx=1))
    n2 = g.add_node(Node(idx=2))
    g.add_edge(Edge(n1.idx,n2.idx))
    print(g.summary(), g.is_empty())
    g.clear()
    print(g.summary(), g.is_empty())
    # try an undirected graph...
    g = SparseGraph(digraph=False)
    g.add_node(Node())
    g.add_node(Node())
    g.add_node(Node())
    g.add_edge(Edge(0,1))
    g.add_edge(Edge(1,2))
    g.add_edge(Edge(2,0))
    g.remove_node(0)
    print(g.summary(), g.is_edge(1,2), g.is_node(0), g.is_node(1))
    g.remove_edge(1, 2)
    print(g.summary(), g.is_edge(1,2))
    # sample graph from book
    adj_list = ((0,3,5),
                (1,3,4),
                (2,3),
                (3,0,1,2),
                (4,1,6),
                (5,0),
                (6,4))
    g = SparseGraph.FromAdjacencyList(adj_list, False)
    print(g.summary())
    print(g.get_adj_list_str())