class DataStorage:
    __instance = None
    variables = {}
    dx = 0.001
    xtol = 1e-8
    itr = 0

    @staticmethod
    def add(name):
        if name not in DataStorage.variables:
            DataStorage.variables.update({name: {"solved": False, "value": 0}})

    @staticmethod
    def getdx():
        return DataStorage.dx

    @staticmethod
    def setValue(name, value):
        DataStorage.variables[name].update({"value": value})

    @staticmethod
    def perturb(name, value):
        DataStorage.variables[name].update({"value": DataStorage.variables[name]["value"] + value})

    @staticmethod
    def setSolved(name, solved):
        DataStorage.variables[name].update({"solved": solved})

    @staticmethod
    def update(name, value, solved):
        DataStorage.variables[name].update({"value": value, "solved": solved})

    @staticmethod
    def get(name):
        return DataStorage.variables[name]