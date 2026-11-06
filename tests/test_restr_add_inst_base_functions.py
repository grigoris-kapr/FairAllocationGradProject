from RestrictedAdditive import RestrictedAdditiveInstance


# make a simple example graph
instance = RestrictedAdditiveInstance()

instance.add_agent("1")
instance.add_agent("2")
instance.add_agent("3")

instance.add_item(("1", "2"), 5)
instance.add_item(("2", "3"), 4)
instance.add_item(("1", "2", "3"), 3)

# test get_agent_max_value
assert instance.get_agent_max_value("1") == 8
assert instance.get_agent_max_value("2") == 12
assert instance.get_agent_max_value("3") == 7

# test get_agent_base_MMS_assumption
assert instance.get_agent_base_MMS_assumption("1") == (8/3)
assert instance.get_agent_base_MMS_assumption("2") == (12/3)
assert instance.get_agent_base_MMS_assumption("3") == (7/3)

