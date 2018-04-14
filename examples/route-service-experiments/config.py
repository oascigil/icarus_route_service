"""This module contains all configuration information used to run simulations
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = 2 #cpu_count()/2 #1

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
DATA_COLLECTORS = ['CACHE_HIT_RATIO', 'LATENCY', 'LINK_LOAD', 'PATH_STRETCH']

# Alpha determines content selection (Zipf parameter)
ALPHA = 0.7

# Default experiment parameters
CACHE_POLICY = 'LRU'

# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 3*10**5

# Number of content objects
N_CONTENTS = 3*10**5

# Total size of network cache as a fraction of content population
NETWORK_CACHE = 0.3

# Number of requests per second (over the whole network)
NETWORK_REQUEST_RATE = 100.0

# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 3*10**5

# Number of content requests generated after the warmup and logged
# to generate results. 
N_MEASURED_REQUESTS = 6*10**5

# List of all implemented topologies
# Topology implementations are located in ./icarus/scenarios/topology.py
TOPO_NAME = 'ROCKET_FUEL'

# Queue of experiments
EXPERIMENT_QUEUE = deque()
default = Tree()
default['workload'] = {'name':       'TRANSIT_LOCAL',
                       'n_contents': N_CONTENTS,
                       'n_warmup':   N_WARMUP_REQUESTS,
                       'n_measured': N_MEASURED_REQUESTS,
                       'rate':       NETWORK_REQUEST_RATE,
                       'transit':    0.7,
                       'local':      0.1,
                       'ingress':    0.1,
                       'egress':     0.1,
                       'alpha' :     ALPHA
                       }
#default['cache_placement']['name'] = 'UNIFORM'
default['content_placement']['name'] = 'TRANSIT_LOCAL'
default['content_placement']['percentage_local'] = 0.2
default['content_placement']['percentage_edge'] = 0.8
default['cache_policy']['name'] = CACHE_POLICY

default['topology']['name'] = 'ROCKET_FUEL'
default['topology']['source_ratio'] = 1.0
#default['topology']['ext_delay'] = 0 # XXX Latency penalty for reaching server is implemented in the LATENCY collector
default['topology']['asn'] = 3257
default['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL'
default['joint_cache_rsn_placement']['network_cache'] = NETWORK_CACHE
default['joint_cache_rsn_placement']['network_rsn'] = 100*NETWORK_CACHE


#default['warmup_strategy']['name'] = WARMUP_STRATEGY

for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for rsn_cache_ratio in [32.0, 64.0, 128.0, 256.0]:
        for strategy in ['FORWARD_TO_RS']: #, 'STOP_AND_WAIT', 'SEARCH_NEARBY']:
            experiment = copy.deepcopy(default)
            experiment['warmup_strategy']['name'] = strategy
            experiment['strategy']['name'] = strategy
            experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
            experiment['joint_cache_rsn_placement']['network_rsn'] = rsn_cache_ratio * NETWORK_CACHE
            experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = rsn_cache_ratio
            experiment['desc'] = "RSN size sensitivity -> RSN/cache ratio: %s" % str(rsn_cache_ratio)
            EXPERIMENT_QUEUE.append(experiment)
