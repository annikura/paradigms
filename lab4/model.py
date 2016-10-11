#!/usr/bin/env python3

# Шаблон для домашнѣго задания
# Рѣализуйте мѣтоды с raise NotImplementedError


class Scope:
    """Scope - представляет доступ к значениям по именам
    (к функциям и именованным константам).
    Scope может иметь родителя, и если поиск по имени
    в текущем Scope не успешен, то если у Scope есть родитель,
    то поиск делегируется родителю.
    Scope должен поддерживать dict-like интерфейс доступа
    (см. на специальные функции __getitem__ и __setitem__)
    """

    def __getitem__(self, item):
        if item in self.field:
            return self.field[item]
        return self.__parent[item]

    def __setitem__(self, key, value):
        self.field[key] = value

    def __init__(self, parent=None):
        self.field = dict()
        self.__parent = parent


class Number:
    """Number - представляет число в программе.
    Все числа в нашем языке целые."""

    def __init__(self, value):
        self.value = value

    def evaluate(self, scope):
        return self


class Function:
    """Function - представляет функцию в программе.
    Функция - второй тип поддерживаемый языком.
    Функции можно передавать в другие функции,
    и возвращать из функций.
    Функция состоит из тела и списка имен аргументов.
    Тело функции это список выражений,
    т. е.  у каждого из них есть метод evaluate.
    Во время вычисления функции (метод evaluate),
    все объекты тела функции вычисляются последовательно,
    и результат вычисления последнего из них
    является результатом вычисления функции.
    Список имен аргументов - список имен
    формальных параметров функции."""

    def __init__(self, args, body):
        self.args = args
        self.body = body

    def evaluate(self, scope):
        return ExprList(self.body).evaluate(scope)


class ExprList:
    """ExprList - список выражений для вычисления в текущем scope
        Возвращает значение последнего вычисления.
        Если список выражений был пуст - вернет None
    """

    def __init__(self, exprs):
        self.exprs = exprs

    def evaluate(self, scope):
        cur = None
        if self.exprs:
            for expr in self.exprs:
                cur = expr.evaluate(scope)
        return cur


class FunctionDefinition:
    """FunctionDefinition - представляет определение функции,
    т. е. связывает некоторое имя с объектом Function.
    Результатом вычисления FunctionDefinition является
    обновление текущего Scope - в него
    добавляется новое значение типа Function."""

    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function


class Conditional:
    """
    Conditional - представляет ветвление в программе, т. е. if.
    """

    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def evaluate(self, scope):
        if self.condition.evaluate(scope).value:
            return ExprList(self.if_true).evaluate(scope)
        else:
            return ExprList(self.if_false).evaluate(scope)


class Print:
    """Print - печатает значение выражения на отдельной строке."""

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        obj = self.expr.evaluate(scope)
        print(obj.value)
        return obj


class Read:
    """Read - читает число из стандартного потока ввода
     и обновляет текущий Scope.
     Каждое входное число располагается на отдельной строке
     (никаких пустых строк и лишних символов не будет).
     """

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        scope[self.name] = Number(int(input()))
        return scope[self.name]


class FunctionCall:
    """
    FunctionCall - представляет вызов функции в программе.
    В результате вызова функции должен создаваться новый объект Scope,
    являющий дочерним для текущего Scope
    (т. е. текущий Scope должен стать для него родителем).
    Новый Scope станет текущим Scope-ом при вычислении тела функции.
    """

    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope):
        func = self.fun_expr.evaluate(scope)
        f_scope = Scope(scope)
        for arg, val in zip(func.args,
                            [expr.evaluate(f_scope) for expr in self.args]):
            f_scope[arg] = val
        return func.evaluate(f_scope)


class Reference:
    """Reference - получение объекта
    (функции или переменной) по его имени."""

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]


class BinaryOperation:
    """BinaryOperation - представляет бинарную операцию над двумя выражениями.
    Результатом вычисления бинарной операции является объект Number.
    Поддерживаемые операции:
    “+”, “-”, “*”, “/”, “%”, “==”, “!=”,
    “<”, “>”, “<=”, “>=”, “&&”, “||”."""

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

    def evaluate(self, scope):
        return self.__ops[self.op](self.lhs.evaluate(scope),
                                   self.rhs.evaluate(scope))


class UnaryOperation:
    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    __ops = {'!': lambda x: Number(not x.value),
             '-': lambda x: Number(-x.value)
             }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        return self.__ops[self.op](self.expr.evaluate(scope))


def example():
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    assert 10 == scope["bar"].value
    scope["bar"] = Number(20)
    assert scope["bar"].value == 20
    print('It should print 2: ', end=' ')
    FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))]).evaluate(scope)


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
    field["foo"] = Function(["a"], [Print(Reference("a"))])
    print("Should print 0:")
    FunctionCall(Reference("foo"), [UnaryOperation('-',
                                                   field["a"])]).evaluate(field)
    print("Should print True:")
    FunctionCall(Reference("foo"), [UnaryOperation('!',
                                                   field["a"])]).evaluate(field)
    print("Should print -3:")
    FunctionCall(Reference("foo"), [UnaryOperation('-',
                                                   field["b"])]).evaluate(field)
    print("Should print False:")
    FunctionCall(Reference("foo"), [UnaryOperation('!',
                                                   field["b"])]).evaluate(field)


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


if __name__ == '__main__':
    example()
    my_tests_cond()
    my_tests_binary()
    my_tests_unary()
    my_tests_hard()
