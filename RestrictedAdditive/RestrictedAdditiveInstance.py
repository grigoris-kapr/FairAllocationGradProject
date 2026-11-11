from hyperdb import HypergraphDB
import heapq
from typing import Dict, List
import MMS

# A class representing one instance of the problem
#
class RestrictedAdditiveInstance:
    # init during init
    graph: HypergraphDB
    num_items: int
    num_items_ever_added: int # used for unique item IDs
    complete: bool # Is initially False. When mark_completed() is run, complete is set to True and the heaps below are created.
    mms_were_manually_provided: bool # If True, won't do MMS calculations. Can be used to save the instance saving and retrieval during allocations.
    
    # init during completion
    all_items_heap: List
    agent_items_heap: Dict[int, List]
    items_allocated: List[bool] # item i was allocated if True

    def __init__(self):
        self.graph = HypergraphDB()
        self.num_items = 0
        self.num_items_ever_added = 0
        self.complete = False
        self.mms_were_manually_provided = False
        return

    # Adds agent to the exaple. Agents must be added sequentially.
    # Raises error if agentID already exists.
    def add_agent(self, agentID:int, metadata:dict=None):
        if self.complete:
            raise ValueError("Problem Instance was already marked as completed. No additions can be made.")
        if agentID in self.get_agent_IDs():
            raise ValueError("An agent with ID " + agentID + " is already present in the graph.")

        self.graph.add_v(agentID, metadata)

    # Add item to example. 
    # agentsInterested: list of agents IDs for the agents interested in the item
    # value: the value of the item, to be added to edge metadata
    # metadata: any metadata that we may need to keep for the item
    def add_item(self, agents_interested:tuple, value:int, item_metadata:dict=None):
        if self.complete:
            raise ValueError("Problem Instance was already marked as completed. No additions can be made.")

        itemID = self.num_items_ever_added
        if item_metadata:
            item_metadata["val"] = value
        else:
            item_metadata = {
                "val": value,
            }
        self.graph.add_e(agents_interested, {itemID:item_metadata})

        self.num_items += 1
        self.num_items_ever_added += 1

    # Removes an item from the corresponding edge in the graph.
    # Item must have been allocated and remove_item must always be called whenever an item is allocated.
    def remove_item(self, edge: tuple, itemID: int):
        # do checks here to provide more user-friendly errors
        if not self.complete:
            raise ValueError("Can only start removing items after Instance is marked completed.")
        if not self.graph.has_e(edge):
            raise ValueError("The provided item's edge does not exist. Can't remove.")
        if itemID not in self.graph.e(edge):
            raise ValueError("The provided item does not exist. Can't remove.")

        if not self.items_allocated[itemID]:
            raise ValueError("Cannot remove an item that has not yet been allocated.")
        
        # if this is the last item in the edge, we can simply delete the edge
        if len(self.graph._e_data[edge].keys()) == 1:
            self.graph.remove_e(edge)
        else:
            self.graph._e_data[edge].pop(itemID)
        

    def mark_completed(self):
        if self.complete:
            raise ValueError("Problem Instance was already marked as completed.")
        
        self.complete = True

        # create empty heaps
        self.all_items_heap = []
        # no need to call heapify on empty list
        self.agent_items_heap = {}
        for agentID in self.get_agent_IDs():
            self.agent_items_heap[agentID] = []
            # no need to call heapify on empty list  

        # add item to the global heap and to the heap for each agent
        # represented as (-item_value, itemID, edge, item_key) to make heap a max-heap of value with smallest ID as the secondary factor
        for edge in self.graph.all_e:
            edge_data = self.graph._e_data[edge]
            for itemID in edge_data:
                item_value = edge_data[itemID]["val"]
                heapq.heappush(self.all_items_heap, (-item_value, itemID, edge))

                for agentID in edge:
                    heapq.heappush(self.agent_items_heap[agentID], (-item_value, itemID, edge))

        # mark that no items have been allocated yet
        self.items_allocated = [False for _ in range(self.num_items_ever_added)]

    def get_agent_max_value(self, agentID:int):
        incident_edges = self.graph.nbr_e_of_v(agentID)
        total_value = 0
        for edge in incident_edges:
            edge_data = self.graph._e_data[edge]
            total_value += sum(edge_data[itemID]["val"] for itemID in edge_data)

        return total_value

    # Returns the baseline MMS for the agent based on the observation that MMS cannot ever be more than (1/n')*Σ where 
    # Σ is the sum of the (objective) values of the items that the agent is interested in,
    # n' is the number of agents that are competing for said items (including queried agent).
    def get_agent_proportional_share(self, agentID:int):
        max_value = self.get_agent_max_value(agentID)
        agents_competing = len(self.graph.nbr_v(agentID)) + 1 # +1 to include themselves
        return max_value / agents_competing

    def get_agent_IDs(self):
        return self.graph.all_v

    def num_agents(self):
        return self.graph.num_v

    def save(self, save_dir:str):
        self.graph.save(save_dir)

    # Returns the first item at top of the respective heap that wasn't allocated. 
    # Can be a slow method if we frequently switch between all_items_heap and agent_items_heap, 
    # since the respective while condition will often be true.
    #
    # Return values in order:
    #   - item value
    #   - item ID
    #   - edge (tupple of agent IDs)
    def allocate_best_item(self, agentID:int=None):
        item = None 
        # item will be tupple (-value, ID, (agents))
        # => item[1] is itemID
        # => self.items_allocated[item[1]] shows if item was previously allocated
        if agentID:
            item = heapq.heappop(self.agent_items_heap[agentID])
            while self.items_allocated[item[1]]:
                item = heapq.heappop(self.agent_items_heap[agentID])
        else:
            item = heapq.heappop(self.all_items_heap)
            while self.items_allocated[item[1]]:
                item = heapq.heappop(self.all_items_heap)

        self.items_allocated[item[1]] = True
        self.remove_item(item[2], item[1])
        
        return -item[0], item[1], item[2] # flip value back to positive for clarity outside of this class

    def filter_agents_by_items_available(self, original_agents_list):
        filtered_agents = [agent for agent in original_agents_list if self.graph.degree_v(agent) > 0]
        return filtered_agents

    def agent_has_item_available(self, agentID: int):
        return self.graph.degree_v(agentID) > 0 # this is sufficient since all allocated items are always deleted

    # load from file. see save()
    def load(self):
        raise NotImplementedError("Can't load instance directly from file.")

    def input_agents_MMS(self, preprocessed_MMS_values: dict):
        for agentID in preprocessed_MMS_values:
            self.graph.update_v(agentID, {"MMS":preprocessed_MMS_values[agentID]})

        if len(preprocessed_MMS_values.keys()) == len(self.graph._v_data.keys()):
            self.mms_were_manually_provided = True
        
    def MMS(self, agentID:int, symmetry_opt=True): 
        a_data = self.graph.v(agentID)
        if "MMS" in a_data:
            return a_data["MMS"]
        else:
            item_values = []
            incident_edges = self.graph.nbr_e_of_v(agentID)
            for edge in incident_edges:
                edge_data = self.graph._e_data[edge]
                for itemID in edge_data:
                    item_values.append(edge_data[itemID]["val"])

            agents_competing = len(self.graph.nbr_v(agentID)) + 1 # +1 to include themselves

            mms = MMS.AdditiveMMSSolver(agents_competing, item_values, symmetry_opt).mms_additive()
            return mms