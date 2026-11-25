"""
This includes 2 types of functions:
    1) Item generators: generate the edges / agent lists
        - require the number of agents or a list of valid agentIDs 
          (if number is provided, they'll make items for ids [1...n])
        - require a number of items to generate
        - return a list of edges
    2) Item-Value generators: generate both items and their values 
        - require the number of agents or a list of valid agentIDs
        - return a list of (edge, value) tuples
"""
import random

def generateRandomItems(agents:int | list[int], m:int, p:float, seed=None):
    """
    Generates **up to** m random items between agents.
    Each item includes agent i with probability p.
    If an item with no agents is produced, it is not added to the output.
    """
    if seed:
        random.seed(seed)

    if isinstance(agents, int):
        agents = list(range(agents))
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for item in range(m):
        edge = []
        for agent in agents:
            if random.random() <= p:
                edge.append(agent)
        if len(edge)>0:
            items.append(edge)

    return items

######################################################################################################################################################
def generateItemsOfDefinedOrder(agents: int | list, orders: tuple, seed=None):
    """
    Generates exactly order[i] items of oder i+1. 
        - orders[0] -> items with 1 interested agent
        - orders[1] -> items with 2 interested agents
        - orders[2] -> items with 3 interested agents
        etc.
    """
    if seed:
        random.seed(seed)
    
    if isinstance(agents, int):
        agents = list(range(agents))
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for i in range(len(orders)):
        for _ in range(orders[i]):
            items.append(random.sample(agents, i+1))

    return items

######################################################################################################################################################
def generateItemValues_1_order_N_ranges(agents: int | list[int], value_ranges: list[tuple], order: int = 3, seed=None):
    """
    Each range is tuple of (m, start, end).
    For each range, this will create exactly m items with an integer value in [start, ..., end].
    By default, the items will be of order 3.
    """
    if seed:
        random.seed(seed)
    
    if isinstance(agents, int):
        agents = list(range(agents))
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for m, start, end in value_ranges:
        for _ in range(m):
            edge = random.sample(agents, order)
            value = random.randint(start, end)

            items.append( (edge, value) )

    return items

######################################################################################################################################################
def generateItemValues_N_orders_1_range(agents: int | list[int], value_range: tuple, orders: tuple, seed=None):
    """
    Generates items of different orders with values in a single range.

    range is tuple of (start, end).
    orders is a tuple of the number of items to generate for each order.
        - orders[0] -> items with 1 interested agent
        - orders[1] -> items with 2 interested agents
        - orders[2] -> items with 3 interested agents
        etc.
    """
    if seed:
        random.seed(seed)
    
    if isinstance(agents, int):
        agents = list(range(agents))
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    start, end = value_range
    edges = generateItemsOfDefinedOrder(agents=agents, orders=orders, seed=seed)
    for edge in edges:
        value = random.randint(start, end)
        items.append( (edge, value) )

    return items