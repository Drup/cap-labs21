# MiniC Compiler 
LAB5a (Control Flow Graph in SSA Form) & LAB5b (Smart Register Allocation), CAP 2021-22

# Authors

YOUR NAME HERE

# Contents

TODO:
- Did you solve (partly or entirely) the bonus of lab5a? If yes, explain your ideas for question 3.
- Explain any design choices you may have made.
- Do not forget to remove all debug traces from your code!

# Howto
## For lab5a:

`python3 MiniCC.py --reg-alloc none --ssa --ssa-graphs TP05/tests/provided/dataflow/df00.c`:
Launch the compiler and obtain a RISCV code with temp.

`python3 MiniCC.py --reg-alloc all_in_mem --ssa --ssa-graphs TP05/tests/provided/dataflow/df00.c`:
Launch the compiler and obtain an executable RISCV code.

Both generate:
- `TP05/tests/provided/dataflow/df00.main.ssa.DT.dot` the domination tree of the original CFG ;
- `TP05/tests/provided/dataflow/df00.main.ssa.dot` the CFG in SSA form, and its dominance frontiers ;
- `TP05/tests/provided/dataflow/df00.main.exitssa.dot` the CFG after exiting SSA form;

To run the test suite, type `make tests-notsmart` (exercise 4), or `make tests-notsmart SSA=1` (once
you have fully implemented SSA).

## For lab5b:

`python3 MiniCC.py --reg-alloc smart --ssa TP05/tests/provided/dataflow/df04.c`:
Launch the compiler and obtain an executable RISCV code, using SSA and the smart allocator.
Options `--debug`, `--graphs` and `--ssa-graphs` can help you to check your implementation.

`make tests SSA=1` to launch the testsuite with smart code generation.

# Test design 

TODO: give the main objectives of your tests.

# Known bugs

TODO: bugs you could not fix (if any).
