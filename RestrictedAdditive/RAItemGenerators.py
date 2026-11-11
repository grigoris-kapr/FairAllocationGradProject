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

"""
Generates **up to** m random items between agents.
Each item includes agent i with probability p.
If an item with no agents is produced, it is not added to the output.
"""
def generateRandomItems(agents:int | list[int], m:int, p:float, seed=None):
    if seed:
        random.seed(seed)

    if type(agents) is int:
        agents = range(agents)
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for item in range(m):
        edge = []
        for agent in agents:
            if random() <= p:
                edge.append(agent)
        if len(edge)>0:
            items.append(edge)

    return items

"""
Generates exactly order[i] items of oder i+1. 
    - order[0] -> items with 1 interested agent
    - order[1] -> items with 2 interested agents
    - order[2] -> items with 3 interested agents
    etc.
"""
def generateItemsOfDefinedOrder(agents: int | list, order: tuple, seed=None):
    if seed:
        random.seed(seed)
    
    if type(agents) is int:
        agents = range(agents)
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for i in range(len(order)):
        for _ in range(order[i]):
            items.append(random.sample(agents, i+1))

    return items

"""
Each range is tuple of (m, start, end).
For each range, this will create exactly m items with an integer value in [start, ..., end].
By default, the items will be of order 3.
"""
def generateItemValues_MultipleValueRanges(agents: int | list[int], ranges: list[tuple], order: int = 3, seed=None):
    if seed:
        random.seed(seed)
    
    if type(agents) is int:
        agents = range(agents)
        for i in range(len(agents)):
            agents[i] += 1

    items = []
    for m, start, end in ranges:
        for _ in range(m):
            edge = random.sample(agents, order)
            value = random.randint(start, end)

            items.append( (edge, value) )

    return items
