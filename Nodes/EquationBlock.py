from __future__ import annotations

from Nodes.Node import Node
from Nodes.Equation import Equation
from Nodes.BinOp import BinOp
from Nodes.NumNode import NumNode
from DataStorage import DataStorage
import numpy as np
from scipy.optimize import *


class EquationBlock(Node):
    def __init__(self, children: list[Equation]):
        super().__init__("EquationBlock", "", children)
        self.is_valid = True
        self.variables = []
        self.N_eq = 0
        self.N_var = 0
        self.is_solved = False
        self.message = ""

    def add(self, equation: Equation):
        self.children.append(equation)

    def init(self):
        while True:
            children_remove = []
            for i, child in enumerate(self.children):
                child.simplify()

                if not child.is_valid:
                    self.is_valid = False
                    return

                if child.is_assignment:
                    children_remove.append(i)

            if children_remove:
                children_remove.sort(reverse=True)
                for i in children_remove:
                    self.children.pop(i)
            else:
                break

        for child in self.children:
            child.find_variables()
            self.variables.extend(child.variables)

        self.variables = list(set(self.variables))
        self.variables.sort()
        self.N_var = len(self.variables)
        self.N_eq = len(self.children)

        if self.N_var != self.N_eq:
            self.is_valid = False
            return

        if self.N_var == 0:
            self.is_valid = False
            return

        # self.x0 = np.ones(self.N_eq)
        self.f = np.zeros(self.N_eq)
        self.df = np.zeros((self.N_eq, self.N_var), dtype=float)

    def string(self, prefix="") -> str:
        result = "Equations: " + str(self.N_eq) + "\n"
        result += "Variables: " + str(self.N_var) + "\n"
        result += "Variable list: " + str(self.variables) + "\n"
        result += "Is Valid: " + str(self.is_valid) + "\n"
        result += super().string(prefix)
        return result

    def solve(self):
        if self.is_valid:
            solution = root(self.solutionHandler, np.ones(self.N_eq), jac=True, method='hybr',
                        options={'xtol': DataStorage.xtol, 'maxfev': DataStorage.itr})

            if solution.success:
                self.is_solved = True
                for i, x_sol in enumerate(solution.x):
                    DataStorage.update(self.variables[i], x_sol, True)
                    self.message = solution.message
        else:
            self.is_solved = False
            self.message = "Equation Block is invalid."

    def calculate(self):
        for i, child in enumerate(self.children):
            self.f[i] = child.calculate()

    def calc_derivatives(self):
        h = DataStorage.getdx()
        for i, var in enumerate(self.variables):
            DataStorage.perturb(var, h)
            # print(DataStorage.variables)
            for j, eq in enumerate(self.children):
                self.df[i, j] = eq.calculate()

            # print("Before:" + str(self.df))
            DataStorage.perturb(var, -2 * h)
            for j, eq in enumerate(self.children):
                self.df[i, j] -= eq.calculate()

            # print("After:" + str(self.df))
            DataStorage.perturb(var, h)

        self.df /= 2 * h

    def solutionHandler(self, x):
        for i, x0 in enumerate(x):
            DataStorage.setValue(self.variables[i], x0)

        self.calculate()
        self.calc_derivatives()
        return self.f, self.df

    def find_variables(self):
        children = []
        children.extend(self.children)
        for child in children:
            if child.type == "VarNode":
                self.variables.append(child._value)

            children.extend(child.children)

        self.variables = list(set(self.variables))
        self.variables.sort()
