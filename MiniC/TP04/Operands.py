from typing import Dict
from MiniCParser import MiniCParser
from Errors import MiniCInternalError

"""
MIF08, CAP, CodeGeneration, RiscV API
 Classes for data location: temporarys, registers, memory
"""


class Operand():

    def is_label(self):
        """True if the instruction is a label."""
        return False


# signed version for riscv
all_ops = ['blt', 'bgt', 'beq', 'bne', 'ble', 'bge', 'beqz', 'bnez']
opdict = {MiniCParser.LT:   'blt', MiniCParser.GT:   'bgt',
          MiniCParser.LTEQ: 'ble', MiniCParser.GTEQ: 'bge',
          MiniCParser.NEQ:  'bne', MiniCParser.EQ:   'beq'}
opnot_dict = {'bgt': 'ble',
              'bge': 'blt',
              'blt': 'bge',
              'ble': 'bgt',
              'beq': 'bne',
              'bne': 'beq',
              'beqz': 'bnez',
              'bnez': 'beqz'}

# map for register shortcuts
reg_map = dict([(0, 'zero'), (1, 'ra'), (2, 'sp'), (8, 'fp'), (9, 's1')] +
               [(i, 'a'+str(i-10)) for i in range(10, 18)] +
               [(i, 's'+str(i-16)) for i in range(18, 28)] +
               [(i, 't'+str(i-5)) for i in range(5, 8)] +
               [(i, 't'+str(i-25)) for i in range(28, 32)])


class Condition(Operand):
    """Condition, i.e. second operand of the add_instruction_cond_JUMP helper
    method.

    Example usage :
    - Condition('beq') = branch if equal.
    - Condition(MiniCParser.LT) = branch if lower than.
      ...
    The constructor's argument shall be a string in the list all_ops, or a
    comparison operator in MiniCParser.LT, MiniCParser.GT, ... (one of the keys
    in opdict).

    A 'negate' method allows getting the negation of this condition.
    """

    def __init__(self, optype):
        if optype in opdict:
            self._op = opdict[optype]
        elif str(optype) in all_ops:
            self._op = str(optype)
        else:
            raise MiniCInternalError("Unsupported comparison operator %s", optype)

    def negate(self):
        return Condition(opnot_dict[self._op])

    def __str__(self):
        return self._op


class Function(Operand):
    """Operand for build-in function call"""

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name


class DataLocation(Operand):
    """ A Data Location is either a register, a temporary
    or a place in memory (offset)
    """

    def is_temporary(self):
        """True if the location is a temporary, i.e. needs to be replaced
        during code generation.
        """
        return False


class Offset(DataLocation):
    """ Offset = address in memory computed with base + offset
    """

    def __init__(self, basereg, offset):
        super().__init__()
        assert isinstance(offset, int)
        self._offset = offset
        self._basereg = basereg

    def __str__(self):
        return("{}({})".format(self._offset, self._basereg))

    __repr__ = __str__

    def get_offset(self):
        return self._offset


class Register(DataLocation):
    """ A (physical) register
    """

    def __init__(self, number):
        super().__init__()
        self._number = number

    def __str__(self):
        numreg = self._number
        if numreg not in reg_map:
            raise Exception("Register number %d should not be used", numreg)
        else:
            return ("{}".format(reg_map[numreg]))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Register) and self._number == other._number

    def __hash__(self):
        return self._number


class RegisterAdd(DataLocation):
    """ A (physical) special register for addresses
    """

    def __init__(self, number):
        super().__init__()
        self._number = number

    def __str__(self):
        if self._number == 2:
            return "sp"
        else:  # should not happen in RISCV
            return ("blu{}".format(self._number))

    def __repr__(self):
        return self.__str__()


class Immediate(DataLocation):
    """Immediate operand (integer)."""

    def __init__(self, val):
        super().__init__()
        self._val = val

    def __str__(self):
        return str(self._val)


# Shortcuts for registers in RISCV
# Only integer registers
ZERO = Register(0)
RA = Register(1)
SP = Register(2)
FP = Register(8)  # could also be S0
S1 = Register(9)
A = tuple(Register(i + 10) for i in range(8))
S = tuple(Register(i + 8) for i in range(2)) + tuple(Register(i + 18) for i in range(10))
T = tuple(Register(i + 5) for i in range(3)) + tuple(Register(i + 28) for i in range(4))
A0 = A[0]  # function args/return Values : A0,A1
A1 = A[1]
S2 = S[2]
S3 = S[3]
S4 = S[4]

# General purpose registers, usable for the allocator
GP_REGS = S[4:] + T  # s0, ..., s3 are special


class TemporaryPool:
    """Manage a pool of temporaries."""

    _allocation: dict

    def __init__(self):
        self._all_temps = []
        self._current_num = 0

    def add_tmp(self, reg):
        """Add a register to the pool."""
        self._all_temps.append(reg)

    def set_temp_allocation(self, allocation):
        """Give a mapping from temporarys to actual registers. allocation must
        be a dict from Temporary to DataLocation other than
        Temporaries (typically Register or Offset).
        """
        assert isinstance(allocation, dict)
        for k, v in allocation.items():
            assert isinstance(k, Temporary), (
                "Incorrect allocation scheme: key " +
                str(k) + " is not a Temporary.")
            assert not isinstance(v, Temporary), (
                "Incorrect allocation scheme: value " +
                str(v) + " is a Temporary.")
            assert isinstance(v, DataLocation), (
                "Incorrect allocation scheme: value " +
                str(v) + " is not a DataLocation.")

        self._allocation = allocation

    def new_tmp(self):
        """Give a new fresh temporary (temp)"""
        r = Temporary(self._current_num, self)
        self._current_num += 1
        return r

    def get_alloced_loc(self, reg):
        """Get the actual DataLocation allocated for the temporary reg."""
        return self._allocation[reg]


class Temporary(DataLocation):
    """Temporary, are locations that haven't been
    allocated yet. They will later be mapped to physical registers
    (Register) or to a memory location."""

    def __init__(self, number, pool):
        self._number = number
        self._pool = pool
        pool.add_tmp(self)

    def __str__(self):
        return("temp_{}".format(str(self._number)))

    __repr__ = __str__

    def get_alloced_loc(self):
        return self._pool.get_alloced_loc(self)

    def is_temporary(self):
        return True


class Renamer:

    _pool: TemporaryPool
    _env: Dict[Temporary, Temporary]

    def __init__(self, pool):
        self._pool = pool
        self._env = dict()

    def fresh(self, t: Temporary):
        new_t = self._pool.new_tmp()
        self._env[t] = new_t
        return new_t

    def replace(self, t: Temporary):
        return self._env.get(t)

    def copy(self):
        r = Renamer(self._pool)
        r._env = self._env.copy()
        return r
