import Expression
from SolutionException import *

class Condition:
    def __init__(self, calcFlow):
        self.condition = None
        self.next = [None, None, None]
        self.cur_next = 0

        self.CF = calcFlow

    def set(self, condition: Expression):
        self.condition = condition

    def setNext(self, item):
        self.next[self.cur_next] = item

    def reset(self):
        for n in self.next:
            if n is not None:
                n.reset()

    def copy(self):
        newCondition = Condition(self.CF)
        newCondition.condition = self.condition

        for i in range(3):
            if self.next[i] is not None:
                newCondition.next[i] = self.next[i].copy()
            else:
                newCondition.next[i] = None

        return newCondition

    def solve(self):
        for name in self.condition.get_variable_names():
            if name not in self.CF.known_variables:
                self.CF.success = False
                self.CF.error = "Variable '" + name + "' must be known for condition '" + self.condition.equation_string + "' to be evaluated!"
                raise SolutionException("Error evaluating condition!")

        result = self.condition.evaluate(self.CF.known_variables)
        if result:
            if self.next[0] is not None:
                self.next[0].solve()
        else:
            if self.next[1] is not None:
                self.next[1].solve()
        if self.next[2] is not None:
            self.next[2].solve()

    def print(self):
        print("IF")
        print(self.condition.equation_string)

        print("TRUE PATH")
        if self.next[0] is not None:
            self.next[0].print()

        print("FALSE PATH")
        if self.next[1] is not None:
            self.next[1].print()

        print("END IF")
        if self.next[2] is not None:
            self.next[2].print()
