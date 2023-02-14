from Expression import *
from EquationSet import *
from SolutionException import *
import numpy as np
from scipy.optimize import *


class EquationSystem:
    def __init__(self, calcFlow):
        self.CF = calcFlow
        self.settings = self.CF.settings
        self.equations = []
        self.N_equations = 0
        self.N_variables = 0
        self.variables = None
        self.guess_values = {}

    def add_equation(self, expression: Expression):
        self.equations = np.append(self.equations, expression)
        self.N_equations += 1

    def reset(self):
        for eq in self.equations:
            eq.reset()

    def initialize(self):

        # Figure out what variables equation system has
        variable_names = set()
        for eq in self.equations:
            variable_names = variable_names.union(eq.get_variable_names())

        # Dealt with variables that are already known
        self.pull_known_variables()
        variable_names = variable_names - set(self.CF.known_variables.keys())

        self.N_variables = len(variable_names)
        variable_names = sorted(variable_names)
        self.variables = dict(zip(variable_names, np.ones(self.N_variables, dtype=float)))

        self.checkWellDefined()

        dicts_update_existing(self.variables, self.CF.guess_values)
        dicts_update_existing(self.variables, self.CF.known_variables)

    def update_variables(self, variables : dict, start):
        self.variables.update(variables)

        for i in range(start, self.N_equations):
            self.equations[i].substitute_variables(variables, True)

    def pull_known_variables(self):
        for i in range(self.N_equations):
            self.equations[i].substitute_variables(self.CF.known_variables, True)

    def push_known_variables(self):
        self.CF.update_known_variables(self.variables)

    def list_equations(self, start, end):
        result = ""
        for i in range(start, end):
            result += "\t" + self.equations[i].equation_string + '\n'

        return result

    def checkWellDefined(self):
        if self.N_variables > self.N_equations:
            self.CF.success = False
            self.error = "Block underdefined! Variables: " + str(self.N_variables) + ", Equations: " + str(self.N_equations) + "\n"
            self.error += self.list_equations(0, self.N_equations)
            self.error += "List of variables:\n"
            self.error += "\t" + str(sorted(self.variables.keys()))
            self.CF.error = self.error
            raise SolutionException("System is underdefined!")

        if self.N_variables < self.N_equations:
            self.CF.success = False
            self.error = "Block overdefined! Variables: " + str(self.N_variables) + ", Equations: " + str(
                self.N_equations) + "\n"
            self.error += self.list_equations(0, self.N_equations)
            self.error += "List of variables:\n"
            self.error += "\t" + str(sorted(self.variables.keys()))
            self.CF.error = self.error
            raise SolutionException("System is overdefined!")

    def handle_solution(self, variables, sol, start, end):
        self.CF.solution = sol
        self.CF.success = sol.success
        if sol.success:
            self.update_variables(dict(zip(variables.keys(), sol.x)), start)
        else:
            self.CF.error = "Failed to solve block:" + '\n'
            self.CF.error += self.list_equations(start, end)
            self.CF.error += "Solver success: " + str(sol.success) + '\n'
            self.CF.error += sol.message + '\n'
            self.CF.error += "Residuals: " + str(sol.fun) + '\n'
            self.CF.error += "Values: " + str(sol.x) + '\n'
            self.CF.solution = sol
            self.CF.success = False
            raise SolutionException("Error solving equation system")

    def solve(self):
        self.equations = sorted(self.equations, key=lambda x: x.N_vars, reverse=False)

        # Test starting point
        start = 0
        end = self.N_equations
        eq_set = EquationSet(self, start, end)
        f = eq_set.test_point(list(eq_set.local_variables.values()))
        if np.isnan(f).any():
            for key in self.variables:
                self.variables[key] = self.variables[key] + np.random.random() / 100

        i = 0
        while (i in range(0, self.N_equations)) and (self.equations[i].N_vars == 1):
            while (i in range(0, self.N_equations)) and (self.equations[i].N_vars == 1):

                if self.equations[i].is_assignment():
                    sol = OptimizeResult.fromkeys(["success", "x"])
                    [vname, val] = self.equations[i].assign()
                    sol.x = [float(val)]
                    sol.success = True
                    self.handle_solution({vname: val}, sol, i, i + 1)
                else:
                    eq_set = EquationSet(self, i, i+1)
                    sol = root(eq_set.function, list(eq_set.local_variables.values()), jac=True, method='hybr',
                               options={'xtol': self.settings["xtol"], 'maxfev': self.settings["iter"]})
                    self.handle_solution(eq_set.local_variables, sol, i, i + 1)

                i += 1
            self.equations[i:self.N_equations] = sorted(self.equations[i:self.N_equations], key=lambda x: x.N_vars, reverse=False)

        if i in range(0, self.N_equations):
            eq_set = EquationSet(self, i, self.N_equations)
            sol = root(eq_set.function, list(eq_set.local_variables.values()), jac=True, method='hybr',
                       options={'xtol': self.settings["xtol"], 'maxfev': self.settings["iter"]})

            self.handle_solution(eq_set.local_variables, sol, i, self.N_equations)

        self.push_known_variables()