# -*- coding: utf-8 -*-
"""Implementations of all routing strategies"""
from __future__ import division
import random

import networkx as nx

from icarus.registry import register_strategy
from icarus.util import inheritdoc, multicast_tree, path_links
from icarus.scenarios.algorithms import extract_cluster_level_topology

from .base import Strategy

__all__ = [
        #'ScopedFlooding',
        #'StopAndWait',
        'ForwardToRS'
        ]
          
@register_strategy('FORWARD_TO_RS')
class ForwardToRS(Strategy):
    """This strategy forwards the Interest with RIB misses to the nearest 
    Routing Service (RS). 
    """

    @inheritdoc(Strategy)
    def __init__(self, view, controller):
        super(ForwardToRS, self).__init__(view, controller)

    @inheritdoc(Strategy)
    def process_event(self, time, receiver, content, log):
        source = self.view.content_source(content)
        self.controller.start_session(time, receiver, content, log)
        path = self.view.shortest_path(receiver, source)

        # Interest Forwarding
        router = path[1]
        if path[0] != receiver:
            print "Error: path[0]"
            router = path[0]
        self.controller.forward_request_hop(receiver, router)
        if self.controller.get_content(router):
            self.controller.forward_content_hop(router, receiver)
            self.controller.end_session()
        
        interest_path = [receiver, router]
        cache_hit = False
        locator_hit = False
        locator = self.controller.get_rsn(router)  #RSN get
        self.controller.put_rsn(router, source) #RSN put
        if locator is None:
            # Forward the packet to a route service
            closest_rs = self.view.closest_rs_source(content, router)
            path = self.view.shortest_path(router, closest_rs)
            for prev_node, curr_node in path_links(path):
                self.controller.forward_request_hop(prev_node, curr_node)
                interest_path.append(curr_node)
                if self.controller.get_content(curr_node):
                    cache_hit = True
                    break
                locator = self.controller.get_rsn(curr_node) #RSN get
                if locator is not None:
                    # Found a cached locator
                    locator_hit = True
                    break
            else:
                # Reached the routing service. Now forward the packet to the source.
                path = self.view.shortest_path(closest_rs, source)
                for prev_node, curr_node in path_links(path):
                    interest_path.append(curr_node)
                    self.controller.forward_request_hop(prev_node, curr_node)
                    if self.controller.get_content(curr_node):
                        cache_hit = True
                        break
            if locator_hit:
                path = self.view.shortest_path(interest_path[-1], source)
                for prev_node, curr_node in path_links(path):
                    interest_path.append(curr_node)
                    self.controller.forward_request_hop(prev_node, curr_node)
                    if self.controller.get_content(curr_node):
                        cache_hit = True
                        break
                    self.controller.put_rsn(curr_node, source) #RSN put
        elif locator == source:
            # Forward the packet towards the source
            path = self.view.shortest_path(router, source)
            for prev_node, curr_node in path_links(path):
                interest_path.append(curr_node)
                self.controller.forward_request_hop(prev_node, curr_node)
                if self.controller.get_content(curr_node):
                    cache_hit = True
                    break
                self.controller.put_rsn(curr_node, source) #RSN put
        else:
            print ("Error: Locator is: " + str(locator) + " and source is: " + str(source))
            raise ValueError('Incorrect locator is returned')

        # Data Forwarding
        curr_node = interest_path[-1]
        for prev_node, curr_node in path_links(reversed(interest_path)):
            self.controller.forward_content_hop(prev_node, curr_node)
            self.controller.put_content()

        self.controller.end_session()
