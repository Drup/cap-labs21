from typing import List
from .Operands import (Operand, Immediate, Renamer, Temporary)

"""
MIF08, CAP, API RiscV. 3A instruction constructors.
"""


def regset_to_string(registerset):
    """Utilitary function: pretty-prints a set of locations."""
    return "{" + ",".join(str(x) for x in registerset) + "}"


class Instruction:

    """Real instruction, comment or label."""
    def __init__(self):
        self._ins = None

    def is_instruction(self):
        """True if the object is a true instruction (not a label or
        comment)."""
        return False

    def is_jump(self):
        """True if the instruction is a jump (conditional or not)."""
        return False

    def is_cond_jump(self):
        """True if the instruction is a jump (conditional or not)."""
        return False

    def is_label(self):
        """True if the instruction is a label."""
        return False

    def defined(self) -> List[Operand]:
        return []

    def used(self) -> List[Operand]:
        return []

    def printIns(self, stream):
        """Print the instruction on the output.
        Should never be called on the base class
        """
        raise NotImplementedError


class Instru3A(Instruction):

    def __init__(self, ins, arg1=None, arg2=None, arg3=None, args=None):
        super().__init__()
        self._ins = ins
        if args:
            self.args = args
        else:
            self.args = [arg for arg in (arg1, arg2, arg3) if arg is not None]
        args = self.args
        for i in range(len(args)):
            if isinstance(args[i], int):
                args[i] = Immediate(args[i])
            assert isinstance(args[i], Operand), (args[i], type(args[i]))

    def is_instruction(self):
        """True if the object is a true instruction (not a label or
        comment)."""
        return True

    def get_name(self):
        # convention is to use lower-case in RISCV, even though not strictly necessary
        return self._ins.lower()

    def is_jump(self):
        """True if the instruction is a jump (conditional or not)."""
        return (self.get_name().startswith("b")
                or self.get_name() == "j")

    def is_cond_jump(self):
        """True if the instruction is a conditional jump."""
        return self.get_name().startswith("b")

    def is_read_only(self):
        """True if the instruction only reads from its operands.

        Otherwise, the first operand is considered as the destination
        and others are source.
        """
        return (self.get_name().startswith("b")
                or self.get_name() == "j"
                or self.get_name() == "ld"
                or self.get_name() == "lw"
                or self.get_name() == "lb")

    def defined(self):
        if self.is_read_only():
            defs = []
        else:
            defs = [self.args[0]]
        return [arg for arg in defs if isinstance(arg, Temporary)]

    def used(self):
        if self.is_read_only():
            uses = self.args
        else:
            uses = self.args[1:]
        return [arg for arg in uses if isinstance(arg, Temporary)]

    def rename(self, renamer: Renamer):
        for i, arg in enumerate(self.args):
            if isinstance(arg, Temporary):
                if i == 0 and not self.is_read_only():
                    new_t = renamer.fresh(arg)
                else:
                    new_t = renamer.replace(arg)
                self.args[i] = new_t

    def __str__(self):
        s = self._ins
        first = True
        for arg in self.args:
            if first:
                s += ' ' + str(arg)
                first = False
            else:
                s += ', ' + str(arg)
        return s

    def printIns(self, stream):
        """Print the instruction on the output."""
        print('       ', str(self), file=stream)

    def unfold(self):
        """Utility function to get both the instruction name and the operands
        in one call. Example:

        ins, args = i.unfold()
        """
        return self.get_name(), self.args

    def label(self):
        """Utility function to find the label of a jump
        Assumes there is only one label!
        """
        labels = [arg for arg in self.args if arg.is_label()]
        assert (len(labels) == 1)
        return labels[0]

    def set_label(self, label):
        """Utility function to replace the label of a jump
        Assumes there is only one label!
        """
        self.args = [label if arg.is_label() else arg for arg in self.args]


class Label(Instruction, Operand):
    """ A label is here a regular instruction"""

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name

    def __str__(self):
        return ("lbl_{}".format(self._name))

    def __repr__(self):
        return ("{}".format(self._name))

    def printIns(self, stream):
        print(str(self) + ':', file=stream)

    def is_label(self):
        """True if the instruction is a label."""
        return True


class Jump(Instru3A):
    """ A Jump is a specific kind of instruction"""

    def __init__(self, label: Label):
        super().__init__("j", label)


class CondJump(Instru3A):
    """ A Conditional Jump is a specific kind of instruction"""

    def __init__(self, ins, op1, op2, label: Label):
        assert(ins.startswith("b"))
        super().__init__(ins, op1, op2, label)


class Comment(Instruction):
    """ A comment is here a regular instruction"""

    def __init__(self, content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = content

    def __str__(self):  # use only for print_dot !
        return "# {}".format(self._content)

    def printIns(self, stream):
        print('        # ' + self._content, file=stream)
