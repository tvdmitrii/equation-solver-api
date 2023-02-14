from Block import Block
from Condition import *
from copy import deepcopy

class CalculationFlow:
    def reset(self):
        self.known_variables = {}
        self.success = False
        self.solution = None
        self.error = ""

        self.start_item.reset()

    def copy(self):
        newCF = CalculationFlow()
        # newCF.known_variables = self.known_variables.copy()
        # newCF.settings = self.settings.copy()
        # newCF.guess_values = self.guess_values.copy()
        # if self.start_item is not None:
        #     newCF.start_item = self.start_item.copy(newCF)
        tmp = []
        for i in range(len(self.exprStack)):
            # print(self.exprStack[i])
            tmp.append(self.exprStack[i].copy())

        newCF.initialize(self.meta.copy(), tmp, self.settings.copy(), self.guess_values.copy())
        # newCF.reset()
        return newCF

    def initialize(self, meta, exprStack, settings, guess_values):
        self.exprStack = {}
        self.meta = meta

        self.settings = {}
        self.guess_values = {}
        self.known_variables = {}
        self.success = False
        self.solution = None
        self.error = ""

        self.is_block_open = False
        self.cur_block = None
        self.cur_item = None
        self.start_item = None

        self.condition_stack = []

        self.exprStack = exprStack
        self.settings = settings
        self.guess_values = guess_values

        i = 0
        j = 0
        N = len(self.meta)
        while j < N:
            if self.meta[j] == "equation":
                if not self.is_block_open:
                    self.startBlock()
                self.cur_item.add(self.exprStack[i])
                i += 1

            if self.meta[j] == "condition":
                self.startCondition()
                self.cur_item.condition = self.exprStack[i]
                i += 1

            if self.meta[j] == "}":
                self.endBlock()
                self.cur_item = self.condition_stack[-1]
                if (j + 1 < N) and (meta[j + 1] == "else"):
                    self.cur_item.cur_next = 1
                else:
                    self.cur_item.cur_next = 2
                    self.condition_stack.pop()
            j += 1

        self.endBlock()

    def __init__(self):
        self.exprStack = {}

        self.settings = {}
        self.guess_values = {}
        self.known_variables = {}
        self.success = False
        self.solution = None
        self.error = ""

        self.is_block_open = False
        self.cur_block = None
        self.cur_item = None
        self.start_item = None

        self.condition_stack = []

    def startBlock(self):
        # print("Start Block")
        self.is_block_open = True
        block = Block(self)
        self.advance(block)

    def advance(self, item):
        if self.cur_item is not None:
            self.cur_item.setNext(item)
        else:
            self.start_item = item
        self.cur_item = item

    def endBlock(self):
        # print("End Block")
        self.is_block_open = False

    def startCondition(self):
        self.endBlock()
        condition = Condition(self)
        self.advance(condition)
        self.condition_stack.append(condition)

    def solve(self):
        self.start_item.solve()

    def update_known_variables(self, known_variables):
        self.known_variables.update(known_variables)
