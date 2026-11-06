#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include "AdditiveMMSSolver.h" 

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++ backend for AdditiveMMSSolver";

    py::class_<AdditiveMMSSolver>(m, "AdditiveMMSSolver")
        .def(py::init([](int num_agents, const std::vector<unsigned long long>& item_values, bool use_symmetry_opt) {
                // Automatically derives num_items from the size of the Python list/array,
                // preventing size mismatch bugs.
                return new AdditiveMMSSolver(
                    num_agents, 
                    static_cast<int>(item_values.size()), 
                    const_cast<unsigned long long*>(item_values.data()), 
                    use_symmetry_opt
                );
            }),
            py::arg("num_agents"),
            py::arg("item_values"),
            py::arg("use_symmetry_opt"),
            "Initialize the AdditiveMMSSolver.\n\n"
            "Args:\n"
            "    num_agents (int): Number of agents / bundles.\n"
            "    item_values (list[int]): Values of each item.\n"
            "    use_symmetry_opt (bool): Enable symmetry check pruning optimization. \n"
            "        Speed-up / Slow-down depending on values distribution."
        )
        .def("mms_additive", &AdditiveMMSSolver::mms_additive, 
             "Executes the MMS calculation and returns the result.");
}