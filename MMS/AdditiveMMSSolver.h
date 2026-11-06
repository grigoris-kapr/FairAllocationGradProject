class AdditiveMMSSolver {
public:
    AdditiveMMSSolver(int num_agents, int num_items, unsigned long long* item_values, bool use_symmetry_opt);
    int mms_additive();
private:
    int num_agents; // the number of agents / bundles for the allocation
    int num_items; // the number of items
    unsigned long long* item_values; // the value of each item
    int num_sums_reached_T; // used in can_partition to see if T was easily met before using all items
    bool use_symmetry_opt; // if using symmetry check optimization is enabled

    bool can_partition(int m_idx, unsigned long long* sums, unsigned long long T, unsigned long long remaining_sum);
};