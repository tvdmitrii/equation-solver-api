from __future__ import annotations

from Nodes.Node import Node
from Nodes.BinOp import BinOp
from Nodes.NumNode import NumNode
from DataStorage import DataStorage


class Equation(Node):
    def __init__(self, children: list[Node]):
        super().__init__("Equation", "=", children)
        self.is_valid = False
        self.is_assignment = False
        self.variables = []
        if self.length != 2:
            raise ValueError('Equation requires exactly 2 operands.')

    def simplify(self):

        simplified = super().simplify()
        if not simplified:
            self.is_valid = True
        else:
            return

        if self.children[0].type == "VarNode" and self.children[1].type == "NumNode":
            self.children[0].value = self.children[1].value
            self.is_assignment = True
        elif self.children[0].type == "NumNode" and self.children[1].type == "VarNode":
            self.children[1].value = self.children[0].value
            self.is_assignment = True

    def calculate(self):
        return self.children[0].calculate() - self.children[1].calculate()

    def find_variables(self):
        children = []
        children.extend(self.children)
        for child in children:
            if child.type == "VarNode":
                self.variables.append(child._value)

            children.extend(child.children)

        self.variables = list(set(self.variables))
        self.variables.sort()

