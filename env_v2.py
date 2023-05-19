"""
Module that manages program environments. Currently a mapping from variables to values.
"""


class EnvironmentManager:
    """
    The EnvironmentManager class maintains the lexical environment for a construct.
    In project 1, this is just a mapping between each variable (aka symbol)
    in a brewin program and the value of that variable - the value that's passed in can be
    anything you like. In our implementation we pass in a Value object which holds a type
    and a value (e.g., Int, 10).
    """

    def __init__(self):
        self.environment = {}
        self.let_tables = []
        self.field_scope = []

    def get(self, symbol):
        """
        Get data associated with variable name.
        """
        for table in reversed(self.let_tables):
            if symbol in table:
                return table[symbol]
        if symbol in self.environment:
            return self.environment[symbol]

        return None
        
    def set(self, symbol, value):
        """
        Set data associated with a variable name.
        """
        for table in reversed(self.let_tables):
            if symbol in table:
                table[symbol] = value
                return
        self.environment[symbol] = value