from __future__ import annotations

from Nodes.Node import Node


class NumNode(Node):
    def __init__(self, value):
        super().__init__("NumNode", value, [])

    def simplify(self) -> NumNode:
        return self

    def calculate(self):
        return self.value
