# -*- coding: utf-8 -*-

"""Main module."""


import sys
import networkx as nx
from types import GeneratorType
from networkx.algorithms import bfs_tree


tasks = []

# decorator
def task(obj, dep=None):
    def decorate(func):
        print(f"appending ({func.__name__},{obj},{dep}) to tasks")
        tasks.append((func, obj, dep))
        return func
    return decorate


def init():
    return nx.DiGraph()


def build_graph(G):
    for t, o, d in tasks:
        print("TASK: {}".format(t))
        G.add_node(t, o=o)

        if d is not None:
            for t1, o1, d1 in tasks:
                if t1 != t and d.__call__(o1):
                    print("EDGE: {} -> {}".format(t1.__name__, t.__name__))
                    G.add_edge(t1, t)

    # remove tasks with unresolved dependency
    for t, o, d in tasks:
        if d is not None and G.in_degree(t) == 0:
            G.remove_node(t)
            print(f"skipping task {t.__name__}")


def traverse_graph(G):
    root_nodes = [n for n in G.nodes if G.in_degree(n) == 0]

    if len(root_nodes) == 0:
        print("error: no root nodes found")
        sys.exit(1)

    for n in root_nodes:
        G.add_edge('start', n)

    tree = bfs_tree(G, 'start')

    tree.remove_node('start')
    G.remove_node('start')

    for n in tree:
        predecessors = list(G.predecessors(n))

        results = []

        if len(predecessors) == 0:
            results.append(n.__call__())
        else:
            for p in predecessors:
                print("NODE: {}; PRE: {}".format(n.__name__, p.__name__))

                for r in tree.nodes[p]['results']:
                    results.append(n.__call__(r))

        if all(isinstance(r, GeneratorType) for r in results):
            results = [r for gen in results for r in list(gen)]

        tree.nodes[n]['results'] = results

    return [r for n, data in tree.nodes.data() for r in data['results']]
