from typing import List, Tuple, Set, Any
from TP04.Operands import Operand, Temporary, S, Register, GP_REGS, FP
from TP04.Instruction3A import Instru3A
from TP04.SimpleAllocations import Allocator
from .LibGraphes import Graph, DiGraph  # For Graph coloring utility functions
from Errors import MiniCInternalError


def replace_smart(old_i):
    """Replace Temporary operands with the corresponding allocated
    physical register OR memory location."""
    before = []
    after = []
    ins, old_args = old_i.unfold()
    args = []
    # TODO (lab5): compute before,after,args. This is similar to what
    # TODO (lab5): replace_mem and replace_reg from TP04 do.
    # and now return the new list!
    i = Instru3A(ins, args=args)  # change argument list into args
    return before + [i] + after


class SmartAllocator(Allocator):

    _igraph: Graph  # interference graph

    def __init__(self, function, basename, liveness,
                 debug=False, debug_graphs=False, *args):
        self._liveness = liveness
        self._basename = basename
        self._debug = debug
        self._debug_graphs = debug_graphs
        super().__init__(function, *args)

    def prepare(self):
        """Perform all steps related to smart register allocation:

        - Dataflow analysis to compute liveness range of each
          temporary.

        - Interference graph construction

        - Graph coloring

        - Substitution of temporaries by actual locations in the
          3-address code.
        """
        # prints the CFG as a dot file
        if self._debug_graphs:
            self._function_code.print_dot(self._basename + ".dot", view=True)
            print("CFG generated in " + self._basename + ".dot.pdf")
        # TODO (lab5): Move the raise statement below down as you progress
        # TODO (lab5): in the lab. It must be removed from the final version.
        raise NotImplementedError("run: stopping here for now")

        # liveness analysis
        self._liveness.run()

        # conflict graph
        self.build_interference_graph()

        if self._debug_graphs:
            print("printing the conflict graph")
            self._igraph.print_dot(self._basename + "_conflicts.dot")

        # Smart Alloc via graph coloring
        self.smart_alloc(self._basename + "_colored.dot")

    def rewriteCode(self, listcode):
        # Finally, modify the code to replace temporaries with
        # regs/memory locations
        self._function_code.iter_instructions(replace_smart)

    def interfere(self, t1, t2):
        """Interfere function: True if t1 and t2 are in conflit anywhere in
        the function."""
        raise NotImplementedError("interfere() function (lab5)") # TODO

    def build_interference_graph(self):
        """Build the interference graph. Nodes of the graph are temporaries,
        and an edge exists between temporaries iff they are in conflict (i.e.
        iff self.interfere(t1, t2)."""
        self._igraph = Graph()
        t = self._function_code._pool._all_temps
        raise NotImplementedError("interference graph (lab5)") # TODO

    def smart_alloc(self, outputname):
        """Allocate all temporaries with graph coloring
        also prints the colored graph if debug.

        Precondition: the interference graph (_igraph) must have been
        initialized.
        """
        if not self._igraph:
            raise MiniCInternalError("hum, the interference graph seems to be empty")
        # Temporary -> Operand (register or offset) dictionary,
        # specifying where a given Temporary should be allocated:
        alloc_dict = {}
        # TODO (lab5): color the graph and get back the coloring (see
        # Graph.color() in LibGraphes.py). Then, construct a dictionary Temporary ->
        # Register or Offset. Our version is less than 15 lines
        # including debug log. You can get all temporaries in
        # self._function_code._pool._all_temps.
        raise NotImplementedError("Allocation based on graph colouring (lab5)")
        self._function_code._pool.set_temp_allocation(alloc_dict)
        self._function_code._stacksize = self._function_code.get_offset()


def generate_smart_move(dest: Operand, src: Operand) -> List[Instru3A]:
    """Generate a list of move, store and load instructions, depending if the
    operands are registers or memory locations"""
    instr = []
    return instr


def sequentialize_moves(tmp: Register,
                        parallel_moves: Set[Tuple[Any, Any]]) -> List[Tuple[Any, Any]]:
    """Take a set of parallel moves represented as (destination, source) pairs,
    and return a list of sequential moves which respect the cycles.
    Use the specified tmp for cycles.
    Returns a list of (destination, source) pairs"""
    move_graph = DiGraph()
    for dest, src in parallel_moves:
        move_graph.add_edge((src, dest))
    moves = []
    # First iteratively remove all the edges without successors.
    vars_without_successor = {src
                              for src, dests in move_graph.neighbourhoods()
                              if len(dests) == 0}
    while vars_without_successor:
        var = vars_without_successor.pop()
        for src, dests in move_graph.neighbourhoods():
            if var in dests:
                moves.append((var, src))
                dests.remove(var)
                if len(dests) == 0:
                    vars_without_successor.add(src)
        move_graph.delete_vertex(var)
    # Then handle the cycles.
    cycles = move_graph.connex_components()
    for cycle in cycles:
        if len(cycle) == 1:
            v = cycle.pop()
            moves.append((v, v))
        else:
            previous = tmp
            for v in reversed(cycle):
                moves.append((previous, v))
                previous = v
            moves.append((previous, tmp))
    return moves
