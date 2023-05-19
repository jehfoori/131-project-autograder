"""
Module handling the operations of an object. This contains the meat
of the code to execute various instructions.
"""

from env_v2 import EnvironmentManager
from intbase import InterpreterBase, ErrorType
from type_valuev2 import create_value
from type_valuev2 import Type, Value, ClassValue


class ObjectDef:
    STATUS_PROCEED = 0
    STATUS_RETURN = 1
    STATUS_NAME_ERROR = 2
    STATUS_TYPE_ERROR = 3

    def __init__(self, interpreter, class_def, trace_output):
        self.interpreter = interpreter  # objref to interpreter object. used to report errors, get input, produce output
        self.class_def = class_def  # take class body from 3rd+ list elements, e.g., ["class",classname", [classbody]]
        self.trace_output = trace_output
        self.class_name = class_def.name
        self.__map_methods_to_fields()
        self.__map_fields_to_values()
        self.__map_method_names_to_method_definitions()
        self.__create_map_of_operations_to_lambdas()  # sets up maps to facilitate binary and unary operations, e.g., (+ 5 6)

    def call_method(self, method_name, actual_params, line_num_of_caller):
        """
        actual_params is a list of Value objects (all parameters are passed by value).

        The caller passes in the line number so we can properly generate an error message.
        The error is then generated at the source (i.e., where the call is initiated).
        """
        if method_name not in self.methods:
            self.interpreter.error(ErrorType.NAME_ERROR, "unknown method " + method_name, line_num_of_caller,)
        method_info = self.methods[method_name]
        
        if len(actual_params) != len(method_info.formal_params):
            self.interpreter.error(ErrorType.NAME_ERROR, "invalid number of parameters in call to " + method_name, line_num_of_caller,)
        
        env = (EnvironmentManager())  # maintains lexical environment for function; just params for now
        for formal, actual in zip(method_info.formal_params, actual_params):
            formal_type = method_info.param_types[formal]
            if not self.__check_types(formal_type, actual):
                self.interpreter.error(ErrorType.NAME_ERROR, "bad type for " + formal, line_num_of_caller,) 
            if actual.type() == Type.CLASS and actual.value() is None and actual.class_name() is None:
                actual.set_class_name(formal_type)
            env.set(formal, (actual, method_info.param_types[formal]))
        # since each method has a single top-level statement, execute it.
        status, return_value = self.__execute_statement(env, method_info.code)
            
        # if the method explicitly used the (return expression) statement to return a value, then return that
        # value back to the caller
        if status == ObjectDef.STATUS_RETURN:
            # return with no value, return the default
            if return_value.type() == Type.NOTHING:
                return self.__default_value(method_info.return_type)
            else: # returned with a value, check the types
                if method_info.return_type == InterpreterBase.VOID_DEF:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR, 
                        "return type mismatch for method " + method_name,
                        line_num_of_caller,
                    ) 
                # associate a class to null return
                if return_value.type() == Type.CLASS and return_value.value() is None and return_value.class_name() is None:
                    return_value.set_class_name(method_info.return_type)
                if not self.__check_types(method_info.return_type, return_value):
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR, 
                        "return type mismatch for method " + method_name,
                        line_num_of_caller,
                    )
            return return_value         
        # The method didn't explicitly return a value, so return the default value
        return self.__default_value(method_info.return_type)

    def __check_types(self, type, value):
        # if the return type is void we know it's wrong because we've already dealt with empty returns!
        base_type = self.class_def.assign_type(type)
        if base_type != value.type():
            return False
        elif base_type == value.type() and base_type == Type.CLASS:
            if value.class_name() is not None: # bare null values are compatible with any class
                hierarchy = self.interpreter.class_index[value.class_name()].class_hierarchy
                if type not in hierarchy:
                    return False
        return True

    def __default_value(self, return_type):
            if return_type == InterpreterBase.INT_DEF:
                return Value(Type.INT, 0)
            elif return_type == InterpreterBase.BOOL_DEF:
                return Value(Type.BOOL, False)
            elif return_type == InterpreterBase.STRING_DEF:
                return Value(Type.STRING, "")
            elif return_type == InterpreterBase.VOID_DEF:
                return Value(Type.NOTHING)
            else:
                return ClassValue(Type.CLASS, None, return_type)    

    def __execute_statement(self, env, code):
        """
        returns (status_code, return_value) where:
        - status_code indicates if the next statement includes a return
            - if so, the current method should terminate
            - otherwise, the next statement in the method should run normally
        - return_value is a Value containing the returned value from the function
        """
        if self.trace_output:
            print(f"{code[0].line_num}: {code}")
        tok = code[0]
        if tok == InterpreterBase.BEGIN_DEF:
            return self.__execute_begin(env, code)
        if tok == InterpreterBase.SET_DEF:
            return self.__execute_set(env, code)
        if tok == InterpreterBase.IF_DEF:
            return self.__execute_if(env, code)
        if tok == InterpreterBase.CALL_DEF:
            return self.__execute_call(env, code)
        if tok == InterpreterBase.WHILE_DEF:
            return self.__execute_while(env, code)
        if tok == InterpreterBase.RETURN_DEF:
            return self.__execute_return(env, code)
        if tok == InterpreterBase.INPUT_STRING_DEF:
            return self.__execute_input(env, code, True)
        if tok == InterpreterBase.INPUT_INT_DEF:
            return self.__execute_input(env, code, False)
        if tok == InterpreterBase.PRINT_DEF:
            return self.__execute_print(env, code)
        if tok == InterpreterBase.LET_DEF:
            return self.__execute_let(env, code)

        self.interpreter.error(
            ErrorType.SYNTAX_ERROR, "unknown statement " + tok, tok.line_num
        )
    def __execute_let(self, env, code):
        let_scope = {}
        for type, name, value in code[1]:
            if name in let_scope:
                self.interpreter.error(
                ErrorType.NAME_ERROR, "duplicate name in let statement: " + name, code[0].line_num
                )
            value = create_value(value)
            if not self.__check_types(type, value):
                self.interpreter.error(
                ErrorType.TYPE_ERROR, "let statement type mismatch: " + name, code[0].line_num
                )
            let_scope[name] = (value, type)
        env.let_tables.append(let_scope)

        self.__execute_begin(env, code[1:])

        env.let_tables.pop()
        return ObjectDef.STATUS_PROCEED, None

    # (begin (statement1) (statement2) ... (statementn))
    def __execute_begin(self, env, code):
        for statement in code[1:]:
            status, return_value = self.__execute_statement(env, statement)
            if status == ObjectDef.STATUS_RETURN:
                return (
                    status,
                    return_value,
                )  # could be a valid return of a value or an error
        # if we run thru the entire block without a return, then just return proceed
        # we don't want the calling block to exit with a return
        return ObjectDef.STATUS_PROCEED, None

    # (call object_ref/me methodname param1 param2 param3)
    # where params are expressions, and expresion could be a value, or a (+ ...)
    # statement version of a method call; there's also an expression version of a method call below
    def __execute_call(self, env, code):
        return ObjectDef.STATUS_PROCEED, self.__execute_call_aux(
            env, code, code[0].line_num
        )

    # (set varname expression), where expresion could be a value, or a (+ ...)
    def __execute_set(self, env, code):
        val = self.__evaluate_expression(env, code[2], code[0].line_num)
        self.__set_variable_aux(env, code[1], val, code[0].line_num)
        return ObjectDef.STATUS_PROCEED, None

    # (return expression) where expresion could be a value, or a (+ ...)
    def __execute_return(self, env, code):
        if len(code) == 1:
            # [return] with no return expression
            return ObjectDef.STATUS_RETURN, create_value(InterpreterBase.NOTHING_DEF)
        else:
            return ObjectDef.STATUS_RETURN, self.__evaluate_expression(
                env, code[1], code[0].line_num
            )

    # (print expression1 expression2 ...) where expresion could be a variable, value, or a (+ ...)
    def __execute_print(self, env, code):
        output = ""
        for expr in code[1:]:
            # TESTING NOTE: Will not test printing of object references
            term = self.__evaluate_expression(env, expr, code[0].line_num)
            val = term.value()
            typ = term.type()
            if typ == Type.BOOL:
                val = "true" if val else "false"
            # document - will never print out an object ref
            output += str(val)
        self.interpreter.output(output)
        return ObjectDef.STATUS_PROCEED, None

    # (inputs target_variable) or (inputi target_variable) sets target_variable to input string/int
    def __execute_input(self, env, code, get_string):
        inp = self.interpreter.get_input()
        if get_string:
            val = Value(Type.STRING, inp)
        else:
            val = Value(Type.INT, int(inp))

        self.__set_variable_aux(env, code[1], val, code[0].line_num)
        return ObjectDef.STATUS_PROCEED, None

    # helper method used to set either parameter variables or member fields; parameters currently shadow
    # member fields
    def __set_variable_aux(self, env, var_name, value, line_num):
        # parameter shadows fields
        if value.type() == Type.NOTHING:
            self.interpreter.error(
                ErrorType.TYPE_ERROR, "can't assign to nothing " + var_name, line_num
            )
        param = env.get(var_name)
        if param is not None:
            param_val, param_type = param
            if not self.__check_types(param_type, value):
                self.interpreter.error(
                    ErrorType.TYPE_ERROR, "incompatible types on assignment of " + var_name, line_num
                )
            if value.type() == Type.CLASS and value.value() is None and value.class_name() is None:
                value.set_class_name(param_type)
            env.set(var_name, (value, param_type))
            return

        if var_name not in self.fields:
            self.interpreter.error(
                ErrorType.NAME_ERROR, "unknown variable " + var_name, line_num
            )
        else:
            field_val, field_type = self.fields[var_name]
            if not self.__check_types(field_type, value):
                self.interpreter.error(
                    ErrorType.TYPE_ERROR, "incompatible types on assignment of " + var_name, line_num
                )
            if value.type() == Type.CLASS and value.value() is None and value.class_name() is None:
                value.set_class_name(field_type)
            self.fields[var_name] = value, field_type

    # (if expression (statement) (statement) ) where expresion could be a boolean constant (e.g., true), member
    # variable without ()s, or a boolean expression in parens, like (> 5 a)
    def __execute_if(self, env, code):
        condition = self.__evaluate_expression(env, code[1], code[0].line_num)
        if condition.type() != Type.BOOL:
            self.interpreter.error(
                ErrorType.TYPE_ERROR,
                "non-boolean if condition " + ' '.join(x for x in code[1]),
                code[0].line_num,
            )
        if condition.value():
            status, return_value = self.__execute_statement(
                env, code[2]
            )  # if condition was true
            return status, return_value
        if len(code) == 4:
            status, return_value = self.__execute_statement(
                env, code[3]
            )  # if condition was false, do else
            return status, return_value
        return ObjectDef.STATUS_PROCEED, None

    # (while expression (statement) ) where expresion could be a boolean value, boolean member variable,
    # or a boolean expression in parens, like (> 5 a)
    def __execute_while(self, env, code):
        while True:
            condition = self.__evaluate_expression(env, code[1], code[0].line_num)
            if condition.type() != Type.BOOL:
                self.interpreter.error(
                    ErrorType.TYPE_ERROR,
                    "non-boolean while condition " + ' '.join(x for x in code[1]),
                    code[0].line_num,
                )
            if not condition.value():  # condition is false, exit loop immediately
                return ObjectDef.STATUS_PROCEED, None
            # condition is true, run body of while loop
            status, return_value = self.__execute_statement(env, code[2])
            if status == ObjectDef.STATUS_RETURN:
                return (
                    status,
                    return_value,
                )  # could be a valid return of a value or an error

    # given an expression, return a Value object with the expression's evaluated result
    # expressions could be: constants (true, 5, "blah"), variables (e.g., x), arithmetic/string/logical expressions
    # like (+ 5 6), (+ "abc" "def"), (> a 5), method calls (e.g., (call me foo)), or instantiations (e.g., new dog_class)
    def __evaluate_expression(self, env, expr, line_num_of_statement):
        if not isinstance(expr, list):
            # locals shadow member variables
            if expr == InterpreterBase.ME_DEF:
                return ClassValue(Type.CLASS, self, self.class_name)
            val = env.get(expr)
            if val is not None:
                return val[0]
            if expr in self.fields:
                return self.fields[expr][0]
            # need to check for variable name and get its value too
            value = create_value(expr)
            if value is not None:
                return value
            self.interpreter.error(
                ErrorType.NAME_ERROR,
                "invalid field or parameter " + expr,
                line_num_of_statement,
            )

        operator = expr[0]
        if operator in self.binary_op_list:
            operand1 = self.__evaluate_expression(env, expr[1], line_num_of_statement)
            operand2 = self.__evaluate_expression(env, expr[2], line_num_of_statement)
            if operand1.type() == operand2.type() and operand1.type() == Type.INT:
                if operator not in self.binary_ops[Type.INT]:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid operator applied to ints",
                        line_num_of_statement,
                    )
                return self.binary_ops[Type.INT][operator](operand1, operand2)
            if operand1.type() == operand2.type() and operand1.type() == Type.STRING:
                if operator not in self.binary_ops[Type.STRING]:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid operator applied to strings",
                        line_num_of_statement,
                    )
                return self.binary_ops[Type.STRING][operator](operand1, operand2)
            if operand1.type() == operand2.type() and operand1.type() == Type.BOOL:
                if operator not in self.binary_ops[Type.BOOL]:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid operator applied to bool",
                        line_num_of_statement,
                    )
                return self.binary_ops[Type.BOOL][operator](operand1, operand2)
            if operand1.type() == operand2.type() and operand1.type() == Type.CLASS:
                if operator not in self.binary_ops[Type.CLASS]:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid operator applied to class",
                        line_num_of_statement,
                    )
                if operand1.class_name() is None or operand2.class_name() is None:
                    return self.binary_ops[Type.CLASS][operator](operand1, operand2)
                op1_hierarchy = self.interpreter.class_index[operand1.class_name()].class_hierarchy
                op2_hierarchy = self.interpreter.class_index[operand2.class_name()].class_hierarchy
                if operand1.class_name() in op2_hierarchy or operand2.class_name() in op1_hierarchy:
                    return self.binary_ops[Type.CLASS][operator](operand1, operand2)

            # error what about an obj reference and null
            self.interpreter.error(
                ErrorType.TYPE_ERROR,
                f"operator {operator} applied to two incompatible types",
                line_num_of_statement,
            )
        if operator in self.unary_op_list:
            operand = self.__evaluate_expression(env, expr[1], line_num_of_statement)
            if operand.type() == Type.BOOL:
                if operator not in self.unary_ops[Type.BOOL]:
                    self.interpreter.error(
                        ErrorType.TYPE_ERROR,
                        "invalid unary operator applied to bool",
                        line_num_of_statement,
                    )
                return self.unary_ops[Type.BOOL][operator](operand)

        # handle call expression: (call objref methodname p1 p2 p3)
        if operator == InterpreterBase.CALL_DEF:
            return self.__execute_call_aux(env, expr, line_num_of_statement)
        # handle new expression: (new classname)
        if operator == InterpreterBase.NEW_DEF:
            return self.__execute_new_aux(env, expr, line_num_of_statement)

    # (new classname)
    def __execute_new_aux(self, _, code, line_num_of_statement):
        obj = self.interpreter.instantiate(code[1], line_num_of_statement)
        return ClassValue(Type.CLASS, obj, code[1])

    # this method is a helper used by call statements and call expressions
    # (call object_ref/me methodname p1 p2 p3)
    def __execute_call_aux(self, env, code, line_num_of_statement):
        # determine which object we want to call the method on
        obj_name = code[1]
        if obj_name == InterpreterBase.ME_DEF:
            obj = self
        else:
            obj = self.__evaluate_expression(
                env, obj_name, line_num_of_statement
            ).value()
        # prepare the actual arguments for passing
        if obj is None:
            self.interpreter.error(
                ErrorType.FAULT_ERROR, "null dereference", line_num_of_statement
            )
        actual_args = []
        for expr in code[3:]:
            actual_args.append(
                self.__evaluate_expression(env, expr, line_num_of_statement)
            )
        return obj.call_method(code[2], actual_args, line_num_of_statement)

    def __map_method_names_to_method_definitions(self):
        self.methods = {}
        for name, method in self.class_def.get_methods().items():
            self.methods[name] = method

    def __map_fields_to_values(self):
        self.fields = {}
        for name, field in self.class_def.get_fields().items():
            self.fields[name] = (create_value(field.default_field_value, field.field_type), field.field_type)

    def __map_methods_to_fields(self):
        curr_class = self.class_def
        self.methods = {}
        self.method_field_map = {}
        while curr_class is not None:
            for name, method in curr_class.get_methods().items():
                self.methods[name] = method
                self.method_field_map[name] = curr_class.get_fields()
            curr_class = curr_class.superclass
        
        print(self.method_field_map)
    def __create_map_of_operations_to_lambdas(self):
        self.binary_op_list = [
            "+",
            "-",
            "*",
            "/",
            "%",
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
            "&",
            "|",
        ]
        self.unary_op_list = ["!"]
        self.binary_ops = {}
        self.binary_ops[Type.INT] = {
            "+": lambda a, b: Value(Type.INT, a.value() + b.value()),
            "-": lambda a, b: Value(Type.INT, a.value() - b.value()),
            "*": lambda a, b: Value(Type.INT, a.value() * b.value()),
            "/": lambda a, b: Value(
                Type.INT, a.value() // b.value()
            ),  # // for integer ops
            "%": lambda a, b: Value(Type.INT, a.value() % b.value()),
            "==": lambda a, b: Value(Type.BOOL, a.value() == b.value()),
            "!=": lambda a, b: Value(Type.BOOL, a.value() != b.value()),
            ">": lambda a, b: Value(Type.BOOL, a.value() > b.value()),
            "<": lambda a, b: Value(Type.BOOL, a.value() < b.value()),
            ">=": lambda a, b: Value(Type.BOOL, a.value() >= b.value()),
            "<=": lambda a, b: Value(Type.BOOL, a.value() <= b.value()),
        }
        self.binary_ops[Type.STRING] = {
            "+": lambda a, b: Value(Type.STRING, a.value() + b.value()),
            "==": lambda a, b: Value(Type.BOOL, a.value() == b.value()),
            "!=": lambda a, b: Value(Type.BOOL, a.value() != b.value()),
            ">": lambda a, b: Value(Type.BOOL, a.value() > b.value()),
            "<": lambda a, b: Value(Type.BOOL, a.value() < b.value()),
            ">=": lambda a, b: Value(Type.BOOL, a.value() >= b.value()),
            "<=": lambda a, b: Value(Type.BOOL, a.value() <= b.value()),
        }
        self.binary_ops[Type.BOOL] = {
            "&": lambda a, b: Value(Type.BOOL, a.value() and b.value()),
            "|": lambda a, b: Value(Type.BOOL, a.value() or b.value()),
            "==": lambda a, b: Value(Type.BOOL, a.value() == b.value()),
            "!=": lambda a, b: Value(Type.BOOL, a.value() != b.value()),
        }
        self.binary_ops[Type.CLASS] = {
            "==": lambda a, b: Value(Type.BOOL, a.value() is b.value()),
            "!=": lambda a, b: Value(Type.BOOL, a.value() is not b.value()),
        }

        self.unary_ops = {}
        self.unary_ops[Type.BOOL] = {
            "!": lambda a: Value(Type.BOOL, not a.value()),
        }
