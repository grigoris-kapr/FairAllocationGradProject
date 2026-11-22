from unittest.mock import MagicMock, patch
import pytest

from RestrictedAdditive import RestrictedAdditiveInstance


def _build_sample_instance() -> RestrictedAdditiveInstance:
    """Create a completed instance with 2 agents and 3 items."""
    inst = RestrictedAdditiveInstance()
    inst.add_agent(0, {"name": "Alice"})
    inst.add_agent(1, {"name": "Bob"})

    # Edge (0, 1): both agents interested
    inst.add_item((0, 1), value=10)
    inst.add_item((0, 1), value=4)
    # Edge (1,): only agent 1 interested
    inst.add_item((1,), value=7)

    inst.mark_completed()
    return inst


def test_lifecycle_and_proportional_share():
    inst = _build_sample_instance()

    assert inst.complete is True
    assert inst.num_agents() == 2
    assert inst.num_items == 3
    assert set(inst.get_agent_IDs()) == {0, 1}

    # Agent 0 sees items worth 10 and 4 (total 14) with 2 competing agents -> 7.0
    assert inst.get_agent_max_value(0) == 14
    assert inst.get_agent_proportional_share(0) == pytest.approx(7.0)

    # Agent 1 sees items worth 10, 4, and 7 (total 21) with 2 competing agents -> 10.5
    assert inst.get_agent_max_value(1) == 21
    assert inst.get_agent_proportional_share(1) == pytest.approx(10.5)


def test_allocate_best_item_global_and_per_agent():
    inst = _build_sample_instance()

    # Highest overall item has value 10 on edge (0, 1)
    val, item_id, edge = inst.allocate_best_item()
    assert val == 10
    assert edge == (0, 1)

    # Next highest overall is value 7 on edge (1,)
    val2, _, edge2 = inst.allocate_best_item()
    assert val2 == 7
    assert edge2 == (1,)

    # Agent 0's remaining item is value 4 on edge (0, 1)
    assert inst.agent_has_item_available(0) is True
    val3, _, edge3 = inst.allocate_best_item(agentID=0)
    assert val3 == 4
    assert edge3 == (0, 1)

    # After removing the last item on (0, 1), neither agent has items left
    assert inst.agent_has_item_available(0) is False
    assert inst.agent_has_item_available(1) is False
    assert inst.filter_agents_by_items_available([0, 1]) == []


def test_mutations_blocked_after_completion():
    inst = _build_sample_instance()

    with pytest.raises(ValueError, match="already marked as completed"):
        inst.add_agent(2)

    with pytest.raises(ValueError, match="already marked as completed"):
        inst.add_item((0,), value=5)

    with pytest.raises(ValueError, match="already marked as completed"):
        inst.mark_completed()


def test_remove_item_requires_prior_allocation():
    inst = _build_sample_instance()

    # Item 0 was added first and has not been allocated yet
    with pytest.raises(ValueError, match="not yet been allocated"):
        inst.remove_item((0, 1), itemID=0)


def test_manual_mms_bypasses_solver_and_falls_back_to_cpp_solver():
    inst = _build_sample_instance()

    # Provide manual MMS for agent 0 only
    inst.input_agents_MMS({0: 6})
    assert inst.mms_were_manually_provided is False

    with patch("MMS.AdditiveMMSSolver") as mock_solver_cls:
        assert inst.MMS(0) == 6
        mock_solver_cls.assert_not_called()

        mock_instance = MagicMock()
        mock_instance.mms_additive.return_value = 7
        mock_solver_cls.return_value = mock_instance

        assert inst.MMS(1, symmetry_opt=True) == 7
        mock_solver_cls.assert_called_once_with(2, [10, 4, 7], True)

    # Providing MMS for all agents sets the flag
    inst.input_agents_MMS({0: 6, 1: 7})
    assert inst.mms_were_manually_provided is True
