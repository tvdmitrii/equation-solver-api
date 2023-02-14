from pyparsing import *
import numpy as np
import operator
from Expression import *
from Function import *
from SolutionException import *
from MultiAssignExpression import MultiAssignExpression

def reconstruct_string(toks):
    result = ""
    for tok in toks:
        if type(tok) is str:
            result += tok + " "
        if type(tok) is tuple:
            result += tok[0]
        if type(tok) is ParseResults:
            result += reconstruct_string(tok)

    return result


def replace_pi(toks):
    toks[0] = str(np.pi)


def replace_e(toks):
    toks[0] = str(np.e)


def collapse_curly_brackets(input):
    output = []
    indent = 0
    i = -1
    for line in input:
        line = line.strip()
        if not line:
            continue

        if indent == 0:
            output.append(line)
            i += 1
        else:
            output[i] += " " + line

        if "{" in line:
            indent += 1
        if "}" in line:
            indent -= 1

    return output


class Grammar:

    def evaluate_stack_old(self, s):
        # print(s)
        op, num_args = s.pop(), 0
        if isinstance(op, tuple):
            op, num_args = op
        if op == "unary -":
            return -self.evaluate_stack(s)
        if op in "+-*/^":
            # note: operands are pushed onto the stack in reverse order
            op2 = self.evaluate_stack(s)
            op1 = self.evaluate_stack(s)
            return self.opn[op](op1, op2)
        elif op in self.fn:
            # note: args are pushed onto the stack in reverse order
            args = reversed([self.evaluate_stack(s) for _ in range(num_args)])
            return self.fn[op](*args)
        elif op[0].isalpha():
            raise Exception("invalid identifier '%s'" % op)
        else:
            # try to evaluate as int first, then as float if int fails
            try:
                return int(op)
            except ValueError:
                return float(op)

    def evaluate_stack(self, s: list, i=0):
        op, num_args = s[-1-i], 0
        i += 1
        if isinstance(op, tuple):
            op, num_args = op
        if op == "unary -":
            [tmp, i] = self.evaluate_stack(s, i)
            return [-tmp, i]
        if op in "+-*/^":
            # note: operands are pushed onto the stack in reverse order
            [op2, i] = self.evaluate_stack(s, i)
            [op1, i] = self.evaluate_stack(s, i)
            return [self.opn[op](op1, op2), i]
        elif op in self.fn:
            args = []
            for j in range(num_args):
                [tmp, i] = self.evaluate_stack(s, i)
                args.append(tmp)
            args = reversed(args)
            return [self.fn[op](*args), i]
        elif op[0].isalpha():
            raise SolutionException("invalid identifier '%s'" % op)
        else:
            # try to evaluate as int first, then as float if int fails
            try:
                return [int(op), i]
            except ValueError:
                return [float(op), i]

    def push_first(self, toks):
        self.exprStack[self.curr].append(toks[0])

    def push_unary_minus(self, toks):
        for t in toks:
            if t == "-":
                self.exprStack[self.curr].append("unary -")
            else:
                break

    def push_expression(self, tokens):
        tmp = self.exprStack[self.curr]
        self.exprStack[self.curr] = Expression.Expression()
        self.exprStack[self.curr].initialize(tmp, self.varStack[self.curr], reconstruct_string(tokens), self)
        self.curr += 1
        self.exprStack.append([])
        self.varStack.append([])

    def nextEquation(self, toks):
        self.meta.append("equation")
        self.push_expression(toks)

    # def nextMultiassing(self, toks):
    #     self.meta.append("multiassign")
    #     tmp = self.exprStack[self.curr]
    #     self.exprStack[self.curr] = MultiAssignExpression()
    #     self.exprStack[self.curr].initialize(tmp, self.varStack[self.curr], reconstruct_string(toks), self)
    #     self.curr += 1
    #     self.exprStack.append([])
    #     self.varStack.append([])

    def push_multiassign(self, toks):
        toks.insert(0, (toks.pop(0), len(toks[0])))
        self.push_first(toks)

    def push_array(self, toks):
        self.push_first(toks.asList())

    def nextCondition(self, toks):
        self.meta.append("condition")
        self.push_expression(toks)

    def functionCreate(self, toks):
        func_name = toks.pop(0)
        func_code = toks.pop(-1)
        args = []
        outs = []

        while toks[0] != ":":
            args.append(toks.pop(0))

        toks.pop(0)
        while toks:
            outs.append(toks.pop(0))

        toks.append(func_name)
        toks.append(args)
        toks.append(outs)
        toks.append(func_code[1:-1])

        self.functions.update({func_name: Function(toks)})

        if len(outs) == 1:
            self.fn.update({func_name: eval(
                "lambda " + ", ".join(args) + " : self.function_exec_wrapper('" + func_name + "', [" + ", ".join(args) + "]" + ")",
                {"self": self})})
        else:
            self.multi_return_fn.update({func_name: eval(
                "lambda " + ", ".join(args) + " : self.function_exec_wrapper('" + func_name + "', [" + ", ".join(
                    args) + "]" + ")",
                {"self": self})})
            # raise SolutionException("Currently only single return value user defined functions allowed")

    def function_exec_wrapper(self, func_name, args):
        return self.functions[func_name].solve(args)

    def addVar(self, toks):
        self.varStack[self.curr].append(toks[0])

    def __init__(self):

        self.curr = 0
        self.exprStack = [[]]
        self.varStack = [[]]
        self.meta = []
        self.radians = 1
        self.functions = {}

        self.opn = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
        }

        self.cond_op = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            ">": operator.gt,
            "<=": operator.le,
            ">=": operator.ge,
        }

        self.fn = {
            "sin": lambda a: np.sin(a) if self.radians else np.sin(np.radians(a)),
            "sinh": lambda a: np.sinh(a) if self.radians else np.sinh(np.radians(a)),
            "cos": lambda a: np.cos(a) if self.radians else np.cos(np.radians(a)),
            "cosh": lambda a: np.cosh(a) if self.radians else np.cosh(np.radians(a)),
            "tan": lambda a: np.tan(a) if self.radians else np.tan(np.radians(a)),
            "tanh": lambda a: np.tanh(a) if self.radians else np.tanh(np.radians(a)),

            "arcsin": lambda a: np.arcsin(a) if self.radians else np.degrees(np.arcsin(a)),
            "arcsinh": lambda a: np.arcsinh(a) if self.radians else np.degrees(np.arcsinh(a)),
            "arccos": lambda a: np.arccos(a) if self.radians else np.degrees(np.arccos(a)),
            "arccosh": lambda a: np.arccosh(a) if self.radians else np.degrees(np.arccosh(a)),
            "arctan": lambda a: np.arctan(a) if self.radians else np.degrees(np.arctan(a)),
            "arctanh": lambda a: np.arctanh(a) if self.radians else np.degrees(np.arctanhn(a)),

            "exp": np.exp,
            "abs": np.abs,
            "sqrt": np.sqrt,
            "trunc": lambda a: int(a),
            "round": round,
            "sgn": lambda a: -1 if a < -1e-12 else 1 if a > 1e-12 else 0,
        }

        self.multi_return_fn = {}

        keywords = {
            k: CaselessKeyword(k)
            for k in """\
                    IF ELSEIF ELSE FUNCTION
                    """.split()
        }

        self.any_keyword = MatchFirst(keywords.values())
        self.any_identifier = (~self.any_keyword + Word(alphas, alphanums + "_$"))
        lpar, rpar = map(Suppress, "()")
        self.FUNCTION = CaselessKeyword("function")
        function_prototype = (Suppress(self.FUNCTION) + self.any_identifier + Suppress(lpar) + delimitedList(
            self.any_identifier) + ":" + delimitedList(self.any_identifier) + rpar + restOfLine()).setParseAction(
            self.functionCreate)

        self.grammar = (Suppress(LineEnd()) | function_prototype)
        self.grammar.ignore(pythonStyleComment)

    def update_grammar(self):
        e = CaselessKeyword("e()").setParseAction(replace_e)
        pi = CaselessKeyword("pi()").setParseAction(replace_pi)
        fnumber = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
        expr_variable = self.any_identifier.copy()
        expr_variable.setParseAction(self.addVar)

        funcname = oneOf(self.fn.keys())

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Suppress, "()")
        lcb = Literal("{")
        rcb = Literal("}").setParseAction(
            lambda t: self.meta.append("}")
        )
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        equals = Literal("=")

        expr = Forward()
        expr_list = delimitedList(Group(expr))
        fn_call = (funcname + lpar - Group(expr_list) + rpar).setParseAction(
            lambda t: t.insert(0, (t.pop(0), len(t[0])))
        )
        atom = (
                addop[...]
                + (
                        (fn_call | pi | e | fnumber | expr_variable).setParseAction(self.push_first)
                        | Group(lpar + expr + rpar)
                )
        ).setParseAction(self.push_unary_minus)

        factor = Forward()
        factor <<= atom + (expop + factor).setParseAction(self.push_first)[...]
        term = factor + (multop + factor).setParseAction(self.push_first)[...]
        expr <<= term + (addop + term).setParseAction(self.push_first)[...]
        equation = (expr + equals.setParseAction(self.push_first) + expr).setParseAction(self.nextEquation)

        # Define if-else statement
        ifElseStmt = Forward()
        IF = CaselessKeyword("if")
        ELSE = CaselessKeyword("else").setParseAction(
            lambda t: self.meta.append("else")
        )

        conditional_op = oneOf(self.cond_op.keys())
        condition = (expr + conditional_op.setParseAction(self.push_first) + expr).setParseAction(self.nextCondition)

        ifelse_content = equation | ifElseStmt
        ifStmt = IF + lpar + condition + rpar + lcb + OneOrMore(ifelse_content) + rcb
        elseStmt = ELSE + lcb + OneOrMore(ifelse_content) + rcb
        ifElseStmt <<= (ifStmt + Optional(elseStmt))

        multi_return_fn_call = (oneOf(self.multi_return_fn.keys()) + lpar - Group(expr_list) + rpar)

        multi_return_expr = (Suppress("[") + Group(delimitedList(expr_variable)).setParseAction(self.push_array) + Suppress("]") + equals + multi_return_fn_call.setParseAction(
            self.push_multiassign
        )).setParseAction(self.nextEquation)

        multi_return_expr.addCondition(lambda toks: len(toks[0]) == toks[2][1], message="Function must return the same number of arguments as the number of arguments to unpack.")
        self.grammar = (Suppress(LineEnd()) | ifElseStmt | OneOrMore(equation) | multi_return_expr)
        # self.grammar = (Suppress(LineEnd()) | grArray)
        self.grammar.ignore(pythonStyleComment)

    def parseFunctionContents(self, settings, guess_values):
        for func_name in self.functions:
            self.curr = 0
            self.exprStack = [[]]
            self.varStack = [[]]
            self.meta = []
            self.functions[func_name].initialize(self, settings, guess_values)

        self.curr = 0
        self.exprStack = [[]]
        self.varStack = [[]]
        self.meta = []