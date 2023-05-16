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
        self.environment_val = {}
        self.environment_type = {}

    def get_val(self, symbol):
        """
        Get data associated with variable name.
        """
        if symbol in self.environment_val:
            return self.environment_val[symbol]

        return None
    
    def get_type(self, symbol):
        if symbol in self.environment_type:
            return self.environment_type[symbol]

        return None

    def set_val(self, symbol, value):
        """
        Set data associated with a variable name.
        """
        self.environment_val[symbol] = value

    def set_type(self, symbol, type):
        self.environment_type[symbol] = type