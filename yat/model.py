#!/usr/bin/env python3

# Шаблон для домашнѣго задания
# Рѣализуйте мѣтоды с raise NotImplementedError


class Operator:
    def access(self, visitor):
        raise NotImplementedError

    def is_below_zero(self):
        return True

    def is_zero(self):
        return False

    def is_constant(self):
        return False

    def get_name(self):
        return None

    def list_exists(self):
        return False


class Scope:
    def __getitem__(self, item):
        if item in self.__field:
            return self.__field[item]
        return self.__parent[item]

    def __setitem__(self, key, value):
        self.__field[key] = value

    def __init__(self, parent=None):
        self.__field = dict()
        self.__parent = parent


class Number(Operator):
    def __init__(self, value):
        self.value = int(value)

    def evaluate(self, scope=None):
        return self

    def is_zero(self):
        return self.value == 0

    def is_constant(self):
        return True

    def is_below_zero(self):
        return self.value < 0

    def access(self, visitor):
        return visitor.visit_number(self)


class ExprList(Operator):
    def __init__(self, exprs):
        self.exprs = exprs

    def evaluate(self, scope=None):
        cur = None
        if self.exprs:
            for expr in self.exprs:
                cur = expr.evaluate(scope)
        return cur

    def access(self, visitor):
        return visitor.visit_exprlist(self)

    def list_exists(self):
        return self.exprs is not None


class Function(Operator):
    def __init__(self, args, body):
        self.args = args
        self.body = ExprList(body)

    def evaluate(self, scope):
        return self.body.evaluate(scope)

    def access(self, visitor):
        return visitor.visit_function(self)


class FunctionDefinition(Operator):
    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope=None):
        scope[self.name] = self.function
        return self.function

    def access(self, visitor):
        return visitor.visit_definition(self)


class Conditional(Operator):
    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = ExprList(if_true)
        self.if_false = ExprList(if_false)

    def evaluate(self, scope=None):
        if self.condition.evaluate(scope).value:
            return self.if_true.evaluate(scope)
        else:
            return self.if_false.evaluate(scope)

    def access(self, visitor):
        return visitor.visit_conditional(self)


class Print(Operator):
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope=None):
        obj = self.expr.evaluate(scope)
        print(obj.value)
        return obj

    def access(self, visitor):
        return visitor.visit_print(self)


class Read(Operator):
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope=None):
        scope[self.name] = Number(int(input()))
        return scope[self.name]

    def access(self, visitor):
        return visitor.visit_read(self)


class FunctionCall(Operator):
    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope=None):
        func = self.fun_expr.evaluate(scope)
        f_scope = Scope(scope)
        for arg, val in zip(func.args,
                            [expr.evaluate(f_scope) for expr in self.args]):
            f_scope[arg] = val
        return func.evaluate(f_scope)

    def access(self, visitor):
        return visitor.visit_call(self)


class Reference(Operator):
    def __init__(self, name):
        self.name = name

    def is_below_zero(self):
        return False

    def evaluate(self, scope=None):
        return scope[self.name]

    def get_name(self):
        return self.name

    def access(self, visitor):
        return visitor.visit_reference(self)


class BinaryOperation(Operator):
    __ops = {'+': lambda x, y: Number(x.value + y.value),
             '-': lambda x, y: Number(x.value - y.value),
             '*': lambda x, y: Number(x.value * y.value),
             '/': lambda x, y: Number(x.value // y.value),
             '%': lambda x, y: Number(x.value % y.value),
             '==': lambda x, y: Number(x.value == y.value),
             '!=': lambda x, y: Number(x.value != y.value),
             '<': lambda x, y: Number(x.value < y.value),
             '>': lambda x, y: Number(x.value > y.value),
             '<=': lambda x, y: Number(x.value <= y.value),
             '>=': lambda x, y: Number(x.value >= y.value),
             '&&': lambda x, y: Number(x.value and y.value),
             '||': lambda x, y: Number(x.value or y.value),
             }

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def evaluate(self, scope=None):
        return self.__ops[self.op](self.lhs.evaluate(scope),
                                   self.rhs.evaluate(scope))

    def access(self, visitor):
        return visitor.visit_binary(self)


class UnaryOperation(Operator):
    __ops = {'!': lambda x: Number(not x.value),
             '-': lambda x: Number(-x.value)
             }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope=None):
        return self.__ops[self.op](self.expr.evaluate(scope))

    def access(self, visitor):
        return visitor.visit_unary(self)


def example():
    printer = PrettyPrinter()
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    scope["bar"] = Number(20)
    # print('It should print 2: ', end=' ')
    defin = FunctionDefinition('foo', parent['foo'])
    defin.evaluate(scope)
    printer.visit(defin)
    call = FunctionCall(Reference("foo"),
                        [Number(5), UnaryOperation('-', Number(3))])

    printer.visit(call)


def my_tests_cond():
    """
        checks if there if there are any problems
        in conditionals and scope inheritance
    """
    field1 = Scope()
    field1["a"] = Number(10)
    field1["b"] = Number(10)
    field1["c"] = Number(12)
    field1["cond"] = Conditional(BinaryOperation(BinaryOperation(Reference("a"), "==",
                                                                 Reference("b")), "&&",
                                                 Reference("c")),
                                 [Print(Reference("c")),
                                  Reference("a")
                                  ],
                                 [Print(Reference("a")),
                                  Reference("b")]
                                 )
    print("Should print 12 and 10: ")
    Print(field1["cond"]).evaluate(field1)
    field2 = Scope(field1)
    field2["b"] = Number(8)
    print("Should print 12 and 10: ")
    Print(field1["cond"]).evaluate(field1)
    print("Should print 12 and 8: ")
    Print(field1["cond"]).evaluate(field2)


def my_tests_binary():
    """
        tries all kinds of binary operations
    """
    field = Scope()
    field["b"] = Number(3)
    field["a"] = Number(10)
    print("Should print 37:", end=' ')
    Print(BinaryOperation(BinaryOperation(Reference("a"), '-',
                                          Reference("b")), '+',
                          BinaryOperation(Reference("a"), '*',
                                          Reference("b")))).evaluate(field)
    print("Should print False:", end=' ')
    Print(BinaryOperation(BinaryOperation(Reference("a"), '%',
                                          Reference("b")), '==',
                          BinaryOperation(Reference("a"), '/',
                                          Reference("b")))).evaluate(field)
    print("Should print True:", end=' ')
    Print(BinaryOperation(BinaryOperation(Reference("a"), '<',
                                          Reference("b")), '!=',
                          BinaryOperation(Reference("a"), '>',
                                          Reference("b")))).evaluate(field)
    print("Should print True:", end=' ')
    Print(BinaryOperation(BinaryOperation(Reference("a"), '<=',
                                          Reference("b")), '||',
                          BinaryOperation(Reference("a"), '>=',
                                          Reference("b")))).evaluate(field)
    print("Should print False:", end=' ')
    Print(BinaryOperation(BinaryOperation(Reference("a"), '<=',
                                          Reference("b")), '&&',
                          BinaryOperation(Reference("a"), '>=',
                                          Reference("b")))).evaluate(field)


def my_tests_unary():
    """
     checks all the unaries
    """
    field = Scope()
    field["b"] = Number(3)
    field["a"] = Number(0)
    field["foo"] = Function("a", [Print(Reference("a"))])
    fun = FunctionDefinition("func!", field["foo"])
    printer = PrettyPrinter()
    printer.visit(fun)
    print()
    #print("Should print 0:")
    call = FunctionCall(Reference("foo"), [UnaryOperation('-',
                                                   Reference("a"))])
    printer.visit(call)
    #print("Should print True:")
    call = FunctionCall(Reference("foo"), [UnaryOperation('!',
                                                   field["a"])])
    printer.visit(call)
    #print("Should print -3:")
    call = FunctionCall(Reference("foo"), [UnaryOperation('-',
                                                   field["b"])])
    printer.visit(call)
    #print("Should print False:")
    call = FunctionCall(Reference("foo"), [UnaryOperation('!',
                                                   field["b"])])


def my_tests_hard():
    """
        functions hell
    """
    field = Scope()
    field["a"] = Number(-100)
    field["b"] = Number(49)
    print("<<Print a number")
    Read("number").evaluate(field)
    print("prints everything you enter:")
    field["foo"] = Function(['divide', 'it'],
                            [FunctionCall(Reference("foo2"),
                                          [Read("number")]),
                             BinaryOperation(Reference("divide"), '/',
                                             UnaryOperation('-',
                                                            Reference("it")))]
                            )
    field["some_func"] = Function(['Why?'], [Print(Reference("Why?"))])
    FunctionDefinition('foo2', field["some_func"]).evaluate(field)
    print("<<print one more num")
    FunctionCall(Reference("foo"),
                 [Reference("a"),
                  UnaryOperation('-',
                                 Reference("b"))]).evaluate(field)
    print("Prints your num and then -3:")
    print("<<and one more")
    FunctionCall(Reference("foo2"),
                 [FunctionCall(Reference("foo"),
                               [UnaryOperation('-',
                                               Reference("a")),
                                Reference("b")])]).evaluate(field)
    print("The first number you entered:")
    Print(Reference("number")).evaluate(field)


def test():
    printer = PrettyPrinter()
    simplify = ConstantFolder()

    number = Number(42)
    conditional = Conditional(number, [], [])
    printer.visit(simplify.visit(conditional))

    function = Function([], [])
    definition = FunctionDefinition('foo', function)
    printer.visit(simplify.visit(definition))

    number = Number(42)
    print = Print(number)
    printer.visit(simplify.visit(print))

    read = Read('x')
    printer.visit(simplify.visit(read))

    ten = Number(10)
    printer.visit(simplify.visit(ten))

    reference = Reference('x')
    printer.visit(simplify.visit(reference))

    n0, n1, n2 = Number(1), Number(2), Number(3)
    add = BinaryOperation(n1, '+', n2)
    mul = BinaryOperation(n0, '*', add)
    printer.visit(simplify.visit(mul))

    number = Number(42)
    unary = UnaryOperation('-', number)
    printer.visit(simplify.visit(unary))

    reference = Reference('foo')
    call = FunctionCall(reference, [Number(1), Number(2), Number(3)])
    printer.visit(simplify.visit(call))

if __name__ == '__main__':
    example()
    # my_tests_cond()
    # my_tests_binary()
    # my_tests_unary()
    # my_tests_hard()
    test()
