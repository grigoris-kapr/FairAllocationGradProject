#include "AdditiveMMSSolver.h"
#include <cstdio>
#include <algorithm>
#include <functional>

AdditiveMMSSolver::AdditiveMMSSolver(int num_agents, int num_items, unsigned long long* item_values, bool use_symmetry_opt) {
    this->num_agents = num_agents;
    this->num_items = num_items;

    this->item_values = new unsigned long long[num_items];
    std::copy(item_values, item_values+num_items, this->item_values);

    this->num_sums_reached_T = 0;
    this->use_symmetry_opt = use_symmetry_opt;
}

// Partition checker. More explanation required.
bool AdditiveMMSSolver::can_partition(
                    int m_idx, // the index in array item_values, the item we are allocating in this call
                    unsigned long long* sums, // the sums as provided by the previous call. sums[n] is the count of how many sums are >= T
                    unsigned long long T, // the threshold for which we are testing
                    unsigned long long remaining_sum // the sum of the values of all remaining items
) {
    if (m_idx == num_items) { return (num_sums_reached_T == num_agents); }

    for(int i=0; i<num_agents; i++) {
        // Symmetry pruning: If bundle i has the same val as a previous bundle, we don't need to check 
        // adding the current item to both, only the first one.
        if (use_symmetry_opt) {
            bool is_duplicate = false;
            for (int k=0; k<i; k++) {
                if ( sums[k] == sums[i] ) {
                    is_duplicate = true;
                    break;
                }
            }
            if (is_duplicate) continue;
        }

        // Maximum potential pruning
        if ( sums[i] + item_values[m_idx] + remaining_sum < T ) continue;

        // Check if bundle doesn't need more items
        if (sums[i] >= T) continue;

        // Try adding this item to the i-th bunle

        // Check if adding this item will make this bundle cross T valuation
        bool crossed_T = (sums[i] < T) && (sums[i] + item_values[m_idx] >= T);
        if (crossed_T) {
            this->num_sums_reached_T++;
            // If this bundle just crossed T, check the if it's the last one to do so
            if (num_sums_reached_T == num_agents) {
                num_sums_reached_T = 0;
                return true;
            }
        }

        // Add item to i-th bundle and run recursion
        sums[i] += item_values[m_idx];

        if (can_partition(m_idx + 1, sums, T, remaining_sum - item_values[m_idx])) {
            return true;
        }

        // Undo adding to the i-th bundle
        sums[i] -= item_values[m_idx];

        // If the i-th bundle had just crossed T, undo crossing it
        if (crossed_T) this->num_sums_reached_T--;

        // If adding to empty bundle failed, trying any other bundle will also fail.
        if (sums[i] == 0) break;
    }
    return false;
}



// Calculate the MMS for an agent using additive valuation function.
// num_agents: how many agents are competing for these items, i.e. how many bundles to make 
// num_items: how many items are there
// item_values: the values of the items, must be >=0, array must contain exactly num_items elements
int AdditiveMMSSolver::mms_additive() {
    // Check requirements
    for(int i=0; i<num_items; i++) if(item_values[i]<0) return -1;

    // Handle trivial cases
    if(num_agents > num_items) { 
        return 0; 
    }
    if(num_agents == num_items) {
        unsigned long long min = item_values[0];
        for(int i=1; i<num_items; i++) {
            if(item_values[i]<min) {
                min = item_values[i];
            }
        } 
        return min;
    }

    // Filter out items of value higher than the proportional share, allocating 1 per bundle.
    // If we allocate these items, the proportional share will go down. 
    // Since this is a single linear scan of all items, it's worth running this code in a loop.

    int num_items_before_allocation; // used to see if any were allocated and to cycle over all items
    unsigned long long total_items_value = 0;
    for(int i=0; i<num_items; i++) { total_items_value += item_values[i]; }
    unsigned long long proportional_share;

    do {
        num_items_before_allocation = num_items;
        proportional_share = total_items_value / num_agents;
        //std::printf("Proportional Share of the instance: %llu\n", proportional_share);
        //std::printf("\t Num agents:%d \t Num items: %d\n", num_agents, num_items);

        for(int i=0; i<num_items; i++) { 
            // Allocate any item of value higher than the proportional share to a bundle and 
            // reduce number of bundles and number of items by 1.
            if(item_values[i] >= proportional_share) {
                //std::printf("allocating item %d with value %llu\n", i, item_values[i]);
                num_agents--;
                unsigned long long temp_val = item_values[i];
                item_values[i] = item_values[num_items-1];
                item_values[num_items-1] = temp_val;
                num_items--;

                // Also keep track of total value for subsequent loops 
                // by subtracting the value of the item just allocated
                total_items_value -= item_values[num_items];

                // After a swap, end of array contains the item we just checked off 
                // and position i contains an unchecked item. 
                // Therefore loop runs until num_items and we reduce i by 1 if we just swapped something
            }
        }
    } while(num_items_before_allocation != num_items); 


    //std::printf("Finished PS trick!\n");
    // Can I do any more tricks???



    // Brute force the rest with binary search

    // sort array in descending order for better pruning
    std::sort(item_values, item_values + num_items, std::greater<unsigned long long>());

    unsigned long long low = item_values[num_items-1];
    unsigned long long high = total_items_value / num_agents; // proportional_share may be out of date right now
    unsigned long long best_mms = low;

    while (low <= high) {
        unsigned long long mid = (low + high) / 2;
        
        //std::printf("Current MMS range: %d to %d \t Testing: %d \t", low, high, mid);

        unsigned long long sums[num_agents]; 
        for(int i=0; i<num_agents; i++) sums[i] = 0;

        if ( can_partition(0, sums, mid, total_items_value) ) {
            //std::printf("T\n");
            low = mid + 1; 
            best_mms = mid;
        } else {
            //std::printf("F\n");
            high = mid - 1;
        }
    }

    return best_mms;

    
}
