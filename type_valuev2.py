"""
Module that contains the Value definition and associated type constructs.
"""

from enum import Enum
from intbase import InterpreterBase


class Type(Enum):
    """Enum for all possible Brewin types."""

    INT = 1
    BOOL = 2
    STRING = 3
    CLASS = 4
    NOTHING = 5


# Represents a value, which has a type and its value
class Value:
    """A representation for a value that contains a type tag."""

    def __init__(self, value_type, value=None):
        self.__type = value_type
        self.__value = value

    def type(self):
        return self.__type

    def value(self):
        return self.__value

    def set(self, other):
        self.__type = other.type()
        self.__value = other.value()

class ClassValue(Value):
    def __init__(self, value_type, value=None, class_name=None):
        super().__init__(value_type, value)
        self.__class_name = class_name
    
    def set_class_name(self, name):
        self.__class_name = name
        
    def class_name(self):
        return self.__class_name

# pylint: disable=too-many-return-statements
def create_value(val, type_name=None):
    """
    Create a Value object from a Python value.
    """
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    if val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    if val[0] == '"':
        return Value(Type.STRING, val.strip('"'))
    if val.lstrip('-').isnumeric():
        return Value(Type.INT, int(val))
    if val == InterpreterBase.NULL_DEF:
        return ClassValue(Type.CLASS, None, type_name)
    if val == InterpreterBase.NOTHING_DEF:
        return Value(Type.NOTHING, None)
    return None
