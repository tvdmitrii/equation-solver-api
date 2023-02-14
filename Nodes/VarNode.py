from __future__ import annotations

from Nodes.Node import Node
from DataStorage import DataStorage
from Nodes.NumNode import NumNode


class VarNode(Node):
    def __init__(self, name):
        super().__init__("VarNode", name, [])
        self.type = "VarNode"

    def simplify(self):
        var = DataStorage.get(self._value)
        if var["solved"]:
            return NumNode(var["value"])
        else:
            return None

    @property
    def value(self):
        return DataStorage.get(self._value)["value"]

    @value.setter
    def value(self, val):
        DataStorage.update(self._value, val, True)

    def calculate(self):
        return DataStorage.get(self._value)["value"]
