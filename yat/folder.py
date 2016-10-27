from yat.model import *
from yat.printer import *


class ConstantFolder:
    def simplify(self, obj):
        try:
            return obj.access(self)
        except AttributeError:
            return obj

    def visit(self, obj):
        return obj.access(self)

    def visit_number(self, num):
        return Number(num.value)

    def visit_binary(self, bin_op):
        ret = BinaryOperation(self.simplify(bin_op.lhs),
                              bin_op.op,
                              self.simplify(bin_op.rhs))
        if ret.lhs.is_constant() and ret.rhs.is_constant():
            return ret.evaluate()
        if ret.lhs.is_zero() or ret.rhs.is_zero():
            if ret.op in ['*', '/', '&&', '%']:
                return Number(0)
        if ret.lhs.get_name() == ret.rhs.get_name() and ret.rhs.get_name():
            if ret.op in ['-', '%', '!=', '<', '>']:
                return Number(0)
            if ret.op in ['/', '==', '<=', '>=']:
                return Number(1)
        return ret

    def visit_unary(self, un_op):
        ret = UnaryOperation(un_op.op, self.simplify(un_op.expr))
        if ret.expr.is_constant():
            ret = ret.evaluate()
        return ret

    def visit_call(self, call):
        return FunctionCall(self.simplify(call.fun_expr),
                            list(map(self.simplify, call.args)))

    def visit_function(self, function):
        return Function(list(map(self.simplify, function.args)),
                        self.simplify(function.body).exprs)

    def visit_definition(self, f_def):
        return FunctionDefinition(self.simplify(f_def.name), self.simplify(f_def.function))

    def visit_exprlist(self, expr_list):
        if expr_list.list_exists():
            return ExprList(list(map(self.simplify, expr_list.exprs)))
        return ExprList(None)

    def visit_conditional(self, cond):
        return Conditional(self.simplify(cond.condition),
                           self.simplify(cond.if_true).exprs,
                           self.simplify(cond.if_false).exprs
                           )

    def visit_read(self, read):
        return Read(read.name)

    def visit_print(self, pr):
        return Print(pr.expr.access(self))

    def visit_reference(self, ref):
        return Reference(ref.name)


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
    printer = PrettyPrinter()
    sim = ConstantFolder()
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

    cond = field1["cond"]
    printer.visit(sim.visit(cond))
    cond = Conditional(Reference("what"), [], [])
    printer.visit(sim.visit(cond))
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
    pass
    # example()
    # my_tests_cond()
    # my_tests_binary()
    # my_tests_unary()
    # my_tests_hard()
    # test()
