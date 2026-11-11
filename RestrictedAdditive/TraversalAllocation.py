from RestrictedAdditive import RestrictedAdditiveInstance
from hyperdb import HypergraphDB
import random

def _random_pick_tr_al(problem_instance:RestrictedAdditiveInstance, seed:int=None):
    if seed:
        random.seed(seed)

    agent_ids = problem_instance.get_agent_IDs() # used to make allocation
    agents_with_items = list(agent_ids) # kept updated for quick jumps when we reach a dead-end in the traversal

    allocation = {}
    agent_values = {}

    for id in agent_ids:
        allocation[id] = []
        agent_values[id] = 0

    # first we pick a random agent from all agents with items
    agents_to_pick_from = agents_with_items
    # we allocate 1 item per iteration
    num_iter = problem_instance.num_items
    for i in range(num_iter):
        if len(agents_to_pick_from) > 0:
            current_agent_id = random.choice(agents_to_pick_from)
        else:
            current_agent_id = random.choice(agents_with_items)
            while not problem_instance.agent_has_item_available(current_agent_id):
                agents_with_items.remove(current_agent_id)
                current_agent_id = random.choice(agents_with_items)

        value, itemID, agents_interested = problem_instance.allocate_best_item(current_agent_id)

        allocation[current_agent_id].append(itemID)
        agent_values[current_agent_id] += value

        # next agent will be chosen from the other agents interested in the same item
        agents_to_pick_from = (agent for agent in agents_interested if agent != current_agent_id)
        agents_to_pick_from = problem_instance.filter_agents_by_items_available(agents_to_pick_from)
        
        print(f"Iteration {i}: agent {current_agent_id} picked item i{itemID}:v{value}:{agents_interested}.")

    return allocation, agent_values



# A family of algorithms that traverse the graph and allocate 1 item for every iteration. 
# Criteria change depending on 'algorithm' parameter.
def traversal_allocation(
        problem_instance: RestrictedAdditiveInstance, # an instance of the problem
        save_dir: str = None, # directory to save instance hypergraph and potentially load for MMS calculations
        algorithm: str = None, # algorithm to use. Implemented algorithms: {"Random Pick"}
        seed: int = None, # seed to be used for random 
    ):
    # check valid algorithm
    algs_implemented = {"Random Pick"}
    if algorithm:
        if algorithm not in algs_implemented:
            raise ValueError("\"" + algorithm + "\" does not corespond to one of the implemented algorithms.")
    else:
        # default to Random Pick
        algorithm = "Random Pick"

    if not problem_instance.mms_were_manually_provided:
        # save original instance for later recall as we're going to edit it
        problem_instance.save(save_dir)

    # calculate proportional share per agent to compare to allocated value and determine if we'll need to find exact MMS
    proportional_shares = {}
    for agentID in problem_instance.get_agent_IDs():
        proportional_shares[agentID] = problem_instance.get_agent_proportional_share(agentID)

    # call the algorithm function requested
    allocation = {}
    agent_values = {}
    if algorithm == "Random Pick":
        allocation, agent_values = _random_pick_tr_al(problem_instance, seed)

    agents_for_MMS_comp = []
    for agentID in problem_instance.get_agent_IDs():
        if agent_values[agentID] < proportional_shares[agentID]:
            agents_for_MMS_comp.append(agentID)
        else:
            print(f"Met proportional share for agent {agentID}")

    met_all_MMS = True
    if len(agents_for_MMS_comp) > 0:
        if not problem_instance.mms_were_manually_provided:
            instance_MMS_compare = RestrictedAdditiveInstance.load(save_dir)
        else:
            instance_MMS_compare = problem_instance

        # this is gonna be the slow part.
        # can make it multithreaded
        for agentID in agents_for_MMS_comp:
            if instance_MMS_compare.MMS(agentID) > agent_values[agentID]:
                met_all_MMS = False
                print(f"Failed to meet MMS for agent {agentID}: \n\
                      MMS: {instance_MMS_compare.MMS(agentID)} \n\
                      value: {agent_values[agentID]}")
            else:
                print(f"Met MMS for agent {agentID}")

    if met_all_MMS:
        print("Met all MMS!")
    else:
        print("Failed to meet at least one agent's MMS :(")

    return allocation, agent_values

    
        


    