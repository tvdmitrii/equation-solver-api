import numpy as np
from scipy.optimize import root
from SolutionException import *


class EquationSet:
    def __init__(self, sys, start, end):
        self.sys = sys
        self.start = start
        self.end = end
        self.N = self.end - self.start

        variable_names = np.array([])
        for i in range(self.start, self.end):
            variable_names = np.concatenate((variable_names, self.sys.equations[i].get_variable_names()))
        variable_names = sorted(set(variable_names))

        self.local_variables = dict.fromkeys(variable_names)
        dicts_update_existing(self.local_variables, sys.variables)

        self.f = np.zeros(self.N)
        self.df = np.zeros((self.N, self.N), dtype=float)

    def calc_derivative(self):
        h = self.sys.settings["fd_step"]
        for i in range(self.start, self.end):
            for j, name in enumerate(self.local_variables):
                tmp_store = self.local_variables[name]
                self.local_variables[name] += h
                tmpp = self.sys.equations[i].evaluate(self.local_variables)
                self.local_variables[name] = tmp_store - h
                tmpm = self.sys.equations[i].evaluate(self.local_variables)
                self.df[i - self.start, j] = (tmpp - tmpm) / h / 2.0
                self.local_variables[name] = tmp_store

    def test_point(self, x):
        self.local_variables.update(dict(zip(self.local_variables.keys(), x)))

        for i in range(self.start, self.end):
            self.f[i - self.start] = self.sys.equations[i].evaluate(self.local_variables)

        return self.f

    def function(self, x):
        self.local_variables.update(dict(zip(self.local_variables.keys(), x)))

        for i in range(self.start, self.end):
            self.f[i - self.start] = self.sys.equations[i].evaluate(self.local_variables)
        self.calc_derivative()
        return self.f, self.df
