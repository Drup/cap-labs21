#! /usr/bin/env python3
"""
Usage:
    python3 arit2.py <filename>
"""
# Main file for MIF08 - Lab03 - 2018, changed in 2020

from Arit2Lexer import Arit2Lexer
from Arit2Parser import Arit2Parser, UnknownIdentifier, DivByZero
from antlr4 import FileStream, CommonTokenStream, StdinStream

import argparse


def main(inputname, debug):
    if inputname is None:
        lexer = Arit2Lexer(StdinStream())
    else:
        lexer = Arit2Lexer(FileStream(inputname))
    stream = CommonTokenStream(lexer)
    parser = Arit2Parser(stream)
    try:
        tree = parser.prog()
        if debug:
            print(tree.toStringTree(tree, parser))
    except UnknownIdentifier as exc:  # Parser's exception
        print('{} is undefined'.format(exc.args[0]))
        exit(1)
    except DivByZero:
        print('Division by zero')
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AritEval lab')
    parser.add_argument('filename', type=str, nargs='?', help='Source file.')
    parser.add_argument('--debug', default=False, action='store_true',
                        help="Print parse tree in Lisp format")
    args = parser.parse_args()
    main(args.filename, args.debug)
