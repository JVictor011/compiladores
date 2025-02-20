from Consts import Consts
from SemanticVisitor import *

class Grammar:
    def __init__(self, parser):
        self.parser = parser
    def Rule(self):
        return self.GetParserManager().fail(f"{Error.parserError}: Implementar suas regras de producao (Heranca de Grammar)!")
    
    def CurrentToken(self):
        return self.parser.CurrentTok()
    
    def NextToken(self):
        return self.parser.NextTok()
    
    def GetParserManager(self):
        return self.parser.Manager()

    @staticmethod
    def StartSymbol(parser): # Start Symbol S from Grammar G(V, T, S, P)
        resultado = Exp(parser).Rule()
        if parser.CurrentTok().type != Consts.EOF: return resultado.fail(f"{Error.parserError}: Erro sintatico")
        return resultado
    
class Exp(Grammar): # A variable from Grammar G
    def Rule(self):
        ast = self.GetParserManager()
        if self.CurrentToken().matches(Consts.KEY, Consts.LET):
            self.NextToken()
            if self.CurrentToken().type != Consts.ID:
                return ast.fail(f"{Error.parserError}: Esperado '{Consts.ID}'")
            varName = self.CurrentToken()
            self.NextToken()
            if self.CurrentToken().type != Consts.EQ:
                return ast.fail(f"{Error.parserError}: Esperado '{Consts.EQ}'")
            return self.varAssign(ast, varName)
        
        if (self.CurrentToken().type == Consts.ID):
            if (self.parser.Lookahead(1).type == Consts.EQ):
                varName = self.CurrentToken()
                self.NextToken()
                return self.varAssign(ast, varName)
        node = ast.registry(NoOpBinaria.Perform(Term(self.parser), (Consts.PLUS, Consts.MINUS)))
        if ast.error:
            return ast.fail(f"{Error.parserError}: Esperado a '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.LET}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}'")
        return ast.success(node)

    def varAssign(self, ast, varName):
        self.NextToken()
        expr = ast.registry(Exp(self.parser).Rule())
        if ast.error: return ast
        return ast.success(NoVarAssign(varName, expr))
    
class Term(Grammar): # A variable from Grammar G
    def Rule(self):
        return NoOpBinaria.Perform(Factor(self.parser), (Consts.MUL, Consts.DIV))

class Factor(Grammar): # A variable from Grammar G
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()

        if tok.type in (Consts.PLUS, Consts.MINUS):
            self.NextToken()
            factor = ast.registry(Factor(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoOpUnaria(tok, factor))
        return Pow(self.parser).Rule()

class Pow(Grammar): # A variable from Grammar G
    def Rule(self):
        return NoOpBinaria.Perform(Atom(self.parser), (Consts.POW, ), Factor(self.parser))
    
class Atom(Grammar): # A variable from Grammar G
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()
        if tok.type in (Consts.INT, Consts.FLOAT):
            self.NextToken()
            return ast.success(NoNumber(tok))
        elif tok.type == Consts.ID:
            self.NextToken()
            return ast.success(NoVarAccess(tok))
        elif(tok.type == Consts.STRING):
            self.NextToken()
            return ast.success(NoString(tok))
        elif tok.type in (Consts.TRUE, Consts.FALSE):
            self.NextToken()
            return ast.success(NoBoolean(tok))
        ##############################
        elif tok.type == Consts.LSQUARE:
            listExp = ast.registry(ListExp(self.parser).Rule())
            if (ast.error!=None): return ast
            return ast.success(listExp)
        ##############################
        elif tok.type == Consts.LPAR:
            tupleExp = ast.registry(TupleExp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(tupleExp)
            
        return ast.fail(f"{Error.parserError}: Esperado por '{Consts.INT}', '{Consts.FLOAT}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}'")

##############################
class ListExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        elementNodes = []
        self.NextToken()

        if (self.CurrentToken().type == Consts.RSQUARE): # TList vazia
            self.NextToken()
        else:
            elementNodes.append(ast.registry(Exp(self.parser).Rule()))
            if (ast.error!=None):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.RSQUARE}', '{Consts.KEYS[Consts.LET]}', '{Consts.INT}', '{Consts.FLOAT}', '{Consts.ID}', '{Consts.PLUS}', '{Consts.MINUS}', '{Consts.LPAR}', '{Consts.LSQUARE}'")
            
            while (self.CurrentToken().type == Consts.COMMA):
                self.NextToken()

                elementNodes.append(ast.registry(Exp(self.parser).Rule()))
                if (ast.error!=None): return ast

            if (self.CurrentToken().type != Consts.RSQUARE):
                return ast.fail(f"{Error.parserError}: Esperando por '{Consts.COMMA}' ou '{Consts.RSQUARE}'")
            self.NextToken()
        
        return ast.success(NoList(elementNodes))

class TupleExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        elements = []
        self.NextToken()

        elements.append(ast.registry(Exp(self.parser).Rule()))
        if ast.error:
            return ast.fail(f"{Error.parserError}: Expressão inválida na tupla.")

        if self.CurrentToken().type != Consts.COMMA:
            return ast.fail(f"{Error.parserError}: As tuplas requerem pelo menos uma vírgula.")

        while self.CurrentToken().type == Consts.COMMA:
            self.NextToken()
            elements.append(ast.registry(Exp(self.parser).Rule()))
            if ast.error:
                return ast

        if self.CurrentToken().type != Consts.RPAR:
            return ast.fail(f"{Error.parserError}: Esperado ')' no final da tupla.")
        
        self.NextToken()
        
        return ast.success(NoTuple(elements))
