from copy import deepcopy
import numpy as np
from pyparsing import ParseException

from CalculationFlow import *


class Function:
    def initialize(self, grammar, settings, guess_values):
        try:
            result = grammar.grammar.parseString(self.code, parseAll=True)
        except ParseException as err:
            self.CF.success = False
            self.CF.error = "Parsing error at (char " + str(err.args[1]) + ") in line: " + err.markInputline("_") + "\n"
            raise err

        all_variable_names = sorted(set(flatten(grammar.varStack)))
        guess_values_real = dict(zip(all_variable_names, np.ones(len(all_variable_names), dtype=float)))
        dicts_update_existing(guess_values_real, guess_values)
        guess_values = guess_values_real

        self.CF.initialize(grammar.meta, grammar.exprStack, settings, guess_values)
        self.CF_fresh_copy = self.CF.copy()

    def __init__(self, prototype):
        self.name = prototype[0]
        self.args = prototype[1]
        self.outs = prototype[2]
        self.code = prototype[3]

        self.CF = CalculationFlow()
        self.CF_fresh_copy = None
        self.is_running = False

    def solve(self, values):
        if self.is_running:
            CF = self.CF_fresh_copy.copy()
            CF.known_variables.update(dict(zip(self.args, values)))
            CF.solve()

            success = CF.success
            solution = CF.known_variables
            error = CF.error
            del CF
        else:
            self.CF.known_variables.update(dict(zip(self.args, values)))
            self.is_running = True
            self.CF.solve()
            self.is_running = False
            success = self.CF.success
            solution = self.CF.known_variables
            error = self.CF.error
            self.CF.reset()

        if success:
            return solution[self.outs[0]]
        else:
            raise SolutionException("Error during function call!\n" + error)

