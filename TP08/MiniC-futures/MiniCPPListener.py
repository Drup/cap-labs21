from MiniCListener import MiniCListener

from antlr4.TokenStreamRewriter import TokenStreamRewriter


class MiniCPPListener(MiniCListener):
    def __init__(self, t):
        self.rewriter = TokenStreamRewriter(tokens=t)

    def printrw(self, output):
        output.write(self.rewriter.getText('default', 0, 1000))

    def enterProgRule(self, ctx):
        # adds an include futurelib.h at the beginning of program
        indexprog = ctx.start.tokenIndex
        self.rewriter.insertBeforeIndex(indexprog, '#include \"futurelib.h\"\n')

    def exitFuncDecl(self, ctx):
        # adds a call to freeAllFutures at the end of the body of the main function
        (indexret, endret) = ctx.RETURN().getSourceInterval()
        if (ctx.ID().getText() == "main"):
            self.rewriter.insertBeforeIndex(indexret, 'freeAllFutures();\n')

    def enterAsyncFuncCall(self, ctx):
        # adds a & for getting a function pointer to the asynchronous called function
        indexfunid = ctx.start.tokenIndex  # token of async
        self.rewriter.insertBeforeIndex(indexfunid + 2, '&')
