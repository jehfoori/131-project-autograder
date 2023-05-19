# pylint: disable=too-few-public-methods

"""
Module with classes for class, field, and method definitions.

In P1, we don't allow overloading within a class;
two methods cannot have the same name with different parameters.
"""

from intbase import InterpreterBase, ErrorType
from type_valuev2 import create_value
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

    def __init__(self, class_def, interpreter, superclass=None):
        self.interpreter = interpreter
        self.superclass = superclass
        self.name = class_def[1]
        self.__create_class_hierarchy(superclass)
        self.__create_field_map(class_def[2:])
        self.__create_method_map(class_def[2:])

    
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

    def assign_type(self, type):
        if type == InterpreterBase.INT_DEF:
            return Type.INT
        elif type == InterpreterBase.BOOL_DEF:
            return Type.BOOL
        elif type == InterpreterBase.STRING_DEF:
            return Type.STRING
        elif self.existing_class(type):
            return Type.CLASS
        else:
            return None

    def existing_class(self, class_name):
        if class_name in self.interpreter.class_index or class_name == self.name:
            return True
        return False

    def __create_class_hierarchy(self, superclass):
        self.class_hierarchy = []
        if superclass is None:
            self.class_hierarchy.append(self.name)
        else:
            self.class_hierarchy = superclass.class_hierarchy + [self.name]
        print(self.name + str(self.class_hierarchy))
    
    def __create_field_map(self, class_body):
        self.fields = {}
        fields_defined_so_far = set()
        # inherit fields from superclass

        for member in class_body:
            if member[0] == InterpreterBase.FIELD_DEF:
                if member[2] in fields_defined_so_far:  # redefinition
                    self.interpreter.error(
                        ErrorType.NAME_ERROR,
                        "duplicate field " + member[1]                    
                    )
                new_field = FieldDef(member)
                f_type = self.assign_type(new_field.field_type)
                v_type = create_value(member[3]).type()

                if f_type is None:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid type/type mismatch with field " + member[2]
                    )
                elif f_type == Type.CLASS:
                    # if default value isn't null
                    if new_field.default_field_value != InterpreterBase.NULL_DEF:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type/type mismatch with field " + member[2]
                        )
                else:
                    if v_type != f_type:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type/type mismatch with field " + member[2]
                        )
                self.fields[new_field.field_name] = new_field
                fields_defined_so_far.add(new_field.field_name)
        print(self.name + str(self.fields))


    def __create_method_map(self, class_body):
        self.methods = {}
        methods_defined_so_far = set()

        for member in class_body:
            if member[0] == InterpreterBase.METHOD_DEF:
                if member[2] in methods_defined_so_far:  # redefinition
                    self.interpreter.error(
                        ErrorType.NAME_ERROR,
                        "duplicate method " + member[1],
                        member[0].line_num,
                    )
                new_method = MethodDef(member)
                r_type = self.assign_type(new_method.return_type)
                if r_type is None and new_method.return_type != InterpreterBase.VOID_DEF:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid return type for method " + new_method.method_name
                    )
                fields_defined = set()
                for formal_param in new_method.formal_params:
                    if formal_param in fields_defined:
                        self.interpreter.error(
                            ErrorType.NAME_ERROR,
                            "duplicate formal param name " + formal_param
                        )
                    f_type = self.assign_type(new_method.param_types[formal_param])
                    if f_type is None:
                        self.interpreter.error(
                            ErrorType.TYPE_ERROR,
                            "invalid type for parameter " + formal_param
                        )
                    fields_defined.add(formal_param)
                self.methods[new_method.method_name] = new_method
                methods_defined_so_far.add(new_method.method_name)
        print(self.name + str(self.methods))