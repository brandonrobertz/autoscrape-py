# -*- coding: UTF-8 -*-
from collections import deque

import networkx as nx


class BFS(object):
    def __init__(self, root_node):
        # queue of remaining BFS nodes
        self.queue = deque()
        # store BFS scrape graph
        self.graph = nx.DiGraph()
        # current node (css tag)
        self.current = None

    def next(self):
        """
        Get the next CSS path node to interact with.
        """
        newcurrent = self.queue.popleft()
        self.current = newcurrent
        return newcurrent

    def add_root_node(self, node, **kwargs):
        """
        Add an isolated node, make it the current node. This
        is for creating new subgraphs inside our graph. Does
        not add any edges.
        """
        self.graph.add_node(node, **kwargs)
        self.current = node

    def add_node(self, node, **kwargs):
        """
        Add a single node to the tree, with edges connecting
        to the current node.
        """
        self.queue.append(node)
        self.graph.add_node(node, **kwargs)
        self.graph.add_edge(self.current, node)

    def add_nodes(self, nodes):
        """
        Add a list of nodes to the current node in the graph.
        This handles adding the nodes and the edges.
        """
        self.queue.extend(nodes)
        for node, meta in nodes:
            self.add_node(node, **meta)
