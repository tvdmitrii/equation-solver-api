from __future__ import annotations


class Node:
    def __init__(self, type: str, value, children: list[Node]):
        self.type = type
        self._value = value
        self.children = children
        self.length = len(self.children)

    def simplify(self) -> bool:
        flag = True
        for i in range(self.length):
            child = self.children[i].simplify()
            if child:
                self.children[i] = child
            else:
                flag = False

        return flag

    def string(self, prefix="") -> str:
        result = prefix + "| [" + str(self._value) + "] (" + str(self.type) + ")\n"
        for child in self.children:
            result += child.string(prefix + "\t")
        return result

    def print(self):
        print(self.string())

    @property
    def value(self):
        return self._value
