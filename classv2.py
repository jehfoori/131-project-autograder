# pylint: disable=too-few-public-methods

"""
Module with classes for class, field, and method definitions.

In P1, we don't allow overloading within a class;
two methods cannot have the same name with different parameters.
"""

from intbase import InterpreterBase, ErrorType
from type_valuev2 import create_value, assign_type
from type_valuev2 import Type, Value

class MethodDef:
    """
    Wrapper struct for the definition of a member method.
    """

    def __init__(self, method_def):
        self.return_type = method_def[1]
        self.method_name = method_def[2]
        self.formal_params = []
        self.param_types = {}
        for param in method_def[3]:
            print(param)
            self.formal_params.append(param[1])
            self.param_types[param[1]] = param[0]
        self.code = method_def[4]


class FieldDef:
    """
    Wrapper struct for the definition of a member field.
    """

    def __init__(self, field_def):
        self.field_type = field_def[1]
        self.field_name = field_def[2]
        self.default_field_value = field_def[3]


class ClassDef:
    """
    Holds definition for a class:
        - list of fields (and default values)
        - list of methods

    class definition: [class classname [field1 field2 ... method1 method2 ...]]
    """

    def __init__(self, class_def, interpreter):
        self.interpreter = interpreter
        self.name = class_def[1]
        self.__create_field_list(class_def[2:])
        self.__create_method_list(class_def[2:])

    def get_fields(self):
        """
        Get a list of FieldDefs for *all* fields in the class.
        """
        return self.fields

    def get_methods(self):
        """
        Get a list of MethodDefs for *all* fields in the class.
        """
        return self.methods

    def __create_field_list(self, class_body):
        self.fields = []
        fields_defined_so_far = set()
        for member in class_body:
            if member[0] == InterpreterBase.FIELD_DEF:
                if member[2] in fields_defined_so_far:  # redefinition
                    self.interpreter.error(
                        ErrorType.NAME_ERROR,
                        "duplicate field " + member[1]                    
                    )
                new_field = FieldDef(member)
                f_type = assign_type(new_field.field_type)
                v_type = create_value(member[3]).type()

                if f_type == Type.CLASS:
                    # if class name doesn't exist yet
                    if new_field.field_type not in self.interpreter.class_index and new_field.field_type != self.name:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type/type mismatch with field " + member[2]
                        )
                    # if default value isn't null
                    elif new_field.default_field_value != InterpreterBase.NULL_DEF:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type/type mismatch with field " + member[2]
                        )
                elif f_type == Type.INT or f_type == Type.STRING or f_type == Type.BOOL:
                    if v_type != f_type:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type/type mismatch with field " + member[2]
                        )
                self.fields.append(new_field)
                fields_defined_so_far.add(new_field.field_name)

    def __create_method_list(self, class_body):
        self.methods = []
        methods_defined_so_far = set()
        for member in class_body:
            if member[0] == InterpreterBase.METHOD_DEF:
                if member[1] in methods_defined_so_far:  # redefinition
                    self.interpreter.error(
                        ErrorType.NAME_ERROR,
                        "duplicate method " + member[1],
                        member[0].line_num,
                    )
                self.methods.append(MethodDef(member))
                methods_defined_so_far.add(member[1])
