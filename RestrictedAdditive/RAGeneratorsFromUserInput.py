def user_input_agents_list():
    """
    Walk the user through generating a list of agents.
    """
    agents_input = input("Enter the number of agents (or a comma-separated list of agent IDs): ")
    if "," in agents_input:
        agents_list = [int(x) for x in agents_input.split(",")]
    else:
        num_agents = int(agents_input)
        if num_agents <= 0:
            raise ValueError("Number of agents must be a positive integer.")
        agents_list = list(range(1, num_agents + 1))

    return agents_list

def user_input_generateRandomItems():
    """
    Walk the user through generating parameters for generateRandomItems()
    """
    generator_template = {}
    generator_template["generator_type"] = "generateRandomItems"
    generator_template["num_items"] = int(input("Enter the number of items to generate: "))
    generator_template["agents_involved"] = user_input_agents_list()
    generator_template["p"] = float(input("Enter the probability of each agent being included in an item (0.0 to 1.0): "))

    if generator_template["num_items"] <= 0:
        raise ValueError("Number of items must be a positive integer.")
    if generator_template["p"] < 0.0 or generator_template["p"] > 1.0:
        raise ValueError("Probability must be between 0.0 and 1.0.")

    return generator_template

def user_input_generateItemsOfDefinedOrder():
    """
    Walk the user through generating parameters for generateItemsOfDefinedOrder()
    """
    generator_template = {}
    generator_template["generator_type"] = "generateItemsOfDefinedOrder"
    generator_template["agents_involved"] = user_input_agents_list()
    orders_input = input("Enter the number of items to generate for each order, separated by commas (e.g. 5,10,15 for 5 items of order 1, 10 items of order 2, 15 items of order 3): ")
    generator_template["orders"] = tuple(int(x) for x in orders_input.split(","))
    if any(order < 0 for order in generator_template["orders"]):
        raise ValueError("Number of items for each order must be a non-negative integer.")
    if sum(generator_template["orders"]) == 0:
        raise ValueError("At least one item must be generated.")

    return generator_template

def user_input_generateItemValues_1_order_N_ranges():
    """
    Walk the user through generating parameters for generateItemValues_1_order_N_ranges()
    """
    generator_template = {}
    generator_template["generator_type"] = "generateItemValues_1_order_N_ranges"
    generator_template["agents_involved"] = user_input_agents_list()
    generator_template["order"] = int(input("Enter the order of the items (number of agents per item): "))
    if generator_template["order"] <= 0:
        raise ValueError("Order must be a positive integer.")
    value_ranges_input = input("Enter the value ranges for the items, in the format m:start-end, separated by commas (e.g. 5:1-10,10:21-30 for 5 items of value [1,...,10] and 10 items of value [21,...,30]): ")
    value_ranges = []
    for value_range in value_ranges_input.split(","):
        m, range_str = value_range.split(":")
        start, end = map(int, range_str.split("-"))
        if start > end:
            raise ValueError("Value range start must be less than or equal to end.")
        value_ranges.append((int(m), start, end))
    generator_template["value_ranges"] = value_ranges
    if any(m < 0 for m, _, _ in generator_template["value_ranges"]):
        raise ValueError("Number of items for each range must be a non-negative integer.")

    return generator_template

def user_input_generateItemValues_N_orders_1_range():
    """
    Walk the user through generating parameters for generateItemValues_N_orders_1_range()
    """
    generator_template = {}
    generator_template["generator_type"] = "generateItemValues_N_orders_1_range"
    generator_template["agents_involved"] = user_input_agents_list()
    orders_input = input("Enter the number of items to generate for each order, separated by commas (e.g. 5,10,15 for 5 items of order 1, 10 items of order 2, 15 items of order 3): ")
    generator_template["orders"] = tuple(int(x) for x in orders_input.split(","))
    if any(order < 0 for order in generator_template["orders"]):
        raise ValueError("Number of items for each order must be a non-negative integer.")
    if sum(generator_template["orders"]) == 0:
        raise ValueError("At least one item must be generated.")
    value_range_input = input("Enter the value range for the items (e.g. 1-10 for range [1,...,10]): ")
    start, end = map(int, value_range_input.split("-"))
    if start > end:
        raise ValueError("Value range start must be less than or equal to end.")
    generator_template["value_range"] = (start, end)

    return generator_template
