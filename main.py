from RestrictedAdditive import RestrictedAdditiveInstance, RAItemGenerators, RAGeneratorsFromUserInput, traversal_allocation
from hyperdb.draw import HypergraphViewer
import random
from pathlib import Path
from datetime import datetime
import json

# Helper to print warnings in yellow
def print_warning(message:str):
    print("\033[93m" + message + "\033[0m")

def user_input_num_instances():
    num_instances = int(input("Enter the number of instances to generate: "))
    # validate num_instances
    if isinstance(num_instances, int) == False or num_instances <= 0:
        raise ValueError("Number of instances must be a positive integer.")

    return num_instances

def user_input_instance_template():
    """
    Walk the user through selecting number of instances, instance template, allocator algorithm, and seed
    """

    instance_template = {}

    instance_template["num_agents"] = int(input("Enter the number of agents: "))
    # validate num_agents
    if isinstance(instance_template["num_agents"], int) == False or instance_template["num_agents"] <= 0:
        raise ValueError("Number of agents must be a positive integer.")
    elif instance_template["num_agents"] >= 10:
        print_warning("Warning: Doing allocation for instances with 10 or more agents may take a long time.")

    instance_template["seed"] = input("Enter a seed for random number generation (or leave blank for system-selected seed): ")
    # validate seed
    if instance_template["seed"] != "":
        try:
            instance_template["seed"] = int(instance_template["seed"])
        except ValueError:
            raise ValueError("Seed must be an integer.")
    else:
        instance_template["seed"] = random.randint(0, 2**32 - 1) # system-selected seed
        print(f"Using system-selected seed: {instance_template['seed']}")

    # To support multiple generators in the same experiment, generator info is stored as:
    # instance_template["generators"] = [
    #   {
    #       "generator_num": int
    #       "generator_type": one of the valid types
    #       "agents_involved": list of agent IDs
    #       additional generator-specific parameters as needed
    #   },
    #   ...
    # ]
    instance_template["generators"] = []
    user_selected_exit = False
    generator_num = 0
    while user_selected_exit == False:
        generator_template = {}
        generator_template["generator_num"] = generator_num

        user_selection = input(f"Select an item/edge generator type: \
                                \n[1] Random Edge (generateRandomItems): {RAItemGenerators.generateRandomItems.__doc__} \
                                \n[2] Defined Order Edge (generateItemsOfDefinedOrder): {RAItemGenerators.generateItemsOfDefinedOrder.__doc__} \
                                \n[3] Items 1 Order, N Value Ranges (generateItemValues_1_order_N_ranges): {RAItemGenerators.generateItemValues_1_order_N_ranges.__doc__} \
                                \n[4] Items N Orders, 1 Value Range (generateItemValues_N_orders_1_range): {RAItemGenerators.generateItemValues_N_orders_1_range.__doc__} \
                                \n[0] Exit generator selection")

        if user_selection == "0":
            user_selected_exit = True
            break
        elif user_selection == "1":
            generator_template.update(RAGeneratorsFromUserInput.user_input_generateRandomItems())
            if generator_template["num_items"] * generator_template["p"] * len(generator_template["agents_involved"]) > 1000:
                print_warning("Warning: These paraameters may cause allocation and MMS computation to take a long time.")

        elif user_selection == "2":
            generator_template.update(RAGeneratorsFromUserInput.user_input_generateItemsOfDefinedOrder())
            if sum(generator_template["orders"]) * len(generator_template["agents_involved"]) > 1000:
                print_warning("Warning: These parameters may cause allocation and MMS computation to take a long time.")

        elif user_selection == "3":
            generator_template.update(RAGeneratorsFromUserInput.user_input_generateItemValues_1_order_N_ranges())
            # no warning implemented yet

        elif user_selection == "4":
            generator_template.update(RAGeneratorsFromUserInput.user_input_generateItemValues_N_orders_1_range())
            # no warning implemented yet

        else:
            print_warning("Invalid selection. Please select a valid generator type. (int 0-4)")
            continue

        # validate that all agent IDs are within the range of the number of agents in the instance
        if max(generator_template["agents_involved"]) > instance_template["num_agents"]:
            print_warning("Generator specified agent IDs that exceed the number of agents in the instance.")
            continue

        # if user selected an edge generator, pick the range of values
        if user_selection in ["1", "2"]:
            value_ranges_input = input("Enter the value range for the items, in the format start-end (e.g. 1-10 for values [1,...,10]): ")
            try:
                start, end = map(int, value_ranges_input.split("-"))
                if start > end:
                    print_warning("Start of range must be less than or equal to end of range.")
                    continue
                generator_template["value_range"] = (start, end)
            except ValueError:
                print_warning("Invalid value range format. Please enter in the format start-end (e.g. 1-10).")
                continue

        instance_template["generators"].append(generator_template)
        generator_num += 1


    # choose allocator here???

    return instance_template



if __name__ == "__main__":
    num_instances = user_input_num_instances()
    instance_template = user_input_instance_template()

    run_dir = Path("experiments") / datetime.now().strftime("run_%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "instances").mkdir(parents=True, exist_ok=True)

    # Save all user input to a file for later reference
    with open(run_dir / "instance_template.json", "w") as f:
        experiment_info = {}
        experiment_info["num_instances"] = num_instances
        experiment_info.update(instance_template)
        json.dump(experiment_info, f, indent=4)
    

    for i in range(num_instances):
        print(f"Generating instance {i+1} of {num_instances}...")

        # Set seed instance-wide for reproducibility
        random.seed(instance_template["seed"] + i)

        example_instance = RestrictedAdditiveInstance()
        for agentID in range(instance_template["num_agents"]):
            example_instance.add_agent(agentID+1)

        for generator in instance_template["generators"]:
            assert isinstance(generator, dict), "Generator must be a dictionary."
            if generator["generator_type"] == "generateRandomItems":
                items = []
                edges = RAItemGenerators.generateRandomItems(generator["agents_involved"], generator["num_items"], generator["p"])
                start, end = generator["value_range"]
                for edge in edges:
                    value = random.randint(start, end)
                    items.append((edge, value))
            elif generator["generator_type"] == "generateItemsOfDefinedOrder":
                items = []
                edges = RAItemGenerators.generateItemsOfDefinedOrder(generator["agents_involved"], generator["orders"])
                start, end = generator["value_range"]
                for edge in edges:
                    value = random.randint(start, end)
                    items.append((edge, value))
            elif generator["generator_type"] == "generateItemValues_1_order_N_ranges":
                items = RAItemGenerators.generateItemValues_1_order_N_ranges(generator["agents_involved"], generator["value_ranges"], generator.get("order", 3), seed=generator.get("seed", None))
            elif generator["generator_type"] == "generateItemValues_N_orders_1_range":
                items = RAItemGenerators.generateItemValues_N_orders_1_range(generator["agents_involved"], generator["value_range"], generator.get("orders", (3,)), seed=generator.get("seed", None))
            else:
                raise ValueError(f"Unknown generator type: {generator['generator_type']}")

            for item in items:
                example_instance.add_item(item[0], item[1])
                print(f"Added item: {item}")

        example_instance.mark_completed()
        filename = run_dir / "instances" / f"example_instance_{i+1}.json"
        example_instance.save(str(filename))
        print(f"Saved instance {i+1} to {filename}")

        if num_instances == 1:
            viewer = HypergraphViewer(example_instance.graph)
            viewer.start_server(open_browser=False)
            input("Press Enter to stop the server...")
            viewer.stop_server()