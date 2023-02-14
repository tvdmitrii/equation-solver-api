from __future__ import annotations

from Nodes.Node import Node
from Nodes.NumNode import NumNode
from DataStorage import DataStorage


class BinOp(Node):
    def __init__(self, value, children: list[Node]):
        super().__init__("BinOp", value, children)
        if self.length != 2:
            raise ValueError('BinOp requires exactly 2 operands.')

    def simplify(self):

        simplified = super().simplify()

        if simplified:
            return NumNode(self.calculate())
        else:
            return None

    def calculate(self):

        if self.value == "+":
            return self.children[0].calculate() + self.children[1].calculate()
        elif self.value == "-":
            return self.children[0].calculate() - self.children[1].calculate()
        elif self.value == "*":
            return self.children[0].calculate() * self.children[1].calculate()
        elif self.value == "/":
            return self.children[0].calculate() / self.children[1].calculate()
        elif self.value == "^":
            return self.children[0].calculate() ** self.children[1].calculate()
        else:
            raise ValueError('Unsupported binary operation ' + self.value)
