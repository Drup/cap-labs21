from typing import Union
from typing import List

# Union[int, float] means ``either an int or a float''.
NUMBER = Union[int, float]


def add_numbers(a: NUMBER, b: NUMBER) -> NUMBER:
    return a + b


# Both int and floats can be passed to the function
print(add_numbers(1, 4.3))


def divide_numbers(a: NUMBER, b: NUMBER) -> float:
    return a / b


print(divide_numbers(1, 2))

# Declare the type of a list whose elements are numbers.
LIST_OF_NUMBERS = List[NUMBER]


def increment(a: LIST_OF_NUMBERS) -> LIST_OF_NUMBERS:
    return [x + 1 for x in a]


print(increment([1, 2, 3]))

# The type DEEP_LIST_OF_NUMBERS is a special case since it references itself.
# The identifier DEEP_LIST_OF_NUMBERS cannot be used before the end of its
# initialization, but the circular dependency can be broken using the string
# 'DEEP_LIST_OF_NUMBERS' instead.
DEEP_LIST_OF_NUMBERS = Union[NUMBER, List['DEEP_LIST_OF_NUMBERS']]


def deep_increment(d: DEEP_LIST_OF_NUMBERS) -> DEEP_LIST_OF_NUMBERS:
    if d == []:
        return []
    elif isinstance(d, list):
        # Note the unusual typing rule applied by Pyright here: because we are
        # in the 'if' branch, it knows that d is a list, and accepts to iterate
        # over it.
        return [deep_increment(e) for e in d]
    else:
        # ... and here, in the 'else' branch Pyright knows that d is not a list,
        # and can deduce that it is a NUMBER.
        return d + 1


print(deep_increment([1, [2, 3]]))
