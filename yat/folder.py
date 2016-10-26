from yat.model import *


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
        return ExprList(list(map(self.simplify, expr_list.exprs)))

    def visit_conditional(self, cond):
        return Conditional(self.simplify(cond.condition),
                           self.simplify(cond.if_true).exprs,
                           self.simplify(cond.if_false.exprs)
                           )

    def visit_read(self, read):
        return Read(read.name)

    def visit_print(self, pr):
        return Print(pr.expr.access(self))

    def visit_reference(self, ref):
        return Reference(ref.name)
