"""
CAP, CodeGeneration, CFG API
Classes for a RiscV CFG: constructors, allocation, dump.
"""

import networkx as nx
import graphviz as gz

from typing import Union, Any, Dict, List, Set, cast

from TP04.APIRiscV import LinearCode
from TP04.Operands import (
    Immediate, Offset, Temporary, Function, A0, S, T)
from TP04.Instruction3A import (
    regset_to_string, Instruction,
    Instru3A, Jump, CondJump, Comment, Label
)


class Block:

    def __init__(self, label, insts):
        self._label: Label = label
        self._listIns: List[Instruction] = insts
        self._in: List[Block] = []
        self._out: List[Block] = []
        self._gen = set()
        self._kill = set()

    def __str__(self):
        instr = [i for i in self._listIns if not isinstance(i, Comment)]
        instr_str = '\n'.join(map(str, instr))
        s = '{}\n\n{}'.format(self._label, instr_str)
        return s

    def __repr__(self):
        return str(self._label)

    def get_instructions(self) -> List[Instruction]:
        return self._listIns

    def get_label(self) -> Label:
        return self._label

    def get_jump(self) -> Union[Jump, CondJump, None]:
        # Get rid of comments
        instr = [i for i in self.get_instructions() if i.is_instruction()]
        if instr:
            j = instr[-1]
            if j.is_jump():
                return cast(Union[Jump, CondJump], j)
            else:
                return None
        else:
            return None

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

    def set_gen_kill(self):
        gen = set()
        kill = set()
        for i in self.get_instructions():
            if i.is_instruction():
                # Reminder: '|' is set union, '-' is subtraction.
                kill = kill | set(i.defined())
                gen = (gen | set(i.used())) - kill
        self._gen = gen
        self._kill = kill

    def print_gen_kill(self, i):  # pragma: no cover
        print("block " + str(self._label), ":", i)
        print("gen: " + regset_to_string(self._gen))
        print("kill: " + regset_to_string(self._kill) + "\n")

    def add_instruction(self, pos, instr):
        self._listIns.insert(pos, instr)


class CFG:

    _start: Label
    _listBlk: Dict[Label, Block]

    def __init__(self, function):
        self._listBlk = {}
        self._dec = function._dec
        self._nblabel = function._nblabel
        self._pool = function._pool
        self._stacksize = 0
        self._name = function._name
        self._init_blks(function._label_div_by_zero)
        self._add_blocks(function)
        self._end: Label = self.new_label("end")

    def _init_blks(self, label_div_by_zero):
        label_div_by_zero_msg = Label(label_div_by_zero._name + "_msg")
        blk = Block(label_div_by_zero, [
            Instru3A("la", A0, label_div_by_zero_msg),
            Instru3A("call", Function("println_string")),
            Instru3A("li", A0, Immediate(1)),
            Instru3A("call", Function("exit")),
        ])
        blk_msg = Block(label_div_by_zero_msg, [
            Instru3A(".string", Function('"Division by 0"'))
        ])
        self.add_block(blk)
        self.add_block(blk_msg)
        self.add_edge(blk, blk_msg)

    """
    Find the leaders in the given list of instructions as linear code.
    Returns a list of indices in the instruction list whose first is 0 and
    last is len(instructions)
    """
    def _find_leaders(self, instructions: List[Instruction]):
        leaders: List[int] = [0]
        # TODO fill leaders
        if len(instructions) not in leaders:
            leaders.append(len(instructions))
        return leaders

    """Extract the blocks from the linear code and add them to the CFG"""
    def _add_blocks(self, linCode: LinearCode):
        # 1. Identify Leaders
        instructions = linCode.get_instructions()
        leaders = self._find_leaders(instructions)
        # 2 Extract Blocks
        blocks: List[Block] = []
        for i in range(0, len(leaders)-1):
            start = leaders[i]
            end = leaders[i+1]
            maybe_label = instructions[start]
            if isinstance(maybe_label, Label):
                block_instrs = instructions[start+1:end]
                label = maybe_label
            else:
                block_instrs = instructions[start:end]
                label = linCode.new_label(linCode._name)
            block = Block(label, block_instrs)
            self.add_block(block)
            blocks.append(block)
        # 2. Add the links and missing jumps
        prev_block = None
        for block in reversed(blocks):
            label = block._label
            instructions = block.get_instructions()
            jump = block.get_jump()
            dests = []
            if jump:
                dests.append(self.get_block(jump.label()))
                if jump.is_cond_jump() and prev_block is not None:
                    dests.append(prev_block)
            else:
                if prev_block is not None:
                    dests.append(prev_block)
            for dest in dests:
                self.add_edge(block, dest)
            prev_block = block
        self._start = blocks[0]._label

    def add_block(self, blk: Block):
        """Add a new block"""
        self._listBlk[blk._label] = blk

    def get_block(self, name: Label):
        """Return the block with label `name`"""
        return self._listBlk[name]

    def get_blocks(self) -> List[Block]:
        """Return all the blocks"""
        return [b for (_, b) in self._listBlk.items()]

    def get_entries(self) -> List[Block]:
        """Return all the blocks with no predecessors"""
        return [b for (_, b) in self._listBlk.items() if not b._in]

    def add_edge(self, src: Block, dest: Block) -> None:
        """Add edge src -> dest in the control flow graph"""
        dest._in.append(src)
        src._out.append(dest)

    def remove_edge(self, src: Block, dest: Block) -> None:
        """Remove edge src -> dest in the control flow graph"""
        dest._in.remove(src)
        src._out.remove(dest)

    def gather_defs(self) -> Dict[Any, Set[Block]]:
        """
        Return a dictionnary associating variables to all the blocks
        containing one of their definition
        """
        defs: Dict[Any, Set[Block]] = dict()
        for b in self.get_blocks():
            for i in b.get_instructions():
                for v in i.defined():
                    if v not in defs:
                        defs[v] = {b}
                    else:
                        defs[v].add(b)
        return defs

    def new_name(self, name):
        """
        Return a new label name
        """
        self._nblabel = self._nblabel + 1
        return name + "_" + str(self._nblabel) + "_" + self._name

    def new_label(self, name):
        """Return a new label"""
        return Label(self.new_name(name))

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

    def get_stacksize(self):
        return self._stacksize

    def iter_instructions(self, f):
        for b in self.get_blocks():
            b.iter_instructions(f)

    def ordered_blocks_list(self) -> List[Block]:
        """
        Compute a list of blocks with optimized ordering for linearization.
        """
        # TODO bonus question 3
        return list(self._listBlk.values())

    def linearize(self) -> List[Instruction]:
        """
        Linearize the control flow graph as a list of instructions
        """
        # TODO bonus question 2
        l: List[Instruction] = []
        blocks: List[Block] = self.ordered_blocks_list()
        for j, block in enumerate(blocks):
            label = block._label
            l.append(label)
            for i in block._listIns:
                l.append(i)
            if len(block._out) == 0:
                l.append(Jump(self._end))
            else:
                jump = block.get_jump()
                if jump:
                    if jump.is_cond_jump():
                        # In case of conditional jump, add the missing edge
                        other_label = [d._label for d in block._out]
                        other_label.remove(jump.label())
                        assert (len(other_label) == 1)
                        l.append(Jump(other_label[0]))
                else:
                    # Add missing absolute Jump
                    assert(len(block._out) == 1)
                    l.append(Jump(block._out[0]._label))
        return l

    def print_code(self, output, comment=None):
        # compute size for the local stack - do not forget to align by 16
        fo = self.get_stacksize()  # allocate enough memory for stack
        cardoffset = 8 * (fo + (0 if fo % 2 == 0 else 1)) + 16
        output.write(
            "##Automatically generated RISCV code, MIF08 & CAP\n")
        if comment is not None:
            output.write("## {}\n".format(comment))
        output.write("\n\n##prelude\n")
        output.write("""
        .text
        .globl {0}
{0}:
        addi sp, sp, -{1}
        sd ra, 0(sp)
        sd fp, 8(sp)
        addi fp, sp, {1}
        j {2}
        """.format(self._name, cardoffset, self._start))
        # Stack in RiscV is managed with SP
        output.write("\n\n##Generated Code\n")
        for i in self.linearize():
            i.printIns(output)
        output.write("\n\n##postlude\n")
        output.write("""
{1}:
        ld ra, 0(sp)
        ld fp, 8(sp)
        addi sp, sp, {0}
        ret
        """.format(cardoffset, self._end))

    def print_dot(self, filename, DF=None, view=False):  # pragma: no cover
        graph = nx.DiGraph()
        # nodes
        for name, blk in self._listBlk.items():
            if DF is not None:
                print(str(name), blk._label)
                df_str = "{}" if blk not in DF or not len(DF[blk]) else str(DF[blk])
                graph.add_node(blk._label, label=str(blk) +
                               "\n\nDominance frontier:\n" + df_str, shape='rectangle')
            else:
                graph.add_node(blk._label, label=str(blk), shape='rectangle')
        # edges
        for name, blk in self._listBlk.items():
            for child in blk._out:
                graph.add_edge(blk._label, child._label)
        graph.graph['graph'] = dict()
        graph.graph['graph']['overlap'] = 'false'
        nx.drawing.nx_agraph.write_dot(graph, filename)
        gz.render('dot', 'pdf', filename)
        if view:
            gz.view(filename + '.pdf')
