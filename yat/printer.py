from yat.model import *


class ExpressionTerm:
    def visit(self, obj):
        return obj.access(self)

    def visit_number(self, num):
        return str(num.value)

    def visit_reference(self, ref):
        return ref.name

    def visit_unary(self, unary):
        ret = unary.op + unary.expr.access(self)
        if unary.op == '-' or unary.expr.is_below_zero():
            ret = "(" + ret + ")"
        return ret

    def visit_binary(self, binary):
        left = binary.lhs.access(self)
        right = binary.rhs.access(self)
        if binary.lhs.is_below_zero():
            left = "(" + left + ")"
        if binary.rhs.is_below_zero():
            right = "(" + right + ")"

        return  left + " " + binary.op + " " + right


class PrettyPrinter:
    expTrm = ExpressionTerm()

    def visit(self, obj):
        for line in obj.access(self):
            print(line)

    def visit_number(self, num):
        return [self.expTrm.visit(num) + ";"]

    def visit_print(self, prnt):
        return ["print " + self.expTrm.visit(prnt.expr) + ";"]

    def visit_read(self, rd):
        return ["read " + rd.name + ';']

    def visit_conditional(self, cond):
        ret = ["if (" + self.expTrm.visit(cond.condition) + ") {"] + \
              cond.if_true.access(self)
        if cond.if_false.exprs:
            ret += ["} else {"] + cond.if_false.access(self)
        ret += ["};"]
        return ret

    def visit_definition(self, defin):
        ret = ["def " + defin.name + "("
               + ", ".join(defin.function.args)
               + ") {"]
        ret += defin.function.body.access(self) + ["};"]
        return ret

    def visit_exprlist(self, exprlist):
        ret = []
        for line in exprlist.exprs:
            ret += line.access(self)
        return ["\t" + line for line in ret]

    def visit_reference(self, ref):
        return [self.expTrm.visit(ref) + ";"]

    def visit_binary(self, binary):
        return [self.expTrm.visit(binary) + ";"]

    def visit_unary(self, unary):
        return [self.expTrm.visit(unary) + ';']

    def visit_call(self, call):
        ret = [self.expTrm.visit(call.fun_expr) + "("
               + ", ".join(self.expTrm.visit(arg) for arg in call.args) + ");"]
        return ret

