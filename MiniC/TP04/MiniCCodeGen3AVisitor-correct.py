from typing import List, Tuple
from MiniCVisitor import MiniCVisitor
from MiniCParser import MiniCParser
from .APIRiscV import (LinearCode, Condition)
from . import Operands
from antlr4.tree.Trees import Trees
from Errors import MiniCInternalError, MiniCUnsupportedError

"""
CAP, MIF08, three-address code generation + simple alloc
This visitor constructs an object of type "LinearCode".
"""


class MiniCCodeGen3AVisitor(MiniCVisitor):

    _current_function: LinearCode

    def __init__(self, debug, parser):
        super().__init__()
        self._parser = parser
        self._debug = debug
        self._functions = []
        self._lastlabel = ""

    def get_functions(self):
        return self._functions

    def printSymbolTable(self):  # pragma: no cover
        print("--variables to temporaries map--")
        for keys, values in self._symbol_table.items():
            print(keys + '-->' + str(values))

    # handle variable decl

    def visitVarDecl(self, ctx) -> None:
        type_str = ctx.typee().getText()
        vars_l = self.visit(ctx.id_l())
        for name in vars_l:
            if name in self._symbol_table:
                raise MiniCInternalError(
                    "Variable {} has already been declared".format(name))
            else:
                tmp = self._current_function.new_tmp()
                self._symbol_table[name] = tmp
                if type_str not in ("int", "bool"):
                    raise MiniCUnsupportedError("Unsupported type " + type_str)
                # Initialization to 0 or False, both represented with 0
                self._current_function.add_instruction_LI(tmp, 0)

    def visitIdList(self, ctx) -> Operands.Temporary:
        t = self.visit(ctx.id_l())
        t.append(ctx.ID().getText())
        return t

    def visitIdListBase(self, ctx) -> List[str]:
        return [ctx.ID().getText()]

    # expressions

    def visitParExpr(self, ctx) -> Operands.Temporary:
        return self.visit(ctx.expr())

    def visitIntAtom(self, ctx) -> Operands.Temporary:
        val = int(ctx.getText())
        dest_temp = self._current_function.new_tmp()
        self._current_function.add_instruction_LI(dest_temp, val)
        return dest_temp

    def visitFloatAtom(self, ctx) -> Operands.Temporary:
        raise MiniCUnsupportedError("float literal")

    def visitBooleanAtom(self, ctx) -> Operands.Temporary:
        # true is 1 false is 0
        b = ctx.getText()
        dest_temp = self._current_function.new_tmp()
        if b == 'true':
            val = 1
        else:
            val = 0
        self._current_function.add_instruction_LI(dest_temp, val)
        return dest_temp

    def visitIdAtom(self, ctx) -> Operands.Temporary:
        try:
            # get the temporary associated to id
            return self._symbol_table[ctx.getText()]
        except KeyError:  # pragma: no cover
            raise MiniCInternalError(
                "Undefined variable {}, this should have failed to typecheck."
                .format(ctx.getText())
            )

    def visitStringAtom(self, ctx) -> Operands.Temporary:
        raise MiniCUnsupportedError("string atom")

    # now visit expressions

    def visitAtomExpr(self, ctx) -> Operands.Temporary:
        return self.visit(ctx.atom())

    def visitAdditiveExpr(self, ctx) -> Operands.Temporary:
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        dest_temp = self._current_function.new_tmp()
        if ctx.myop.type == MiniCParser.PLUS:
            self._current_function.add_instruction_ADD(dest_temp, tmpl, tmpr)
        else:
            self._current_function.add_instruction_SUB(dest_temp, tmpl, tmpr)
        return dest_temp

    def visitOrExpr(self, ctx) -> Operands.Temporary:
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        dest_temp = self._current_function.new_tmp()
        self._current_function.add_instruction_OR(dest_temp, tmpl, tmpr)
        return dest_temp

    def visitAndExpr(self, ctx) -> Operands.Temporary:
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        dest_temp = self._current_function.new_tmp()
        self._current_function.add_instruction_AND(dest_temp, tmpl, tmpr)
        return dest_temp

    def visitEqualityExpr(self, ctx) -> Operands.Temporary:
        return self.visitRelationalExpr(ctx)

    def visitRelationalExpr(self, ctx) -> Operands.Temporary:
        c = Condition(ctx.myop.type)
        if self._debug:
            print("relational expression:")
            print(Trees.toStringTree(ctx, None, self._parser))
            print("Condition:", c)
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        dest = self._current_function.new_tmp()
        end_relational = self._current_function.new_label('end_relational')
        self._current_function.add_instruction_LI(dest, 0)
        self._current_function.add_instruction_cond_JUMP(
            end_relational, tmpl, c.negate(), tmpr)
        self._current_function.add_instruction_LI(dest, 1)
        self._current_function.add_label(end_relational)
        return dest

    def visitMultiplicativeExpr(self, ctx) -> Operands.Temporary:
        div_by_zero_lbl = self._current_function.get_label_div_by_zero()
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        dest_temp = self._current_function.new_tmp()
        if ctx.myop.type == MiniCParser.MULT:
            self._current_function.add_instruction_MUL(dest_temp, tmpl, tmpr)
        elif ctx.myop.type == MiniCParser.DIV:
            self._current_function.add_instruction_cond_JUMP(
                div_by_zero_lbl, tmpr, Condition("beq"), 0)
            self._current_function.add_instruction_DIV(dest_temp, tmpl, tmpr)
        elif ctx.myop.type == MiniCParser.MOD:
            self._current_function.add_instruction_cond_JUMP(
                div_by_zero_lbl, tmpr, Condition("beq"), 0)
            self._current_function.add_instruction_REM(dest_temp, tmpl, tmpr)
        else:
            raise MiniCInternalError("Multiplicative expr, but not MUL|DIV|MOD?")
        return dest_temp

    def visitNotExpr(self, ctx) -> Operands.Temporary:
        temp = self.visit(ctx.expr())
        dest_temp = self._current_function.new_tmp()
        # there is no boolean not :-(
        labelneg = self._current_function.new_label("cond_neg")
        labelend = self._current_function.new_label("cond_end")
        self._current_function.add_instruction_cond_JUMP(
            labelneg, temp,
            Condition("beq"), 0)
        self._current_function.add_instruction_LI(dest_temp, 0)
        self._current_function.add_instruction_JUMP(labelend)
        self._current_function.add_label(labelneg)
        self._current_function.add_instruction_LI(dest_temp, 1)
        self._current_function.add_label(labelend)
        return dest_temp

    def visitUnaryMinusExpr(self, ctx) -> Operands.Temporary:
        tmp = self.visit(ctx.expr())
        dest_temp = self._current_function.new_tmp()
        self._current_function.add_instruction_SUB(dest_temp, Operands.ZERO, tmp)
        return dest_temp

    def visitProgRule(self, ctx) -> None:
        self.visitChildren(ctx)

    def visitFuncDecl(self, ctx) -> None:
        funcname = ctx.ID().getText()
        self._current_function = LinearCode(funcname)
        self._symbol_table = dict()

        self.visit(ctx.vardecl_l())
        self.visit(ctx.block())
        self._current_function.add_comment("Return at end of function:")
        # This skeleton doesn't deal properly with functions, and
        # hardcodes a "return 0;" at the end of function. Generate
        # code for this "return 0;".
        self._current_function.add_instruction_LI(Operands.A0, 0)
        self._functions.append(self._current_function)
        del self._current_function

    def visitAssignStat(self, ctx) -> None:
        if self._debug:
            print("assign statement, rightexpression is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
        expr_temp = self.visit(ctx.expr())
        name = ctx.ID().getText()
        self._current_function.add_instruction_MV(self._symbol_table[name], expr_temp)

    def visitIfStat(self, ctx) -> None:
        if self._debug:
            print("if statement")
        end_if_label = self._current_function.new_label("end_if")
        else_label = self._current_function.new_label('else')
        cond = self.visit(ctx.expr())
        self._current_function.add_instruction_cond_JUMP(else_label, cond,
                                                         Condition("beq"), 0)
        self.visit(ctx.then_block)
        self._current_function.add_instruction_JUMP(end_if_label)
        self._current_function.add_label(else_label)
        if ctx.else_block is not None:
            if self._debug:
                print("else  ")
            self.visit(ctx.else_block)
        self._current_function.add_label(end_if_label)

    def visitWhileStat(self, ctx) -> None:
        if self._debug:
            print("while statement, condition is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
            print("and block is:")
            print(Trees.toStringTree(ctx.stat_block(), None, self._parser))
        labelbegin = self._current_function.new_label("begin_while")
        labelend = self._current_function.new_label("end_while")
        self._current_function.add_label(labelbegin)
        cond_temp = self.visit(ctx.expr())
        self._current_function.add_instruction_cond_JUMP(labelend, cond_temp,
                                                         Condition("beq"), 0)
        self.visit(ctx.stat_block())
        self._current_function.add_instruction_JUMP(labelbegin)
        self._current_function.add_label(labelend)
    # visit statements

    def visitPrintlnintStat(self, ctx) -> None:
        expr_loc = self.visit(ctx.expr())
        if self._debug:
            print("print_int statement, expression is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
        self._current_function.add_instruction_PRINTLN_INT(expr_loc)

    def visitPrintlnfloatStat(self, ctx) -> None:
        raise MiniCUnsupportedError("Unsupported type float")

    def visitPrintlnstringStat(self, ctx) -> None:
        raise MiniCUnsupportedError("Unsupported type string")

    def visitStatList(self, ctx) -> None:
        for stat in ctx.stat():
            self._current_function.add_comment(Trees.toStringTree(stat, None, self._parser))
            self.visit(stat)

    def visitForForStat(self, ctx) -> None:
        raise NotImplementedError("fortran for")  # pragma: no cover

    def visitForCStat(self, ctx) -> None:
        raise NotImplementedError("C for")  # pragma: no cover

    def visitArrayAllocExpr(self, ctx) -> None:
        raise NotImplementedError("array")  # pragma: no cover

    def visitArrayReadExpr(self, ctx) -> None:
        raise NotImplementedError("array")  # pragma: no cover

    def visitArrayWriteStat(self, ctx) -> None:
        raise NotImplementedError("array")  # pragma: no cover

    def visitArrayType(self, ctx) -> None:
        raise NotImplementedError("array")  # pragma: no cover
