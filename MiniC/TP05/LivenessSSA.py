from typing import Dict, Set, Tuple
from TP04.Operands import Operand
from TP04.Instruction3A import Instruction, regset_to_string
from TP05.CFG import Block
from TP05.SSA import PhiNode


class LivenessSSA:

    def __init__(self, function, debug=False):
        self._function = function
        self._debug = debug
        self._seen: Dict[Block, Set[Operand]] = dict()
        # Live Operands at outputs of instructions
        self._liveout: Dict[Instruction, Set[Operand]] = dict()

    def run(self):
        # Initialization
        for block in self._function.get_blocks():
            self._seen[block] = set()
            for instr in block.get_instructions():
                self._liveout[instr] = set()
        # Start the use-def chains
        for var, uses in self.gather_uses().items():
            for block, pos, instr in uses:
                self.live_start(block, pos, instr, var)
        # Add conflicts on phis
        self.conflict_on_phis()
        # Final debuging print
        if self._debug:
            self.print_map_in_out()

    def live_start(self, block: Block, pos: int,
                   instr: Instruction, var: Operand) -> None:
        """Start backward propagation of liveness information"""
        if isinstance(instr, PhiNode):
            for label, op in instr.used().items():
                if op == var:
                    prev_block = self._function.get_block(label)
                    self.liveout_at_block(prev_block, var)
        else:
            self.livein_at_instruction(block, pos, var)

    def liveout_at_block(self, block: Block, var: Operand) -> None:
        """Backward propagation of liveness information at a block."""
        pass # TODO (lab5b, exercise 1)

    def liveout_at_instruction(self, block: Block, pos: int, var: Operand) -> None:
        """Backward propagation of liveness information at an instruction."""
        instr = block.get_instructions()[pos]
        # TODO (lab5b, exercise 1)

    def livein_at_instruction(self, block: Block, pos: int, var: Operand) -> None:
        """Backward propagation of liveness information at an instruction."""
        pass # TODO (lab5b, exercise 1)

    def gather_uses(self) -> Dict[Operand, Set[Tuple[Block, int, Instruction]]]:
        uses: Dict[Operand, Set[Tuple[Block, int, Instruction]]] = dict()
        for block in self._function.get_blocks():
            for pos, instr in enumerate(block.get_instructions()):
                args = instr.used().values() if isinstance(instr, PhiNode) else instr.used()
                for var in args:
                    if var is not None:
                        var_uses = uses.get(var, set())
                        uses[var] = var_uses.union({(block, pos, instr)})
        return uses

    def conflict_on_phis(self):
        """Ensures that variables defined by phi instructions are in conflict
        with one-another"""
        for b in self._function.get_blocks():
            phis = [i for i in b.get_instructions() if isinstance(i, PhiNode)]
            previous_vars = set()
            for phi in phis:
                previous_vars.update(phi.defined())
                self._liveout[phi].update(previous_vars)

    def print_gen_kill(self):  # pragma: no cover
        print("Dataflow Analysis, Initialisation")
        i = 0
        for blk in self._function.get_blocks():
            blk.print_gen_kill(i)
            i += 1

    def print_map_in_out(self):  # pragma: no cover
        """Print out sets, useful for debug!"""
        print("Out: {" +
              ",\n ".join("\"{}\": {}"
                          .format(x, regset_to_string(self._liveout[x]))
                          for x in self._liveout.keys()) +
              "}")
