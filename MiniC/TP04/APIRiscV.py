#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Errors import MiniCInternalError
from .Operands import (
    Condition, Immediate, Offset, Temporary,
    TemporaryPool, Function,
    A0,
    ZERO)
from .Instruction3A import (
    Instru3A, Jump, CondJump, Comment, Label
)

"""
MIF08, CAP, CodeGeneration, RiscV API
 Classes for a RiscV program: constructors, allocation, dump.
"""


class LinearCode:
    """Representation of a RiscV program as a list of instructions."""

    def __init__(self, name):
        self._listIns = []
        self._nblabel = -1
        self._dec = 0
        self._pool = TemporaryPool()
        self._name = name
        self._start = None
        self._label_div_by_zero = self.new_label("div_by_zero")
        self._stacksize = 0

    def add_instruction(self, i, link_with_succ=True):
        """Utility function to add an instruction in the program.
        """
        self._listIns.append(i)
        return i

    def iter_instructions(self, f):
        """Iterate over instructions.

        For each real instruction (not label or comment), call f,
        which must return either None or a list of instruction. If it
        returns None, nothing happens. If it returns a list, then the
        instruction is replaced by this list.

        """
        i = 0
        while i < len(self._listIns):
            old_i = self._listIns[i]
            if not old_i.is_instruction():
                i += 1
                continue
            new_i_list = f(old_i)
            if new_i_list is None:
                i += 1
                continue
            del self._listIns[i]
            self._listIns.insert(i, Comment(str(old_i)))
            i += 1
            for new_i in new_i_list:
                self._listIns.insert(i, new_i)
                i += 1
            self._listIns.insert(i, Comment("end " + str(old_i)))
            i += 1

    def get_instructions(self):
        return self._listIns

    def new_tmp(self) -> Temporary:
        """
        Return a new fresh temporary (temp)
        + add in list
        """
        return self._pool.new_tmp()

    def new_offset(self, base):
        """
        Return a new offset in the memory stack
        """
        self._dec = self._dec + 1
        return Offset(base, -8 * self._dec)

    def get_offset(self):
        return self._dec

    def new_name(self, name):
        """
        Return a new label name
        """
        self._nblabel = self._nblabel + 1
        return name + "_" + str(self._nblabel) + "_" + self._name

    def new_label(self, name):
        """Return a new label"""
        return Label(self.new_name(name))

    def get_label_div_by_zero(self):
        return self._label_div_by_zero

    # each instruction has its own "add in list" version
    def add_label(self, s):
        return self.add_instruction(s)

    def add_comment(self, s):
        self.add_instruction(Comment(s))

    def add_instruction_PRINTLN_INT(self, reg):
        """Print integer value, with newline. (see Expand)"""
        # a print instruction generates the temp it prints.
        ins = Instru3A("mv", A0, reg)
        self.add_instruction(ins)
        self.add_instruction_CALL('println_int')

    # Other printing instructions are not implemented.

    def add_instruction_CALL(self, function):
        if isinstance(function, str):
            function = Function(function)
        assert isinstance(function, Function)
        self.add_instruction(Instru3A('call', function))

    # Unconditional jump to label.
    def add_instruction_JUMP(self, label):
        assert isinstance(label, Label)
        i = Jump(label)
        self.add_instruction(i)
        return i

    # Conditional jump
    def add_instruction_cond_JUMP(self, label, op1, c, op2):
        """Add a conditional jump to the code.

        This is a wrapper around bge, bgt, beq, ... c is a Condition, like
        Condition('bgt'), Condition(MiniCParser.EQ), ...
        """
        assert isinstance(label, Label)
        assert isinstance(c, Condition)
        if op2 != 0:
            ins = CondJump(c.__str__(), op1, op2, label)
        else:
            ins = CondJump(c.__str__(), op1, ZERO, label)
        self.add_instruction(ins)
        return ins

    def add_instruction_ADD(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            ins = Instru3A("addi", dr, sr1, sr2orimm7)
        else:
            ins = Instru3A("add", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_MUL(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            raise MiniCInternalError("Cant multiply by an immediate")
        else:
            ins = Instru3A("mul", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_DIV(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            raise MiniCInternalError("Cant divide by an immediate")
        else:
            ins = Instru3A("div", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_REM(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            raise MiniCInternalError("Cant divide by an immediate")
        else:
            ins = Instru3A("rem", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_NOT(self, dr, sr):
        ins = Instru3A("not", dr, sr)
        self.add_instruction(ins)

    def add_instruction_SUB(self, dr, sr1, sr2orimm7):
        assert not isinstance(sr2orimm7, Immediate)
        ins = Instru3A("sub", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_AND(self, dr, sr1, sr2orimm7):
        ins = Instru3A("and", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    def add_instruction_OR(self, dr, sr1, sr2orimm7):
        ins = Instru3A("or", dr, sr1, sr2orimm7)
        self.add_instruction(ins)

    # Copy values (immediate or in register)
    def add_instruction_LI(self, dr, imm7):
        ins = Instru3A("li", dr, imm7)
        self.add_instruction(ins)

    def add_instruction_MV(self, dr, sr):
        ins = Instru3A("mv", dr, sr)
        self.add_instruction(ins)

    def add_instruction_LD(self, dr, mem):
        ins = Instru3A("ld", dr, mem)
        self.add_instruction(ins)

    def add_instruction_SD(self, sr, mem):
        ins = Instru3A("sd", sr, mem)
        self.add_instruction(ins)

    def __str__(self):
        return '\n'.join(map(str, self._listIns))

    def print_code(self, output, comment=None):
        # compute size for the local stack - do not forget to align by 16
        fo = self._stacksize  # allocate enough memory for stack
        cardoffset = 8 * (fo + (0 if fo % 2 == 0 else 1)) + 16
        output.write(
            "##Automatically generated RISCV code, MIF08 & CAP\n")
        if comment is not None:
            output.write("##{} version\n".format(comment))
        output.write("\n\n##prelude\n")
        output.write("""
        .text
        .globl {0}
{0}:
        addi sp, sp, -{1}
        sd ra, 0(sp)
        sd fp, 8(sp)
        addi fp, sp, {1}
        """.format(self._name, cardoffset))
        # Stack in RiscV is managed with SP
        output.write("\n\n##Generated Code\n")
        for i in self._listIns:
            i.printIns(output)
        output.write("\n\n##postlude\n")
        output.write("""
        ld ra, 0(sp)
        ld fp, 8(sp)
        addi sp, sp, {0}
        ret

{1}:
        la a0, {1}_msg
        call println_string
        li a0, 1
        call exit
{1}_msg: .string "Division by 0"

""".format(cardoffset, self._label_div_by_zero))
