from __future__ import annotations

from Nodes.Node import Node
from Nodes.NumNode import NumNode
from DataStorage import DataStorage
import math as math

class FuncOp(Node):
    def __init__(self, fncName, children: list[Node]):
        super().__init__("FuncOp", "", children)
        self.fncName = fncName

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
