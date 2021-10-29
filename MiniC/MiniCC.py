#! /usr/bin/env python3
"""
Code generation lab, main file. Code Generation with Smart IRs.
Usage:
    python3 MiniCC.py <filename>
    python3 MiniCC.py --help
"""
import traceback
from MiniCLexer import MiniCLexer
from MiniCParser import MiniCParser
from TP04.MiniCCodeGen3AVisitor import MiniCCodeGen3AVisitor
from TP03.MiniCTypingVisitor import MiniCTypingVisitor, MiniCTypeError
from Errors import MiniCUnsupportedError, MiniCInternalError, AllocationError
from TP04.SimpleAllocations import (
    NaiveAllocator, AllInMemAllocator
)
try:  # Common part for TP05 and TP05a
    from TP05.CFG import CFG  # type: ignore[import]
except ModuleNotFoundError:
    pass
try:  # Common part for TP05 and TP05b
    from TP05.SmartAllocation import SmartAllocator  # type: ignore[import]
except ModuleNotFoundError:
    pass
try:  # Liveness for TP05 (M1IF08)
    from TP05.LivenessDataFlow import LivenessDataFlow  # type: ignore[import]
except ModuleNotFoundError:
    pass
try:  # SSA for TP05a (CAP)
    from TP05.SSA import (enter_ssa, exit_ssa)  # type: ignore[import]
except ModuleNotFoundError:
    pass
try:  # Liveness for TP05b (CAP)
    from TP05.LivenessSSA import LivenessSSA  # type: ignore[import]
except ModuleNotFoundError:
    pass

import argparse

from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

import os
import sys


class CountErrorListener(ErrorListener):
    """Count number of errors.

    Parser provides getNumberOfSyntaxErrors(), but the Lexer
    apparently doesn't provide an easy way to know if an error occurred
    after the fact. Do the counting ourserves with a listener.
    """

    def __init__(self):
        super(CountErrorListener, self).__init__()
        self.count = 0

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        self.count += 1


def main(inputname, reg_alloc, enable_ssa=False,
         typecheck=True, typecheck_only=False, stdout=False, output_name=None, debug=False,
         debug_graphs=False, ssa_graphs=False):
    (basename, rest) = os.path.splitext(inputname)
    if not typecheck_only:
        if stdout:
            output_name = None
            print("Code will be generated on standard output")
        elif output_name is None:
            output_name = basename + ".s"
            print("Code will be generated in file " + output_name)

    input_s = FileStream(inputname, encoding='utf-8')
    lexer = MiniCLexer(input_s)
    counter = CountErrorListener()
    lexer._listeners.append(counter)
    stream = CommonTokenStream(lexer)
    parser = MiniCParser(stream)
    parser._listeners.append(counter)
    tree = parser.prog()
    if counter.count > 0:
        exit(3)  # Syntax or lexicography errors occurred, don't try to go further.
    if typecheck:
        typing_visitor = MiniCTypingVisitor()
        try:
            typing_visitor.visit(tree)
        except MiniCTypeError as e:
            print(e.args[0])
            exit(2)

    if typecheck_only:
        if debug:
            print("Not running code generation because of --typecheck-only.")
        return

    # Codegen 3@ CFG Visitor, first argument is debug mode
    visitor3 = MiniCCodeGen3AVisitor(debug, parser)

    # dump generated code on stdout or file.
    with open(output_name, 'w') if output_name else sys.stdout as output:
        visitor3.visit(tree)
        for function in visitor3.get_functions():
            # Allocation part
            cfg = CFG(function)
            if debug_graphs:
                s = "{}.{}.dot".format(basename, cfg._name)
                print("Output", s)
                cfg.print_dot(s)
            if enable_ssa:
                DF = enter_ssa(cfg, basename, debug, ssa_graphs)
                if ssa_graphs:
                    s = "{}.{}.ssa.dot".format(basename, cfg._name)
                    print("Output", s)
                    cfg.print_dot(s, DF, True)
            allocator = None
            if reg_alloc == "naive":
                allocator = NaiveAllocator(cfg)
                comment = "naive allocation"
            elif reg_alloc == "all_in_mem":
                allocator = AllInMemAllocator(cfg)
                comment = "all-in-memory allocation"
            elif reg_alloc == "smart":
                liveness = None
                if enable_ssa:
                    try:
                        liveness = LivenessSSA(cfg, debug=debug)
                    except NameError:
                        form = "CFG in SSA form"
                        raise ValueError("Invalid dataflow form: \
liveness file not found for {}.".format(form))
                else:
                    try:
                        liveness = LivenessDataFlow(cfg, debug=debug)
                    except NameError:
                        form = "CFG not in SSA form"
                        raise ValueError("Invalid dataflow form: \
liveness file not found for {}.".format(form))
                allocator = SmartAllocator(cfg, basename, liveness,
                                           debug, debug_graphs)
                comment = "smart allocation with graph coloring"
            elif reg_alloc == "none":
                comment = "non executable 3-Address instructions"
            else:
                raise ValueError("Invalid allocation strategy:" + reg_alloc)
            if allocator:
                allocator.prepare()
            if enable_ssa:
                exit_ssa(cfg)
                comment += " with SSA"
            if allocator:
                allocator.rewriteCode(cfg)
            if enable_ssa and ssa_graphs:
                s = "{}.{}.exitssa.dot".format(basename, cfg._name)
                print("Output", s)
                cfg.print_dot(s, view=True)
            cfg.print_code(output, comment=comment)
            if debug:
                visitor3.printSymbolTable()


# command line management
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate code for .c file')

    parser.add_argument('filename', type=str,
                        help='Source file.')
    parser.add_argument('--reg-alloc', type=str,
                        choices=['none', 'naive', 'all_in_mem', 'smart'],
                        help='Allocation to perform')
    parser.add_argument('--ssa', action='store_true',
                        default=False,
                        help='Enable SSA form')
    parser.add_argument('--stdout', action='store_true',
                        help='Generate code to stdout')
    parser.add_argument('--debug', action='store_true',
                        default=False,
                        help='Emit verbose debug output')
    parser.add_argument('--graphs', action='store_true',
                        default=False,
                        help='Display graphs (CFG, conflict graph).')
    parser.add_argument('--ssa-graphs', action='store_true',
                        default=False,
                        help='Display SSA graphs (DT, DF).')
    parser.add_argument('--disable-typecheck', action='store_true',
                        default=False,
                        help="Don't run the typechecker before generating code")
    parser.add_argument('--typecheck-only', action='store_true',
                        default=False,
                        help="Run only the typechecker, don't try generating code.")
    parser.add_argument('--output', type=str,
                        help='Generate code to outfile')

    args = parser.parse_args()

    if args.reg_alloc is None and not args.typecheck_only:
        print("error: the following arguments is required: --reg-alloc")
        exit(1)

    try:
        main(args.filename, args.reg_alloc, args.ssa,
             not args.disable_typecheck, args.typecheck_only,
             args.stdout, args.output, args.debug,
             args.graphs, args.ssa_graphs)
    except MiniCUnsupportedError as e:
        print(e)
        exit(5)
    except (MiniCInternalError, AllocationError):
        traceback.print_exc()
        exit(4)
