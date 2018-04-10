# -*- coding: utf-8 -*-
"""Implements route service placement strategies
"""

from __future__ import division
import random
import networkx as nx

from icarus.util import iround
from icarus.registry import register_route_service_placement

__all__ = ['edge_rs_placement', 'random_rs_placement']

def apply_rs_placement(placement, topology):
    """Apply a route service placement to a topology

    Parameters
    ----------
    placement : dict of sets
        Set of contents to be assigned to nodes keyed by node identifier
    topology : Topology
        The topology
    """
    for v, contents in placement.items():
        topology.node[v]['stack'][1]['route_service'] = contents

@register_route_service_placement('EDGE')
def edge_rs_placement(topology, contents, n_services, **kwargs):
    """Places route services at the edges of the network
    """
    edge_routers = topology.graph['edge_nodes']
    rs_placement = collections.defaultdict(set)
    n = 0
    for v in edge_routers:
        n += 1
        if n == n_services:
            break
        rs_placement[v] = set(contents)
    apply_rs_placement(rs_placement, topology)

@register_route_service_placement('RANDOM')
def random_rs_placement(topology, contents, n_services, seed=None, **kwargs):
    """Places route services randomly
    """
    routers = topology.graph['routers'] 
    random.seed(seed)
    rs_placement = collections.defaultdict(set)
    selected = set()
    n = 0
    r = 0
    while n < n_services:
        while r not in selected:
            r = random.choice(routers)
            selected.add(r)
        n += 1
        rs_placement[r] = set(contents)
    apply_rs_placement(rs_placement, topology)
