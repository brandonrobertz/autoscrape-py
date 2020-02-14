# -*- coding: UTF-8 -*-
import logging

try:
    import networkx as nx
except ModuleNotFoundError:
    pass


logger = logging.getLogger('AUTOSCRAPE')


class Graph(object):
    def __init__(self):
        try:
            self.graph = nx.DiGraph()
        except NameError:
            logger.debug(
                "NetworkX not installed. Not building crawl graph."
                " (Hint: pip install autoscrape[graph])"
            )
            self.graph = None
        # store scrape graph
        # current node (css tag)
        self.current = None

    def add_root_node(self, node, **kwargs):
        """
        Add an isolated node, make it the current node. This
        is for creating new subgraphs inside our graph. Does
        not add any edges.
        """
        if self.graph is None:
            return
        self.graph.add_node(node, **kwargs)
        self.current = node

    def add_node(self, node, **kwargs):
        """
        Add a single node to the tree, with edges connecting
        to the current node.
        """
        if self.graph is None:
            return
        self.graph.add_node(node, **kwargs)
        self.graph.add_edge(self.current, node)

    def add_nodes(self, nodes):
        """
        Add a list of nodes to the current node in the graph.
        This handles adding the nodes and the edges.
        """
        if self.graph is None:
            return
        for node, meta in nodes:
            self.add_node(node, **meta)

    def add_meta_to_current(self, **meta):
        if self.graph is None:
            return
        self.graph.nodes[self.current].update(**meta)

    def add_action_to_current(self, action):
        if self.graph is None:
            return
        current_meta = self.graph.nodes[self.current]
        current_actions = current_meta.get("actions", [])
        current_actions.append(action)
        current_meta["actions"] = current_actions
        nx.set_node_attributes(self.graph, current_meta, name=self.current)

    def move_to_node(self, node):
        if self.graph is None:
            return
        self.current = node

    def move_to_parent(self):
        if self.graph is None:
            return
        try:
            preds = self.graph.predecessors(self.current)
            parent = self.graph.predecessors(self.current).__next__()
        except StopIteration:
            return
        self.move_to_node(parent)

    def save_graph(self, output_path):
        if self.graph is None:
            return
        nx.write_gpickle(self.graph, output_path)
