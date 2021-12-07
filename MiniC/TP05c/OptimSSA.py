#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
CAP, SSA Intro, Elimination and Optimisations
Optimisations on SSA.
"""

from enum import Enum
from Errors import MiniCInternalError
from typing import List, Dict, Optional, Union, Tuple, cast
from TP05.CFG import (Block, CFG)
from TP04.Operands import (Operand, Temporary, Immediate, A, ZERO)
from TP04.Instruction3A import (Instruction, Instru3A, Label, CondJump)
from TP05.SSA import PhiNode


def div_rd_0(a: int, b: int) -> int:
    """ Division rounded towards 0 (integer division in Python rounds down). """
    return -(-a // b) if (a < 0) ^ (b < 0) else a // b


def mod_rd_0(a: int, b: int) -> int:
    """ Modulo rounded towards 0 (integer division in Python rounds down). """
    return -(-a % b) if (a < 0) ^ (b < 0) else a % b


class Lattice(Enum):
    Bottom = 0
    Top = 1


LATTICE_VALUE = Union[int, Lattice]


def join(v1: LATTICE_VALUE, v2: LATTICE_VALUE) -> LATTICE_VALUE:
    if v1 == Lattice.Top or v2 == Lattice.Top:
        return Lattice.Top
    elif isinstance(v1, int) and isinstance(v2, int):
        if v1 == v2:
            return v1
        else:
            return Lattice.Top
    elif v1 == Lattice.Bottom:
        return v2
    elif v2 == Lattice.Bottom:
        return v1
    else:
        return Lattice.Bottom


def joinl(values: List[LATTICE_VALUE]) -> LATTICE_VALUE:
    res = Lattice.Bottom
    for v in values:
        res = join(res, v)
    return res


def has_top(values: List[LATTICE_VALUE]) -> bool:
    return any((x == Lattice.Top for x in values))


def has_bottom(values: List[LATTICE_VALUE]) -> bool:
    return any((x == Lattice.Bottom for x in values))


class CondConstantPropagation:
    """
    Class that optimises a function
    following the algorithm "Sparse Conditionnal Constant Propagation".
    """

    _function: CFG
    valueness: Dict[Operand, LATTICE_VALUE]
    # Values of each variable v:
    # valueness[v] = Lattice.Bottom if no evidence that v is assigned
    # valueness[v] = n if we found evidence that only n is assigned to v
    # valueness[v] = Lattice.Top if we found evidence that v is assigned
    # to at least two different values

    executability: Dict[Tuple[Optional[Block], Block], bool]
    # Exectuability of an edge (B, C):
    # executability[B, C] = False if no evidence that the edge (B, C) can ever be executed
    # executability[B, C] = True if (B, C) may be executed (over-approximation)

    _modified_flag: bool

    def __init__(self, function: CFG):
        self._function = function
        self.valueness = dict()
        self.executability = dict()

        self._all_vars = function.gather_defs().keys()
        self._all_blocks: List[Block] = function.get_blocks()

        # Initialisation of valueness and executability
        for var in self._all_vars:
            self.valueness[var] = Lattice.Bottom
        for block in self._all_blocks:
            for block_succ in block._out:
                self.executability[block, block_succ] = False
        # Add an init edge from None to the start block
        start_blk = self._function.get_block(self._function._start)
        self.executability[None, start_blk] = False

    def dump(self) -> None:
        """
        For debug purposes: print valueness and executability.
        """
        print("Valueness:")
        for x, v in self.valueness.items():
            print("{0}: {1}".format(x, v))
        print("Executability:")
        for (B, C), v in self.executability.items():
            print("{0} -> {1}: {2}".format(B.get_label() if B is not None else "",
                                           C.get_label(), v))

    def set_valueness(self, v: Operand, x: LATTICE_VALUE) -> None:
        """
        Update the valueness of a variable by performing a join with
        its current value.
        """
        old_x = self.valueness[v]
        new_x = join(x, old_x)
        if new_x != old_x:
            self._modified_flag = True
            self.valueness[v] = new_x

    def set_executability(self, B: Optional[Block], C: Block) -> None:
        """
        Mark an edge as executable.
        """
        old_x = self.executability[B, C]
        if not old_x:
            self._modified_flag = True
            self.executability[B, C] = True

    def is_constant(self, op: Operand) -> bool:
        return isinstance(self.valueness.get(op, None), int)

    def is_executable(self, B: Block) -> bool:
        return B in (C for ((_, C), b) in self.executability.items() if b)

    def compute(self, debug: bool) -> None:
        """
        Compute executability for all edges and valueness for all variables
        using a fixpoint algorithm.
        """
        # 1. For any v comming from outside the function (parameters, function calls),
        # set valueness[v] = Top. These are exactly the registers of A.
        for var in A:
            self.valueness[var] = Lattice.Top

        # 2. The start block is executable, with an init edge coming from None
        start_blk = self._function.get_block(self._function._start)
        self.set_executability(None, start_blk)

        # Start fixpoint
        self._modified_flag = True
        while self._modified_flag:
            # Whenever an executability or valueness is modified,
            # _modified_flag is set to true (see set_executability and set_valueness)
            # so that the fixpoint continues.
            self._modified_flag = False
            if debug:
                self.dump()

            # 3. For any executable block B with only one successor C,
            # set executability[B, C] = True
            for B in self._all_blocks:
                if self.is_executable(B) and len(B._out) == 1:
                    C = B._out[0]
                    self.set_executability(B, C)

            for B in self._all_blocks:
                if self.is_executable(B):
                    for ins in B.get_instructions():
                        self.propagate_in(B, ins)

    def propagate_in(self, B: Block, ins: Instruction) -> None:
        """
        Propagate valueness and executability to
        the given instruction ins located in the given executable block B.
        See the 'compute' function for more context.
        """
        raise NotImplementedError()

        # 4. TODO For any executable assignment v <- op (x, y)
        # set valueness[v] = eval (op, x, y)

        # 5. TODO For any executable assignment v <- phi (x1, ..., xn)
        # set valueness[v] = join(x1, .., xn)

        # 6. TODO For any executable conditional branch to blocks B1 and B2,
        # set executability[B1] = True and/or executability[B2] = True
        # depending on the valueness of its condition

    def get_executable_srcs(self, B: Block, phi: PhiNode) -> List[Operand]:
        """
        Returns for a phi node phi belonging to block B its operands
        which come from an executable edge.
        """
        return [x for lbl, x in phi.used().items()
                if x is not None and self.executability[self._function.get_block(lbl), B]]

    def get_operands(self, ins: Instru3A) -> List[LATTICE_VALUE]:
        """
        Returns the valueness of the operands of the given instruction.
        Also takes into account immediate values and the zero register.
        """
        args: List[LATTICE_VALUE] = []
        all_used = ins.args if ins.is_read_only() else ins.args[1:]
        for x in all_used:
            if isinstance(x, Temporary):
                args.append(self.valueness[x])
            elif isinstance(x, Immediate):
                args.append(x._val)
            elif (x == ZERO):
                args.append(0)
            elif isinstance(x, Label):
                continue
            else:
                args.append(Lattice.Top)
        return args

    def eval_arith_instr(self, ins: Instru3A) -> LATTICE_VALUE:
        """
        Computes the result of an arithmetic instruction in the valueness lattice,
        from the valueness of its operands.
        """
        args = self.get_operands(ins)
        name = ins.get_name()

        if has_top(args):
            return Lattice.Top
        elif has_bottom(args):
            return Lattice.Bottom

        args = cast(List[int], args)
        if name == "add" or name == "addi":
            return args[0] + args[1]
        elif name == "mul":
            return args[0] * args[1]
        elif name == "div":
            return div_rd_0(args[0], args[1])
        elif name == "rem":
            return mod_rd_0(args[0], args[1])
        elif name == "not":
            return ~ args[0]
        elif name == "sub":
            return args[0] - args[1]
        elif name == "and":
            return args[0] & args[1]
        elif name == "or":
            return args[0] | args[1]
        elif name == "li":
            assert(isinstance(ins.args[1], Immediate))
            return args[0]
        elif name == "mv":
            return args[0]

        raise MiniCInternalError("Instruction modifying a temporary not in\
                                  ['add', 'addi', 'mul', 'div', 'rem',\
                                  'not', 'sub', 'and', 'or', 'li', 'mv']")

    def eval_bool_instr(self, ins: CondJump) -> LATTICE_VALUE:
        """
        Computes the result of the comparison of a branching instruction
        in the valueness lattice, from the valueness of its operands.
        """
        args = self.get_operands(ins)
        name = ins.get_name()

        if has_top(args):
            return Lattice.Top
        elif has_bottom(args):
            return Lattice.Bottom

        args = cast(List[int], args)
        if name == "blt":
            return args[0] < args[1]
        elif name == "bgt":
            return args[0] > args[1]
        elif name == "beq":
            return args[0] == args[1]
        elif name == "bne":
            return args[0] != args[1]
        elif name == "ble":
            return args[0] <= args[1]
        elif name == "bge":
            return args[0] >= args[1]
        elif name == "beqz":
            return args[0] == 0
        elif name == "bnez":
            return args[0] != 0

        raise MiniCInternalError("Condition of a CondJump not in ['blt',\
                                 'bgt', 'beq', 'bne', 'ble', 'bge',\
                                 'beqz', 'bnez']")

    def replaceInstruction(self, ins: Instru3A) -> List[Instru3A]:
        """
        Replace instructions that have constant operands
        according to the valueness computation.
        """
        # Add some LIs before the instruction and replace the variables
        li_instrs: List[Instru3A] = []
        new_args: List[Operand] = []

        # TODO replace this with something correct
        new_args = ins.args

        new_ins = Instru3A(ins._ins, args=new_args)
        return li_instrs + [new_ins]

    def replacePhi(self, B: Block, ins: PhiNode) -> PhiNode:
        """
        Replace phi nodes that have constant operands
        according to the valueness computation.
        """
        to_remove: List[Label] = []
        for Bi_label, xi in ins.used().items():
            Bi = self._function.get_block(Bi_label)
            if self.executability[Bi, B]:
                if self.is_constant(xi):
                    # Add a LI in the block from where xi comes,
                    # at the end but before the jump,
                    # and replace xi
                    new_xi = self._function.new_tmp()
                    ins._srcs[Bi_label] = new_xi
                    li_ins = Instru3A("li", new_xi, self.valueness[xi])
                    jump = Bi.get_jump()
                    if jump:
                        pos = Bi._listIns.index(jump)
                        Bi.add_instruction(pos, li_ins)
                    else:
                        Bi._listIns.append(li_ins)
            else:
                to_remove.append(Bi_label)
        for Bi_label in to_remove:
            del ins._srcs[Bi_label]
        return ins

    def rewriteCFG(self) -> None:
        """ Update the CFG """
        # a. Whenever valueness[x] = c, substitute c for x and delete assignment to x
        for block in self._all_blocks:
            if self.is_executable(block):
                new_instrs: List[Instruction] = []
                for ins in block._listIns:
                    defs = ins.defined()
                    if len(defs) == 1 and self.is_constant(defs[0]):
                        continue
                    elif isinstance(ins, Instru3A):
                        new_instrs.extend(self.replaceInstruction(ins))
                    elif isinstance(ins, PhiNode):
                        new_instrs.append(self.replacePhi(block, ins))
                    else:
                        new_instrs.append(ins)
                block._listIns = new_instrs
        # b. Whenever executability[B, C] = False, delete this edge
        for (B, C) in [(B, C) for ((B, C), b) in self.executability.items()
                       if not b and B is not None]:
            self._function.remove_edge(B, C)
            jump = B.get_jump()
            if jump:
                B.get_instructions().remove(jump)
        # c. Whenever B is not executable, delete block B
        # There are no edges implicating B, for it would not be executable
        for block in self._all_blocks:
            if not self.is_executable(block):
                del self._function._listBlk[block._label]


def OptimSSA(function: CFG, debug) -> None:
    optim = CondConstantPropagation(function)
    optim.compute(debug)
    optim.rewriteCFG()
