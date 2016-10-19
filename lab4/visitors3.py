#!/usr/bin/env python3

# Шаблон для домашнѣго задания
# Рѣализуйте мѣтоды с raise NotImplementedError


class PartialEnum:
    beg = ''
    end = ''
    sep = ' '


class SentenceEnum:
    beg = '\t'
    end = ';\n'
    sep = '\n'


class ArgsEnum:
    beg = ''
    end = ''
    sep = ', '


class Operator:
    def access(self, visitor):
        visitor.step_in()
        visitor.visit(self)
        visitor.step_out()


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
        if item in self.__field:
            return self.__field[item]
        return self.__parent[item]

    def __setitem__(self, key, value):
        self.__field[key] = value

    def __init__(self, parent=None):
        self.__field = dict()
        self.__parent = parent


class Number(Operator):
    """Number - представляет число в программе.
    Все числа в нашем языке целые."""

    def __init__(self, value):
        self.value = value

    def evaluate(self, scope=None):
        return self


class Function(Operator):
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
        self.body = ExprList(body)

    def evaluate(self, scope):
        return self.body.evaluate(scope)


class ExprList(Operator):
    """ExprList - список выражений для вычисления в текущем scope
        Возвращает значение последнего вычисления.
        Если список выражений был пуст - вернет None
    """

    def __init__(self, exprs):
        self.exprs = exprs

    def evaluate(self, scope=None):
        cur = None
        if self.exprs:
            for expr in self.exprs:
                cur = expr.evaluate(scope)
        return cur


class FunctionDefinition(Operator):
    """FunctionDefinition - представляет определение функции,
    т. е. связывает некоторое имя с объектом Function.
    Результатом вычисления FunctionDefinition является
    обновление текущего Scope - в него
    добавляется новое значение типа Function."""

    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope=None):
        scope[self.name] = self.function
        return self.function


class Conditional(Operator):
    """
    Conditional - представляет ветвление в программе, т. е. if.
    """

    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = ExprList(if_true)
        self.if_false = ExprList(if_false)

    def evaluate(self, scope=None):
        if self.condition.evaluate(scope).value:
            return self.if_true.evaluate(scope)
        else:
            return self.if_false.evaluate(scope)


class Print(Operator):
    """Print - печатает значение выражения на отдельной строке."""

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope=None):
        obj = self.expr.evaluate(scope)
        print(obj.value)
        return obj


class Read(Operator):
    """Read - читает число из стандартного потока ввода
     и обновляет текущий Scope.
     Каждое входное число располагается на отдельной строке
     (никаких пустых строк и лишних символов не будет).
     """

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope=None):
        scope[self.name] = Number(int(input()))
        return scope[self.name]


class FunctionCall(Operator):
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

    def evaluate(self, scope=None):
        func = self.fun_expr.evaluate(scope)
        f_scope = Scope(scope)
        for arg, val in zip(func.args,
                            [expr.evaluate(f_scope) for expr in self.args]):
            f_scope[arg] = val
        return func.evaluate(f_scope)


class Reference(Operator):
    """Reference - получение объекта
    (функции или переменной) по его имени."""

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope=None):
        return scope[self.name]


class BinaryOperation(Operator):
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

    def evaluate(self, scope=None):
        return self.__ops[self.op](self.lhs.evaluate(scope),
                                   self.rhs.evaluate(scope))


class UnaryOperation(Operator):
    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    __ops = {'!': lambda x: Number(not x.value),
             '-': lambda x: Number(-x.value)
             }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope=None):
        return self.__ops[self.op](self.expr.evaluate(scope))


class OperatorVisitor:
    def visit(self, op):
        name = op.__class__.__name__
        try:
            fn = getattr(self, 'visit' + name)
        except AttributeError:
            print("Method for {} not found!".format(name))
            raise NotImplementedError
        return fn(op)

    def step_in(self):
        pass

    def step_out(self):
        pass

class ExpressionPrinter(OperatorVisitor):
    enclosingPriority = -1
    enclosingComm = True

    @staticmethod
    def param_wrapper( ):

    def visitNumber(self, num):
        print(num.value)


class PrettyPrinter(OperatorVisitor):
    expPrnt = ExpressionPrinter()
    def visitNumber(self, num):


class ConstantFolder(OperatorVisitor):
    @staticmethod
    def is_constant(obj):
        return isinstance(obj, Number)

    @staticmethod
    def is_zero(obj):
        return isinstance(obj, Number) and obj.value == 0

    @staticmethod
    def name(obj):
        if isinstance(obj, Reference):
            return obj.name

    def simplify(self, obj):
        try:
            return obj.access(self)
        except AttributeError:
            return obj

    def visitNumber(self, num):
        return Number(num.value)

    def visitBinaryOperation(self, bin_op):
        ret = BinaryOperation(self.simplify(bin_op.lhs),
                              bin_op.op,
                              self.simplify(bin_op.rhs))
        if self.is_constant(ret.lhs) and self.is_constant(ret.rhs):
            ret = bin_op.evaluate()
        if self.is_zero(ret.lhs) or self.is_zero(ret.rhs):
            ret = Number(0)
        if self.name(bin_op.lhs) == self.name(bin_op.rhs) and self.name(bin_op.rhs):
            if bin_op.op in ['-', '%', '!=', '<', '>']:
                return Number(0)
            if bin_op.op in ['/', '==', '<=', '>=']:
                return Number(1)
        return ret

    def visitUnaryOperator(self, un_op):
        ret = UnaryOperation(un_op.op, self.simplify(un_op.expr))
        if self.is_constant(un_op.expr):
            ret = un_op.evaluate()
        return ret

    def visitFunctionCall(self, call):
        return FunctionCall(self.simplify(call.fun_expr),
                            map(self.simplify, call.args))

    def visitFunction(self, function):
        return Function(map(self.simplify, function.args),
                        self.simplify(function.body()))

    def visitFunctionDefinition(self, f_def):
        return FunctionDefinition(self.simplify(f_def.name), self.simplify(f_def.function))

    def visitExprList(self, expr_list):
        return ExprList(map(self.simplify, expr_list.exprs))

    def visitConditional(self, cond):
        return Conditional(self.simplify(cond.condition),
                           self.simplify(cond.if_true),
                           self.simplify(cond.if_false)
                           )

    def visitRead(self, read):
        return Read(read.access(self))

    def visitPrint(self, pr):
        return Print(pr.access(self))

    def visitReference(self, ref):
        return Reference(ref.name)

def example():
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    scope["bar"] = Number(20)
    # print('It should print 2: ', end=' ')
    call = FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))])
    printer = PrettyPrinter()
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
                                                   field["a"])])
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


if __name__ == '__main__':
    #example()
    #my_tests_cond()
    #my_tests_binary()
    #my_tests_unary()
    #my_tests_hard()
