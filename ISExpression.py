class ISExpression:
    def __init__(self, equation_string, N_vars, N_equations):
        self.equation_string = equation_string
        self.N_vars = N_vars
        self.N_equations = N_equations

    def reset(self):
        raise NotImplemented("You must implement ISExpression methods!")

    def get_variable_names(self):
        raise NotImplemented("You must implement ISExpression methods!")

    def substitute_variables(self):
        raise NotImplemented("You must implement ISExpression methods!")

    def is_assignment(self):
        raise NotImplemented("You must implement ISExpression methods!")