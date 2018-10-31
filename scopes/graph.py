import networkx as nx
from networkx.algorithms import bfs_tree

import sys

from scopes import utils
from .tasks import Spout

import pdb

G = nx.DiGraph()


def build(tasks):
    """ Build graph from a list of tasks. """


    for t in tasks:
        G.add_node(t)

    for t in tasks:
        deps_found = 0

        for d in tasks:
            if t is not d and t.is_dependency(d):
                G.add_edge(d, t)
                deps_found += 1

        if not isinstance(t, Spout) and deps_found == 0:
            print("could not find deps for non-spout")
            sys.exit(1)


def root_nodes():
    return [n for n in G.nodes if G.in_degree(n) == 0]


def topological_sort():
    """ Before we can sort we need a source node """

    for n in root_nodes():
        G.add_edge('start', n)

    tree = bfs_tree(G, 'start')

    """ Remove dummy source node """
    tree.remove_node('start')
    G.remove_node('start')

    return list(tree)


def traverse(nodes):
    """ Invoke each task func once with the results of its dependency task """
    for n in nodes:
        args = [r for p in G.predecessors(n) for r in p.results]
        # what happens when args is empty, and n is a non-spout?
        n.run(args)

    return {t.name: t.results for t in G.nodes}
