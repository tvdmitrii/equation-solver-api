from ISExpression import ISExpression
from SolutionException import SolutionException

class MultiAssignExpression(ISExpression):
    def get_variable_names(self):
        return list(self.variable_positions.keys())

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

        self.N_equations = len(self.exprStack[0])
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
