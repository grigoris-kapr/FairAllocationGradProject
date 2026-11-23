from RestrictedAdditive import RestrictedAdditiveInstance, RAItemGenerators
from hyperdb.draw import HypergraphViewer
from time import sleep

num_agents = 5
item_ranges = [
    (15, 1, 10), # 15 items of value [1,...,10]
    (5, 21, 30), # 5 items of value [21,...,30]
]

example_instance = RestrictedAdditiveInstance()

for i in range(num_agents):
    example_instance.add_agent(i+1)

# items are tuples of (edge, value)
items = RAItemGenerators.generateItemValues_MultipleValueRanges(num_agents, item_ranges,seed=43)


for i in range(len(items)):
    item = items[i]
    example_instance.add_item(item[0], item[1])
    print(f"Added item {i}: {item}")

for agent in example_instance.get_agent_IDs():
    max_value = example_instance.get_agent_max_value(agent)
    proportional_share = example_instance.get_agent_proportional_share(agent)
    mms = example_instance.MMS(agent)

    print(f"Agent {agent} has \n\t max value {max_value} \n\t proportional share {proportional_share} \n\t MMS {mms}")

example_instance.mark_completed()

example_instance.graph.draw(port = 8080, open_browser=False)
