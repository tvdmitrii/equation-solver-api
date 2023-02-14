#!/usr/bin/env python

# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# Class-based example contributed to PLY by David McNab
# -----------------------------------------------------------------------------

import sys

from Nodes.BinOp import BinOp
from Nodes.Node import Node
from Nodes.EquationBlock import EquationBlock
from Nodes.Equation import Equation
from Nodes.NumNode import NumNode
from Nodes.VarNode import VarNode
from DataStorage import DataStorage
import math as math

sys.path.insert(0, "../..")

import ply.lex as lex
import ply.yacc as yacc
import os


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = False#kw.get('debug', 0)
        self.names = {}
        self.root = None
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                          1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        # print self.debugfile

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile)

    def parse(self,s):
        yacc.parse(s, debug=False)

    def run(self):
        while True:
            try:
                s = input('parse > ')
            except EOFError:
                break
            if not s:
                continue
            yacc.parse(s)


class Calc(Parser):
    tokens = (
        'NAME', 'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS',
        'LPAREN', 'RPAREN',
        'LSPAREN', 'RSPAREN',
    )

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\^'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LSPAREN = r'\['
    t_RSPAREN = r'\]'

    def t_NUMBER(self, t):
        r'[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
        try:
            t.value = float(t.value)
        except ValueError:
            print("Failed to parse the number: %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        return t

    t_ignore = " \t"

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
       # return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS'),
    )

    def p_equation_block(self, p):
        """
         equation_block : equation
                    | equation_block equation
         """
        if p[1]:
            if len(p) == 2:
                p[0] = [p[1]]
            else:
                p[1].append(p[2])
                p[0] = p[1]

        self.root = p[0]

    def p_equation(self, p):
        """equation : arithmetic_expression EQUALS arithmetic_expression"""
        p[0] = Equation([p[1], p[3]])
        p[0].simplify()
        if not p[0].is_valid:
            self.p_error(p.slice[2])

    def p_arithmetic_expression_binop(self, p):
        """
        arithmetic_expression : arithmetic_expression PLUS arithmetic_expression
                  | arithmetic_expression MINUS arithmetic_expression
                  | arithmetic_expression TIMES arithmetic_expression
                  | arithmetic_expression DIVIDE arithmetic_expression
                  | arithmetic_expression EXP arithmetic_expression
        """
        p[0] = BinOp(p[2], [p[1], p[3]])

    def p_arithmetic_expression_uminus(self, p):
        """arithmetic_expression : MINUS arithmetic_expression %prec UMINUS"""
        p[0] = BinOp("-", [0, p[2]])

    def p_arithmetic_expression_group(self, p):
        """arithmetic_expression : LPAREN arithmetic_expression RPAREN"""
        p[0] = p[2]

    def p_arithmetic_expression_number(self, p):
        """arithmetic_expression : NUMBER"""
        p[0] = NumNode(p[1])

    def p_arithmetic_expression_variable(self, p):
        """arithmetic_expression : variable"""
        p[0] = p[1]

    def p_variable(self, p):
        """
        variable : simple_variable
        """
        p[0] = p[1]

    # def p_array_element(self, p):
    #     'array_element : NAME LSPAREN arithmetic_expression RSPAREN'
    #     p[0] = Node("ARR_ELM", p[1], children=[p[3]])

    def p_simple_variable(self, p):
        """simple_variable : NAME"""
        DataStorage.add(p[1])
        p[0] = VarNode(p[1])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")


if __name__ == '__main__':
    calc = Calc()
    # calc.run()
    s = """M_n = 39870
M_0_E = 28
M_0_VA = 86
wt_frac = 0.129

X_E = ((1 - wt_frac)/M_0_E)/((1 - wt_frac)/M_0_E + wt_frac/M_0_VA)
X_VA = 1 - X_E
M_0_cop = X_E * M_0_E + X_VA * M_0_VA
x_cop = M_n / M_0_cop
"""
    calc.parse(s)

    for item in calc.root:
        print(item.string())

    eb = EquationBlock(calc.root)
    eb.init()
    eb.print()
    #eb.calculate()
    #eb.calc_derivatives()

    #print(eb.f)
    #print(eb.df)
    eb.solve()
    print("Solved: " + str(eb.is_solved))
    print("Message: " + str(eb.message))
    # N = len(calc.root)
    # for i in range(N):
    #     print("[" + str(i+1) + "/" + str(N) + "]")
    #     calc.root[i].simplify()
    #     calc.root[i].find_variables()
    #     print("Is valid equation: " + str(calc.root[i].is_valid))
    #     print("Is assignment: " + str(calc.root[i].is_assignment))
    #     print("Variables: " + str(calc.root[i].variables))
    #     calc.root[i].print()

    for k in DataStorage.variables:
        print("Name: " + str(k))
        var = DataStorage.variables[k]
        print("\tSolved: " + str(var["solved"]))
        print("\tValue: " + str(var["value"]))
    # print(DataStorage.variables)

    test = getattr(math, "sqrt", None)
    if test:
        print(test(4))
    else:
        print("Unknown attribute")