import numpy as np
from ISExpression import ISExpression


def pick_from_dictionary(dictA: dict, keys: list):
    common_keys = dictA.keys() & keys

    result = dict.fromkeys(common_keys)
    for key in common_keys:
        result[key] = dictA[key]

    return result


class Expression(ISExpression):

    def set_variable_pos(self):
        for i, key in enumerate(self.exprStack):
            try:
                self.variable_positions[key].append(i)
            except KeyError as err:
                continue

        self.variable_positions_original = self.variable_positions.copy()

    def get_variable_names(self):
        return list(self.variable_positions.keys())

    def reset(self):
        self.variable_positions = self.variable_positions_original.copy()
        self.N_vars = self.N_vars_original

    def substitute_variables(self, variables: dict, remove=False):
        subs_dict = pick_from_dictionary(variables, self.variable_positions.keys())

        for name in subs_dict:
            for i in self.variable_positions[name]:
                self.exprStack[i] = str(subs_dict[name])

        if remove:
            for name in subs_dict:
                del self.variable_positions[name]
                self.N_vars -= 1

    def evaluate(self, variables: dict):
        self.substitute_variables(variables)
        [result, i] = self.grammar.evaluate_stack(self.exprStack)
        # result = self.grammar.evaluate_stack(self.exprStack.copy())
        if self.op == "=":
            return result
        else:
            return self.grammar.cond_op[self.op](result, 0)

    def move_left(self):
        length = len(self.exprStack)
        i = self.detectOperator()

        if i == 1:
            self.assign_var = self.exprStack[0]

        if i == length - 2 and self.exprStack[length - 1] == "0":
            self.exprStack.pop()
            self.exprStack.pop()
            return

        j = i + 1
        while j < length:
            self.exprStack[i] = self.exprStack[j]
            i += 1
            j += 1
        self.exprStack[i] = "-"

    def is_assignment(self):
        if (self.assign_var is not None) and (self.assign_var in self.variable_positions) and (self.N_vars == 1) and (len(self.variable_positions[self.assign_var]) == 1):
            return True

        return False

    def assign(self):
        result = self.evaluate({self.assign_var: 0.0})
        return [self.assign_var, -result]

    def copy(self):
        newExpr = Expression()
        newExpr.equation_string = self.equation_string
        newExpr.exprStack = self.exprStack.copy()
        newExpr.grammar = self.grammar
        newExpr.variable_positions_original = self.variable_positions_original.copy()
        newExpr.variable_positions = newExpr.variable_positions_original.copy()
        newExpr.op = self.op
        newExpr.N_vars_original = self.N_vars_original
        newExpr.N_vars = newExpr.N_vars_original
        newExpr.assign_var = self.assign_var
        return newExpr

    def detectOperator(self):
        try:
            i = self.exprStack.index("=")
            self.op = "="
        except ValueError as err:
            for op in self.grammar.cond_op.keys():
                try:
                    i = self.exprStack.index(op)
                    self.op = op
                except ValueError as err:
                    continue

        return i

    def __init__(self):
        super().__init__("", 0, 0)
        self.exprStack = []
        self.grammar = None
        self.variable_positions = {}
        self.variable_positions_original = {}
        self.op = ""
        self.N_vars_original = 0
        self.assign_var = None

    def initialize(self, exprStack, varStack, equation_str, grammar):
        self.equation_string = equation_str
        self.exprStack = exprStack
        self.grammar = grammar
        self.variable_positions_original = {}
        self.op = ""

        variable_names = sorted(set(varStack))
        self.N_vars = len(variable_names)
        self.N_vars_original = self.N_vars

        self.variable_positions = dict.fromkeys(variable_names)
        for key in self.variable_positions:
            self.variable_positions[key] = []

        self.move_left()

        if self.N_vars != 0:
            self.set_variable_pos()

