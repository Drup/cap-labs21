# MiniC Compiler 
LAB5 (Control Flow Graph in SSA Form), CAP 2021-22

# Authors

YOUR NAME HERE

# Contents

TODO: did you solve (partly or entirely) the bonus ? Explain your ideas for question 3.

# Howto

`python3 MiniCC.py --reg-alloc none --ssa --ssa-graphs TP05/tests/provided/dataflow/df00.c`:
Launch the compiler and obtain a RISCV code with temp.

`python3 MiniCC.py --reg-alloc all_in_mem --ssa --ssa-graphs TP05/tests/provided/dataflow/df00.c`:
Launch the compiler and obtain an executable RISCV code.

Both generate:
- `TP05/tests/provided/dataflow/df00.main.ssa.DT.dot` the domination tree of the original CFG ;
- `TP05/tests/provided/dataflow/df00.main.ssa.dot` the CFG in SSA form, and its dominance frontiers ;
- `TP05/tests/provided/dataflow/df00.main.exitssa.dot` the CFG after exiting SSA form;

# Test design 

TODO: give the main objectives of your tests.

# Known bugs

TODO: bugs you could not fix (if any).
