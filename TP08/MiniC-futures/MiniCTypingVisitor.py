from MiniCVisitor import MiniCVisitor
from MiniCParser import MiniCParser
from Errors import MiniCInternalError

from enum import Enum


class MiniCTypeError(Exception):
    pass


# NEW: ADD FutInteger
class BaseType(Enum):
    Float, Integer, Boolean, String, FutInteger = range(5)


class MiniCTypingVisitor(MiniCVisitor):
    pass
