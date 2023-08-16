# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..settings import Settings
from .converter import Converter


class ConverterZ3_Settings(Settings):
    pass


class ConverterZ3(
        Converter, format='z3', format_long='Z3',
        settings=ConverterZ3_Settings):

    def __init__(self, cls, arg, prove=None, simplify=None, solve=None,
                 **kwargs):
        import z3
        super().__init__(cls, arg, **kwargs)
        # settings
        self.settings = cls._thy().settings.converter.z3(**kwargs)
        # internal attributes
        self.z3 = z3
        self.prove = prove
        self.simplify = simplify
        self.solver = solve

    def do_convert_from(self):
        return self._do_convert_from(self.arg)

    def _do_convert_type_from(self, z3obj):
        if z3obj == self.z3.BoolSort():
            return self.cls.BoolType()
        else:
            return self.cls.BaseType(z3obj.name())

    def _do_convert_from(self, z3obj):
        if self.z3.is_sort(z3obj):
            return self._do_convert_type_from(z3obj)
        if self.z3.is_true(z3obj):
            return self.cls.Truth()
        elif self.z3.is_false(z3obj):
            return self.cls.Falsity()
        elif self.z3.is_eq(z3obj):
            args = z3obj.children()
            return self.cls.Equal(*map(self._do_convert_from, args))
        elif self.z3.is_not(z3obj):
            (t,) = z3obj.children()
            return self.cls.Not(self._do_convert_from(t))
        elif self.z3.is_and(z3obj):
            args = z3obj.children()
            return self.cls.And(*map(self._do_convert_from, args))
        elif self.z3.is_or(z3obj):
            args = z3obj.children()
            return self.cls.Or(*map(self._do_convert_from, args))
        elif self.z3.is_implies(z3obj):
            args = z3obj.children()
            return self.cls.Implies(*map(self._do_convert_from, args))
        elif self.z3.is_quantifier(z3obj):
            if z3obj.is_forall():
                pass
            elif z3obj.is_exists():
                pass
            else:
                raise self.error(f"cannot convert '{z3obj}'")
        elif self.z3.is_const(z3obj):
            name = str(z3obj)
            type = self._do_convert_type_from(z3obj.sort())
            if name[0] == '?':
                return self.cls.Variable(name[1:], type)
            else:
                return self.cls.Constant(name, type)
        else:
            raise self.error(f"cannot convert '{z3obj}'")

    def do_convert_to(self):
        z3obj = self._do_convert_to(self.arg)
        if self.prove:
            solver = self.z3.Solver()
            solver.add(self.z3.Not(z3obj))
            result = solver.check()
            if result == self.z3.unsat:
                return True
            elif result == self.z3.unknown:
                return None
            else:
                return False
        elif self.simplify:
            raise NotImplementedError
        elif self.solver is True:
            solver = self.z3.Solver()
            solver.add(z3obj)
            return solver
        elif self.solver is not None:
            self.solver.add(z3obj)
            return z3obj
        else:
            return z3obj

    def _do_convert_to(self, obj):
        if obj.is_type():
            return self._do_convert_type_to(obj)
        elif obj.is_truth():
            return self.z3.BoolVal(True)
        elif obj.is_falsity():
            return self.z3.BoolVal(False)
        elif obj.is_equal():
            l, r = obj.unfold_equal()
            return self._do_convert_to(l) == self._do_convert_to(r)
        elif obj.is_iff():
            error.should_not_get_here()  # handled above
        elif obj.is_not():
            (t,) = obj._unpack_not()
            return self.z3.Not(self._do_convert_to(t))
        elif obj.is_and():
            args = obj._unfold_and()
            return self.z3.And(*map(self._do_convert_to, args))
        elif obj.is_or():
            args = obj._unfold_or()
            return self.z3.Or(*map(self._do_convert_to, args))
        elif obj.is_implies():
            args = obj._unpack_implies()
            return self.z3.Implies(*map(self._do_convert_to, args))
        elif obj.is_exists():
            args = obj.unfold_exists()
            return self.z3.Exists(
                list(map(self._do_convert_to, args[:-1])),
                self._do_convert_to(args[-1]))
        elif obj.is_exists1():
            x, body = obj.unpack_exists1()
            y = x.get_variant_not_in([body])
            zx = self._do_convert_to(x)
            zy = self._do_convert_to(y)
            return self.z3.Exists(
                zx,
                self.z3.And(
                    self._do_convert_to(body),
                    self.z3.ForAll(
                        zy,
                        self.z3.Implies(
                            self._do_convert_to(body.substitute({x: y})),
                            zx == zy))))
        elif obj.is_forall():
            args = obj.unfold_forall()
            return self.z3.ForAll(
                list(map(self._do_convert_to, args[:-1])),
                self._do_convert_to(args[-1]))
        elif obj.is_application():
            op, *args = obj._unfold_application()
            return self._do_convert_to(op)(*map(self._do_convert_to, args))
        elif obj.is_abstraction():
            args = list(map(self._do_convert_to, obj._unfold_abstraction()))
            f = self.z3.RecFunction(
                f'({obj})', *map(lambda x: x.sort(), args))
            self.z3.RecAddDefinition(f, args[:-1], args[-1])
            return f
        elif obj.is_constant() or obj.is_variable():
            type = self._do_convert_type_to(obj.type)
            if not obj.is_variable():
                if isinstance(type, tuple):
                    if (obj == self.cls.RealType.ge
                            or obj == self.cls.IntType.ge):
                        return self.z3.ArithRef.__ge__
                    elif (obj == self.cls.RealType.gt
                          or obj == self.cls.IntType.gt):
                        return self.z3.ArithRef.__gt__
                    elif (obj == self.cls.RealType.le
                          or obj == self.cls.IntType.le):
                        return self.z3.ArithRef.__le__
                    elif (obj == self.cls.RealType.lt
                          or obj == self.cls.IntType.lt):
                        return self.z3.ArithRef.__lt__
                    else:
                        return self.z3.Function(obj.id, *type)
                elif isinstance(type, self.z3.ArithSortRef):
                    return type.cast(obj.id)
            return self.z3.Const(obj.id, type)
        elif obj.is_theory():
            solver = self.z3.Solver()
            it = filter(lambda x: x.is_new_axiom(), obj.args_no_prelude)
            for ax in it:
                solver.add(self._do_convert_to(ax[1]))
            return solver
        else:
            raise self.error(f"cannot convert '{obj}'")

    def _do_convert_type_to(self, obj):
        if obj.is_type_variable():
            return self.z3.DeclareSort(obj.id)
        elif obj.is_bool_type():
            return self.z3.BoolSort()
        elif obj.is_int_type():
            return self.z3.IntSort()
        elif obj.is_real_type():
            return self.z3.RealSort()
        elif obj.is_base_type():
            (tc,) = obj._unpack_base_type()
            return self.z3.DeclareSort(tc.id)
        elif obj.is_function_type():
            args = obj._unfold_function_type()
            if any(map(lambda x: isinstance(x, tuple), args)):
                raise ValueError(
                    f"unsupported function type '{z3obj}'")
            return tuple(map(self._do_convert_type_to, args))
        else:
            raise self.error(f"cannot convert '{obj}'")
