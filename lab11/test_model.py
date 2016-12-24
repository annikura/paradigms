#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock
import io
import sys

try:
    from model import *
except:
    from yat.model import *


class TestTemplate(unittest.TestCase):
    a = 42
    b = 1039
    c = -39

    def setUp(self):
        self.scope = Scope()
        self.scope["a"] = Number(self.a)
        self.scope["b"] = Number(self.b)
        self.scope["c"] = Number(self.c)
        self.scope["zero"] = Number(0)
        self.backup_out = sys.stdout
        self.backup_in = sys.stdin
        sys.stdout = io.StringIO()
        sys.stdin = io.StringIO(str(self.c))

    def tearDown(self):
        sys.stdout = self.backup_out
        sys.stdin = self.backup_in
        del self.scope
        del self.backup_out
        del self.backup_in

    def get_val(self, obj):
        Print(obj).evaluate(self.scope)
        ret = int(sys.stdout.getvalue())
        sys.stdout = io.StringIO()
        return ret


class NumberTest(TestTemplate):
    def test_Number_positive(self):
        self.assertEqual(self.get_val(Number(self.a)), self.a)

    def test_Number_zero(self):
        self.assertEqual(self.get_val(Number(0)), 0)

    def test_Number_negative(self):
        self.assertEqual(self.get_val(Number(self.c)), self.c)


class ScopeTest(TestTemplate):
    def test_Scope_inheritance_access(self):
        child = Scope(self.scope)
        self.assertIs(self.scope["a"], child["a"])

    def test_Scope_inheritance_overlay(self):
        child = Scope(self.scope)
        child["a"] = Number(self.a)
        self.assertIsNot(self.scope["a"], child["a"])


class PrintTest(TestTemplate):
    def test_print_positive(self):
        number = Number(self.a)
        number.evaluate = MagicMock(return_value=Number(self.a))
        self.assertEqual(self.get_val(number), self.a)

    def test_print_negative(self):
        number = Number(self.c)
        number.evaluate = MagicMock(return_value=Number(self.c))
        self.assertEqual(self.get_val(number), self.c)

    def test_print_return(self):
        number = Number(self.c)
        number.evaluate = MagicMock(return_value=Number(self.c))
        number = Print(number).evaluate(self.scope)
        sys.stdout = io.StringIO()
        self.assertEqual(self.get_val(number), self.c)


class ReadTest(TestTemplate):
    def test_read(self):
        self.assertEqual(self.get_val(Read("r").evaluate(self.scope)), self.c)


class ConditionalTest(TestTemplate):
    def test_false_empties(self):
        Conditional(Number(0), [], [])

    def test_true_empties(self):
        Conditional(Number(1), [], [])

    def test_false_nones(self):
        Conditional(Number(0), None, None)

    def test_true_nones(self):
        Conditional(Number(1), None, None)

    def test_false_comb1(self):
        Conditional(Number(0), None, [])

    def test_true_comb1(self):
        Conditional(Number(1), None, [])

    def test_false_comb2(self):
        Conditional(Number(0), None, [])

    def test_true_comb2(self):
        Conditional(Number(1), None, [])

    def test_true_none(self):
        self.assertEqual(self.get_val(Conditional(Number(1), [Number(self.a)], None)),
                         self.a)

    def test_false_none(self):
        self.assertEqual(self.get_val(Conditional(Number(0), None, [Number(self.a)])),
                         self.a)

    def test_true(self):
        self.assertEqual(self.get_val(Conditional(Number(1),
                                                  [Number(self.a), Number(self.c)],
                                                  [Number(self.b), Number(self.a)])),
                         self.c)

    def test_false(self):
        self.assertEqual(self.get_val(Conditional(Number(0),
                                                  [Number(self.c), Number(self.c)],
                                                  [Number(self.b), Number(self.a)])),
                         self.a)


class FunctionCallTest(TestTemplate):
    def test_empty(self):
        f = Function([], [])
        FunctionCall(FunctionDefinition("foo", f),
                     []).evaluate(self.scope)

    def test_scope_references(self):
        f = Function(["one", "two", "three", "a"], [Reference("one"), Reference("two")])
        self.assertEqual(self.get_val(FunctionCall(FunctionDefinition("foo", f),
                                                   [Number(1),
                                                    Number(2),
                                                    Number(3),
                                                    Number(self.a + 1)]).evaluate(self.scope)), 2)
        self.assertEqual(self.get_val(self.scope["a"]), self.a)


class ReferenceTest(TestTemplate):
    def test_reference(self):
        self.assertIs(Reference("a").evaluate(self.scope), self.scope["a"])


class BinaryOperationTest(TestTemplate):
    __ops = {'+': lambda x, y: x + y,
             '-': lambda x, y: x - y,
             '*': lambda x, y: x * y,
             '/': lambda x, y: x // y,
             '%': lambda x, y: x % y,
             '==': lambda x, y: x == y,
             '!=': lambda x, y: x != y,
             '<': lambda x, y: x < y,
             '>': lambda x, y: x > y,
             '<=': lambda x, y: x <= y,
             '>=': lambda x, y: x >= y,
             '&&': lambda x, y: x and y,
             '||': lambda x, y: x or y,
             }

    def test_binary(self):
        for op in self.__ops:
            for i in range(-10, 11):
                for j in range(-10, 11):
                    if j != 0:
                        self.assertEqual(self.get_val(BinaryOperation(Number(i), op, Number(j))),
                                         self.__ops[op](i, j))


class UnaryOperationTest(TestTemplate):
    __ops = {'!': lambda x: not x,
             '-': lambda x: -x
             }

    def test_unary(self):
        for op in self.__ops:
            for i in range(-10, 10):
                self.assertEqual(self.get_val(UnaryOperation(op, Number(i))),
                                 self.__ops[op](i))


class FunctionTest(TestTemplate):
    def test_empty(self):
        Function([], []).evaluate(self.scope)

    def test_empty_body(self):
        Function([Number(10), Number(5)], []).evaluate(self.scope)

    def test_empty_args(self):
        self.assertEqual(self.get_val(Function([],
                                               [Number(4),
                                                Number(7)]).evaluate(self.scope)),
                         7)

    def test_simple(self):
        self.assertEqual(self.get_val(Function(["a"],
                                               [Reference("a")]).evaluate(self.scope)),
                         self.a)

    def test_normal(self):
        self.assertEqual(self.get_val(Function(["a", "zero", "b"],
                                               [Reference("zero"),
                                                Reference("b")]).evaluate(self.scope)),
                         self.b)

    def test_numeral(self):
        self.assertEqual(self.get_val(Function(["a", "zero", "b"],
                                               [Reference("zero"),
                                                Reference("b"),
                                                Number(100500)]).evaluate(self.scope)),
                         100500)


class FunctionDefinitionTest(TestTemplate):
    def test_def(self):
        f = Function(["a"], [Number(10)])
        FunctionDefinition("function", f).evaluate(self.scope)
        self.assertIs(self.scope["function"], f)

if __name__ == "__main__":
    unittest.main()
