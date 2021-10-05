# MiniC Compiler 
LAB4 (simple code generation), MIF08 / CAP 2021-22

# Authors

YOUR NAME HERE

# Contents

TODO for STUDENTS : Say a bit about the code infrastructure ...

# Howto

`python3 MiniCC.py TP04/tests/provided/step1/test00.c --reg-alloc=naive`: launch the compiler and obtain a RISCV code with temp.

`make TEST_FILES="TP04/tests/provided/step1/*.c" tests-naive`: check expected and compile with the naive allocation.

`make TEST_FILES="TP04/tests/provided/step1/*.c" tests-notsmart`: check expected and compile with the naive allocation and the all in memory allocation.

# Test design 

TODO: explain your tests

# Design choices

TODO: explain your choices

# Known bugs

TODO: Bugs and limitations.

# Checklists

A check ([X]) means that the feature is implemented 
and *tested* with appropriate test cases.

## Code generation

- [ ] Number Atom 
- [ ] Boolean Atom
- [ ] Id Atom 
- [ ] Additive expression
- [ ] Multiplicative expr
- [ ] UnaryMinus expr
- [ ] Or expression
- [ ] And expression
- [ ] Equality expression
- [ ] Relational expression (! many cases -> many tests)
- [ ] Not expression

## Statements

- [ ] Prog, assignements
- [ ] While
- [ ] Cond Block
- [ ] If
- [ ] Nested ifs
- [ ] Nested whiles

## Allocation

- [ ] Naive allocation
- [ ] All in memory allocation
- [ ] Massive tests of memory allocation

