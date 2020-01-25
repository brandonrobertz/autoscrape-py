# -*- coding: UTF-8 -*-
import logging

import networkx as nx


logger = logging.getLogger('AUTOSCRAPE')


class Graph(object):
    def __init__(self):
        # store scrape graph
        self.graph = nx.DiGraph()
        # current node (css tag)
        self.current = None
        self.dbg("Initializing graph")

    def dbg(self, msg):
        # logger.debug("[GRAPH]%s", msg)
        pass

    def add_root_node(self, node, **kwargs):
        """
        Add an isolated node, make it the current node. This
        is for creating new subgraphs inside our graph. Does
        not add any edges.
        """
        self.dbg("Adding root node as current: %s" % node)
        self.graph.add_node(node, **kwargs)
        self.current = node

    def add_node(self, node, **kwargs):
        """
        Add a single node to the tree, with edges connecting
        to the current node.
        """
        self.dbg("Adding to current: %s, Node: %s, Meta: %s" % (
            self.current, node, kwargs))
        self.graph.add_node(node, **kwargs)
        self.graph.add_edge(self.current, node)

    def add_nodes(self, nodes):
        """
        Add a list of nodes to the current node in the graph.
        This handles adding the nodes and the edges.
        """
        self.dbg("Adding to current: %s, Nodes: %s" % (self.current, nodes))
        for node, meta in nodes:
            self.add_node(node, **meta)

    def add_meta_to_current(self, **meta):
        self.dbg("Adding meta to current: %s, Meta: %s" % (self.current, meta))
        self.graph.nodes[self.current].update(**meta)

    def add_action_to_current(self, action):
        self.dbg("Adding action to current node: %s, Action: %s" % (
            self.current, action))
        current_meta = self.graph.nodes[self.current]
        current_actions = current_meta.get("actions", [])
        current_actions.append(action)
        current_meta["actions"] = current_actions
        nx.set_node_attributes(self.graph, current_meta, name=self.current)

    def move_to_node(self, node):
        self.dbg("Moving to node: %s" % node)
        self.current = node

    def move_to_parent(self):
        self.dbg("Moving to parent from current: %s" % self.current)
        try:
            preds = self.graph.predecessors(self.current)
            [self.dbg("Parent: %s" % p) for p in preds]
            parent = self.graph.predecessors(self.current).__next__()
        except StopIteration:
            self.dbg("Stop iteration exception hit! Current: %s" % self.current)
            return
        self.move_to_node(parent)

    def save_graph(self, output_path):
        nx.write_gpickle(self.graph, output_path)
