from MiniCVisitor import MiniCVisitor
from MiniCParser import MiniCParser
from Errors import MiniCInternalError

from enum import Enum


class MiniCTypeError(Exception):
    pass


class BaseType(Enum):
    Float, Integer, Boolean, String = range(4)


# Basic Type Checking for MiniC programs.
class MiniCTypingVisitor(MiniCVisitor):

    def __init__(self):
        self._memorytypes = dict()  # id-> types
        # For now, we don't have real functions ...
        self._current_function = "main"

    def _raise(self, ctx, for_what, *types):
        raise MiniCTypeError(
            'In function {}: Line {} col {}: invalid type for {}: {}'.format(
                self._current_function,
                ctx.start.line, ctx.start.column, for_what,
                ' and '.join(t.name.lower() for t in types)))

    def _raiseMismatch(self, ctx, for_what, *types):
        raise MiniCTypeError(
            'In function {}: Line {} col {}: type mismatch for {}: {}'.format(
                self._current_function,
                ctx.start.line, ctx.start.column, for_what,
                ' and '.join(t.name.lower() for t in types)))

    def _raiseNonType(self, ctx, message):
        raise MiniCTypeError(
            'In function {}: Line {} col {}: {}'.format(
                self._current_function,
                ctx.start.line, ctx.start.column, message))

    # type declaration

    def visitVarDecl(self, ctx):
        raise NotImplementedError()

    def visitBasicType(self, ctx):
        if ctx.mytype.type == MiniCParser.INTTYPE:
            return BaseType.Integer
        elif ctx.mytype.type == MiniCParser.FLOATTYPE:
            return BaseType.Float
        else:  # TODO: same for other types
            raise NotImplementedError()

    def visitIdList(self, ctx):
        raise NotImplementedError()

    def visitIdListBase(self, ctx):
        raise NotImplementedError()

    # typing visitors for expressions, statements !

    # visitors for atoms --> value
    def visitParExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitIntAtom(self, ctx):
        return BaseType.Integer

    def visitFloatAtom(self, ctx):
        return BaseType.Float

    def visitBooleanAtom(self, ctx):
        raise NotImplementedError()

    def visitIdAtom(self, ctx):
        try:
            valtype = self._memorytypes[ctx.getText()]
            return valtype
        except KeyError:
            self._raiseNonType(ctx,
                               "Undefined variable {}".format(ctx.getText()))

    def visitStringAtom(self, ctx):
        return BaseType.String

    # now visit expr

    def visitAtomExpr(self, ctx):
        return self.visit(ctx.atom())

    def visitOrExpr(self, ctx):
        raise NotImplementedError()

    def visitAndExpr(self, ctx):
        raise NotImplementedError()

    def visitEqualityExpr(self, ctx):
        raise NotImplementedError()

    def visitRelationalExpr(self, ctx):
        raise NotImplementedError()

    def visitAdditiveExpr(self, ctx):
        raise NotImplementedError()

    def visitMultiplicativeExpr(self, ctx):
        raise NotImplementedError()

    def visitNotExpr(self, ctx):
        raise NotImplementedError()

    def visitUnaryMinusExpr(self, ctx):
        raise NotImplementedError()

    # visit statements

    def visitPrintlnintStat(self, ctx):
        etype = self.visit(ctx.expr())
        if etype not in (BaseType.Integer, BaseType.Boolean):
            self._raise(ctx, 'println_int statement', etype)

    def visitPrintlnfloatStat(self, ctx):
        etype = self.visit(ctx.expr())
        if etype != BaseType.Float:
            self._raise(ctx, 'println_float statement', etype)

    def visitPrintlnstringStat(self, ctx):
        etype = self.visit(ctx.expr())
        if etype != BaseType.String:
            self._raise(ctx, 'println_string statement', etype)

    def visitAssignStat(self, ctx):
        raise NotImplementedError()

    def visitWhileStat(self, ctx):
        raise NotImplementedError()

    def visitIfStat(self, ctx):
        raise NotImplementedError()
