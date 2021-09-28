from MiniCLexer import MiniCLexer
from MiniCParser import MiniCParser
from TP03.MiniCInterpretVisitor import MiniCInterpretVisitor
from Errors import MiniCRuntimeError, MiniCInternalError
from TP03.MiniCTypingVisitor import MiniCTypingVisitor, MiniCTypeError
import sys

import argparse
import antlr4
from antlr4.error.ErrorListener import ErrorListener


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


enable_typing = False


def main():
    # command line
    parser = argparse.ArgumentParser(description='Exec/Type mu files.')
    parser.add_argument('path', type=str,
                        help='file to exec and type')
    args = parser.parse_args()

    # lex and parse
    input_s = antlr4.FileStream(args.path, encoding='utf8')
    lexer = MiniCLexer(input_s)
    counter = CountErrorListener()
    lexer._listeners.append(counter)
    stream = antlr4.CommonTokenStream(lexer)
    parser = MiniCParser(stream)
    parser._listeners.append(counter)
    tree = parser.prog()
    if counter.count > 0:
        exit(3)  # Syntax or lexicography errors occurred

    # typing Visitor
    if enable_typing:
        typing_visitor = MiniCTypingVisitor()
        try:
            typing_visitor.visit(tree)
        except MiniCTypeError as e:
            print(e.args[0])
            exit(2)

    # interpret Visitor
    interpreter_visitor = MiniCInterpretVisitor()
    try:
        interpreter_visitor.visit(tree)
    except MiniCRuntimeError as e:
        print(e.args[0])
        exit(1)
    except MiniCInternalError as e:
        print(e.args[0], file=sys.stderr)
        exit(4)


if __name__ == '__main__':
    main()
