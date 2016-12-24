#!/usr/bin/env python3


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


class Number:
    def __init__(self, value):
        self.value = int(value)

    def evaluate(self, scope=None):
        return self


class ExprList:
    def __init__(self, exprs):
        self.exprs = exprs

    def evaluate(self, scope=None):
        cur = None
        if self.exprs:
            for expr in self.exprs:
                cur = expr.evaluate(scope)
        return cur


class Function:
    def __init__(self, args, body):
        self.args = args
        self.body = ExprList(body)

    def evaluate(self, scope):
        return self.body.evaluate(scope)


class FunctionDefinition:
    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope=None):
        scope[self.name] = self.function
        return self.function


class Conditional:
    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = ExprList(if_true)
        self.if_false = ExprList(if_false)

    def evaluate(self, scope=None):
        if self.condition.evaluate(scope).value:
            return self.if_true.evaluate(scope)
        else:
            return self.if_false.evaluate(scope)


class Print:
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope=None):
        obj = self.expr.evaluate(scope)
        print(obj.value)
        return obj


class Read:
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope=None):
        scope[self.name] = Number(int(input()))
        return scope[self.name]


class FunctionCall:
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


class Reference:
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope=None):
        return scope[self.name]


class BinaryOperation:
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


class UnaryOperation:
    __ops = {'!': lambda x: Number(not x.value),
             '-': lambda x: Number(-x.value)
             }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope=None):
        return self.__ops[self.op](self.expr.evaluate(scope))
