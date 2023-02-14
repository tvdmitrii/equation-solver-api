import Expression
import EquationSystem


class Block:

    def __init__(self, calcFlow):
        self.next = None
        self.CF = calcFlow
        self.eq_system = EquationSystem.EquationSystem(self.CF)

    def add(self, expr: Expression):
        self.eq_system.add_equation(expr)

    def setNext(self, item):
        self.next = item

    def reset(self):
        self.eq_system.reset()
        if self.next is not None:
            self.next.solve()

    def solve(self):
        self.eq_system.initialize()
        self.eq_system.solve()
        if self.next is not None:
            self.next.solve()

    def copy(self):
        newBlock = Block(self.CF)
        if newBlock.next is not None:
            newBlock.next = self.next.copy()
        else:
            newBlock.next = None

        return newBlock

    def print(self):
        print("BLOCK START")
        for expr in self.eq_system.equations:
            print("\t" + expr.equation_string)
            print(expr.variable_names)
        print("BLOCK END")

        if self.next is not None:
            self.next.print()
