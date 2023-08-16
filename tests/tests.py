# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import pathlib
import tempfile
from unittest import SkipTest, TestCase, main, skip

from ulkb import *


def skip_if_not_set(var):
    import os
    if not os.getenv(var, None):
        raise SkipTest(f'{var} not set')


class ULKB_TestCase(TestCase):

    # -- Object ------------------------------------------------------------

    def assert_object(self, obj, args, kwargs={}):
        self.assertIsInstance(obj, Object)
        self.assertIsInstance(args, (tuple, list))
        self.assertIsInstance(kwargs, dict)
        self.assertTrue(obj.is_object())
        self.assertTrue(obj.test_object())
        self.assertEqual(obj.check_object(), obj)
        self.assertEqual(obj.unfold_object(), args)
        self.assertEqual(obj.unfold_object_unsafe(), args)
        self.assertEqual(obj.unpack_object(), args)
        self.assertEqual(obj.unpack_object_unsafe(), args)
        self.assertEqual(len(obj), len(args))
        self.assertEqual(obj.annotations, kwargs)

    def assert_deep_equal(self, x, y):
        self.assertIsInstance(x, Object)
        self.assertIsInstance(y, Object)
        self.assertEqual(x, y)
        self.assertTrue(x.equal(y, deep=True))

    def assert_equal_but_not_deep_equal(self, x, y):
        self.assertIsInstance(x, Object)
        self.assertIsInstance(y, Object)
        self.assertEqual(x, y)
        self.assertFalse(x.equal(y, deep=True))

    # -- Theory ------------------------------------------------------------

    def assert_theory(self, obj, args, kwargs={}):
        self.assert_object(obj, args, kwargs)
        self.assertIsInstance(obj, Theory)
        self.assertTrue(obj.is_theory())
        self.assertTrue(obj.test_theory())
        self.assertEqual(obj.check_theory(), obj)
        self.assertEqual(obj.unfold_theory(), args)
        self.assertEqual(obj.unpack_theory(), args)

    # -- Extension ---------------------------------------------------------

    def assert_extension(self, obj, args, kwargs={}):
        self.assert_object(obj, args, kwargs)
        self.assertIsInstance(obj, Extension)
        self.assertTrue(obj.is_extension())
        self.assertTrue(obj.test_extension())
        self.assertEqual(obj.check_extension(), obj)
        self.assertEqual(obj.unfold_extension(), args)
        self.assertEqual(obj.unpack_extension(), args)

    def assert_assumption(self, obj, args, kwargs={}):
        self.assert_extension(obj, args, kwargs)
        self.assertIsInstance(obj, Assumption)
        self.assertTrue(obj.is_assumption())
        self.assertTrue(obj.test_assumption())
        self.assertEqual(obj.check_assumption(), obj)
        self.assertEqual(obj.unfold_assumption(), args)
        self.assertEqual(obj.unpack_assumption(), args)

    def assert_new_type_constructor(self, obj, args, kwargs={}):
        self.assert_assumption(obj, args, kwargs)
        self.assertIsInstance(obj, NewTypeConstructor)
        self.assertTrue(obj.is_new_type_constructor())
        self.assertTrue(obj.test_new_type_constructor())
        self.assertEqual(obj.check_new_type_constructor(), obj)
        self.assertEqual(obj.unfold_new_type_constructor(), args)
        self.assertEqual(obj.unpack_new_type_constructor(), args)
        self.assertEqual(obj.id, args[0].id)

    def assert_new_constant(self, obj, args, kwargs={}):
        self.assert_assumption(obj, args, kwargs)
        self.assertIsInstance(obj, NewConstant)
        self.assertTrue(obj.is_new_constant())
        self.assertTrue(obj.test_new_constant())
        self.assertEqual(obj.check_new_constant(), obj)
        self.assertEqual(obj.unfold_new_constant(), args)
        self.assertEqual(obj.unpack_new_constant(), args)
        self.assertEqual(obj.id, args[0].id)

    def assert_assertion(self, obj, args, kwargs={}):
        self.assert_extension(obj, args, kwargs)
        self.assertIsInstance(obj, Assertion)
        self.assertTrue(obj.is_assertion())
        self.assertTrue(obj.test_assertion())
        self.assertEqual(obj.check_assertion(), obj)
        self.assertEqual(obj.unfold_assertion(), args)
        self.assertEqual(obj.unpack_assertion(), args)

    def assert_new_axiom(self, obj, args, kwargs={}):
        self.assert_assumption(obj, args, kwargs)
        self.assertIsInstance(obj, NewAxiom)
        self.assertTrue(obj.is_new_axiom())
        self.assertTrue(obj.test_new_axiom())
        self.assertEqual(obj.check_new_axiom(), obj)
        self.assertEqual(obj.unfold_new_axiom(), args)
        self.assertEqual(obj.unpack_new_axiom(), args)
        self.assertEqual(obj.id, args[0].id)

    def assert_new_definition(self, obj, args, kwargs={}):
        self.assert_assertion(obj, args, kwargs)
        self.assertIsInstance(obj, NewDefinition)
        self.assertTrue(obj.is_new_definition())
        self.assertTrue(obj.test_new_definition())
        self.assertEqual(obj.check_new_definition(), obj)
        self.assertEqual(obj.unfold_new_definition(), args)
        self.assertEqual(obj.unpack_new_definition(), args)
        self.assertEqual(obj.id, args[0][0][1].id)

    def assert_new_theorem(self, obj, args, kwargs={}):
        self.assert_assertion(obj, args, kwargs)
        self.assertIsInstance(obj, NewTheorem)
        self.assertTrue(obj.is_new_theorem())
        self.assertTrue(obj.test_new_theorem())
        self.assertEqual(obj.check_new_theorem(), obj)
        self.assertEqual(obj.unfold_new_theorem(), args)
        self.assertEqual(obj.unpack_new_theorem(), args)
        self.assertEqual(obj.id, args[0].id)

    def assert_notation(self, obj, args, kwargs={}):
        self.assert_extension(obj, args, kwargs)
        self.assertIsInstance(obj, Notation)
        self.assertTrue(obj.is_notation())
        self.assertTrue(obj.test_notation())
        self.assertEqual(obj.check_notation(), obj)
        self.assertEqual(obj.unfold_notation(), args)
        self.assertEqual(obj.unpack_notation(), args)

    def assert_new_python_type_alias(self, obj, args, kwargs={}):
        self.assert_notation(obj, args, kwargs)
        self.assertIsInstance(obj, NewPythonTypeAlias)
        self.assertTrue(obj.is_new_python_type_alias())
        self.assertTrue(obj.test_new_python_type_alias())
        self.assertEqual(obj.check_new_python_type_alias(), obj)
        self.assertEqual(obj.unfold_new_python_type_alias(), args)
        self.assertEqual(obj.unpack_new_python_type_alias(), args)

    # -- Expression --------------------------------------------------------

    def assert_expression(self, obj, args, kwargs={}):
        self.assert_object(obj, args, kwargs)
        self.assertIsInstance(obj, Expression)
        self.assertTrue(obj.is_expression())
        self.assertTrue(obj.test_expression())
        self.assertEqual(obj.check_expression(), obj)
        self.assertEqual(obj.unfold_expression(), args)
        self.assertEqual(obj.unpack_expression(), args)

    def assert_unfolded_args(self, obj, uargs):
        self.assertIsInstance(obj, Expression)
        self.assertIsInstance(uargs, tuple)
        self.assertEqual(obj.unfolded_args, uargs)

    def assert_type_constructors(self, obj, tcons):
        self.assertIsInstance(obj, Expression)
        self.assertIsInstance(tcons, set)
        self.assertEqual(obj.type_constructors, tcons)
        if tcons:
            self.assertTrue(obj.has_type_constructors())
        else:
            self.assertFalse(obj.has_type_constructors())

    def assert_type_variables(self, obj, tvars):
        self.assertIsInstance(obj, Expression)
        self.assertIsInstance(tvars, set)
        self.assertEqual(obj.type_variables, tvars)
        if tvars:
            self.assertTrue(obj.has_type_variables())
        else:
            self.assertFalse(obj.has_type_variables())

    # -- TypeConstructor ---------------------------------------------------

    def assert_type_constructor(self, obj, args, kwargs={}):
        self.assert_expression(obj, args, kwargs)
        self.assertIsInstance(obj, TypeConstructor)
        self.assertTrue(obj.is_type_constructor())
        self.assertTrue(obj.test_type_constructor())
        self.assertEqual(obj.check_type_constructor(), obj)
        self.assertEqual(obj.unfold_type_constructor(), args)
        self.assertEqual(obj.unpack_type_constructor(), args)
        self.assertEqual(obj.id, args[0])
        self.assertEqual(obj.arity, args[1])

    # -- Type --------------------------------------------------------------

    def assert_type(self, obj, args, kwargs={}):
        self.assert_expression(obj, args, kwargs)
        self.assertIsInstance(obj, Type)
        self.assertTrue(obj.is_type())
        self.assertTrue(obj.test_type())
        self.assertEqual(obj.check_type(), obj)
        self.assertEqual(obj.unfold_type(), args)
        self.assertEqual(obj.unpack_type(), args)

    def assert_type_variable(self, obj, args, kwargs={}):
        self.assert_type(obj, args, kwargs)
        self.assertIsInstance(obj, TypeVariable)
        self.assertTrue(obj.is_type_variable())
        self.assertTrue(obj.test_type_variable())
        self.assertEqual(obj.unfold_type_variable(), args)
        self.assertEqual(obj.unpack_type_variable(), args)
        self.assertEqual(obj.id, args[0])

    def assert_type_application(self, obj, args, unfold, kwargs={}):
        self.assert_type(obj, args, kwargs)
        self.assertIsInstance(obj, TypeApplication)
        self.assertTrue(obj.is_type_application())
        self.assertTrue(obj.test_type_application())
        self.assertEqual(obj.check_type_application(), obj)
        self.assertEqual(obj.unfold_type_application(), unfold)
        self.assertEqual(obj.unpack_type_application(), args)
        self.assertEqual(obj.head, obj[0])
        self.assertEqual(obj.tail, obj[1:])

    def assert_match(self, type, other, theta):
        self.assertEqual(type.match(other), theta)
        if theta is not None:
            self.assertTrue(type.matches(other))
        else:
            self.assertFalse(type.matches(other))

    # -- Term --------------------------------------------------------------

    def assert_term(self, obj, args, kwargs={}):
        self.assert_expression(obj, args, kwargs)
        self.assertIsInstance(obj, Term)
        self.assertTrue(obj.is_term())
        self.assertTrue(obj.test_term())
        self.assertEqual(obj.check_term(), obj)
        self.assertEqual(obj.unfold_term(), args)
        self.assertEqual(obj.unpack_term(), args)

    def assert_atomic_term(self, obj, args, kwargs={}):
        self.assert_term(obj, args, kwargs)
        self.assertIsInstance(obj, AtomicTerm)
        self.assertTrue(obj.is_atomic_term())
        self.assertTrue(obj.test_atomic_term())
        self.assertEqual(obj.check_atomic_term(), obj)
        self.assertEqual(obj.unfold_atomic_term(), args)
        self.assertEqual(obj.unpack_atomic_term(), args)
        self.assertEqual(obj.id, args[0])
        self.assertEqual(obj.type, args[1])

    def assert_variable(self, obj, args, kwargs={}):
        self.assert_atomic_term(obj, args, kwargs)
        self.assertIsInstance(obj, Variable)
        self.assertTrue(obj.is_variable())
        self.assertTrue(obj.test_variable())
        self.assertEqual(obj.check_variable(), obj)
        self.assertEqual(obj.unfold_variable(), args)
        self.assertEqual(obj.unpack_variable(), args)
        self.assertEqual(obj.id, args[0])
        self.assertEqual(obj.type, args[1])

    def assert_constant(self, obj, args, kwargs={}):
        self.assert_atomic_term(obj, args, kwargs)
        self.assertIsInstance(obj, Constant)
        self.assertTrue(obj.is_constant())
        self.assertTrue(obj.test_constant())
        self.assertEqual(obj.check_constant(), obj)
        self.assertEqual(obj.unfold_constant(), args)
        self.assertEqual(obj.unpack_constant(), args)
        self.assertEqual(obj.id, args[0])
        self.assertEqual(obj.type, args[1])

    def assert_compound_term(self, obj, args, type, kwargs={}):
        self.assert_term(obj, args, kwargs)
        self.assertIsInstance(obj, CompoundTerm)
        self.assertTrue(obj.is_compound_term())
        self.assertTrue(obj.test_compound_term())
        self.assertEqual(obj.check_compound_term(), obj)
        self.assertEqual(obj.unfold_compound_term(), args)
        self.assertEqual(obj.unpack_compound_term(), args)
        self.assertEqual(obj.left, args[0])
        self.assertEqual(obj.right, args[1])
        self.assertEqual(obj.type, type)

    def assert_application(self, obj, args, unfold, type, kwargs={}):
        self.assert_compound_term(obj, args, type, kwargs)
        self.assertIsInstance(obj, Application)
        self.assertTrue(obj.is_application())
        self.assertTrue(obj.test_application())
        self.assertEqual(obj.check_application(), obj)
        self.assertEqual(obj.unfold_application(), unfold)
        self.assertEqual(obj.unpack_application(), args)
        self.assertEqual(obj.left, args[0])
        self.assertEqual(obj.right, args[1])
        self.assertEqual(obj.type, type)

    def assert_beta_redex(self, obj, args, unfold, type, kwargs={}):
        self.assert_application(obj, args, unfold, type, kwargs)
        self.assertTrue(obj.is_beta_redex())
        self.assertTrue(obj.test_beta_redex())
        self.assertTrue(obj.check_beta_redex(), obj)
        self.assertTrue(obj.unfold_beta_redex(), obj.unfold_application())
        self.assertTrue(obj.unpack_beta_redex(), obj.unpack_beta_redex())

    def assert_abstraction(self, obj, args, unfold, type, kwargs={}):
        self.assert_compound_term(obj, args, type, kwargs)
        self.assertIsInstance(obj, Abstraction)
        self.assertTrue(obj.is_abstraction())
        self.assertTrue(obj.test_abstraction())
        self.assertEqual(obj.check_abstraction(), obj)
        self.assertEqual(obj.unfold_abstraction(), unfold)
        self.assertEqual(obj.unpack_abstraction(), args)
        self.assertEqual(obj.left, args[0])
        self.assertEqual(obj.right, args[1])
        self.assertEqual(obj.type, type)

    def assert_constants(self, obj, const):
        self.assertIsInstance(obj, Term)
        self.assertIsInstance(const, set)
        self.assertEqual(obj.get_constants(), const)
        self.assertEqual(obj.constants, const)
        if const:
            self.assertTrue(obj.has_constants())
        else:
            self.assertFalse(obj.has_constants())

    def assert_variables(self, obj, vars):
        self.assertIsInstance(obj, Term)
        self.assertIsInstance(vars, set)
        self.assertEqual(obj.get_variables(), vars)
        self.assertEqual(obj.variables, vars)
        if vars:
            self.assertTrue(obj.has_variables())
            for x in vars:
                self.assertTrue(x.occurs_in([obj]))
                self.assertTrue(obj.has_occurrence_of(x))
        else:
            self.assertFalse(obj.has_variables())

    def assert_bound_variables(self, obj, bound):
        self.assertIsInstance(obj, Term)
        self.assertIsInstance(bound, set)
        self.assertEqual(obj.get_bound_variables(), bound)
        self.assertEqual(obj.bound_variables, bound)
        if bound:
            self.assertTrue(obj.has_bound_variables())
            for x in bound:
                self.assertTrue(x.occurs_bound_in([obj]))
                self.assertTrue(obj.has_bound_occurrence_of(x))
        else:
            self.assertFalse(obj.has_bound_variables())

    def assert_free_variables(self, obj, free):
        self.assertIsInstance(obj, Term)
        self.assertIsInstance(free, set)
        self.assertEqual(obj.get_free_variables(), free)
        self.assertEqual(obj.free_variables, free)
        if free:
            self.assertTrue(obj.has_free_variables())
            for x in free:
                self.assertTrue(x.occurs_free_in([obj]))
                self.assertTrue(obj.has_free_occurrence_of(x))
        else:
            self.assertFalse(obj.has_free_variables())

    # -- BaseType ----------------------------------------------------------

    def assert_base_type(self, obj, args, kwargs={}):
        self.assert_type_application(obj, args, args, kwargs)
        self.assertTrue(obj.is_base_type())
        self.assertTrue(obj.test_base_type())
        self.assertEqual(obj.check_base_type(), obj)
        self.assertEqual(obj.unfold_base_type(), args)
        self.assertEqual(obj.unpack_base_type(), args)

    # -- BoolType ----------------------------------------------------------

    def assert_bool_type(self, obj, args, kwargs={}):
        self.assert_type_application(obj, args, args, kwargs)
        self.assertTrue(obj.is_bool_type())
        self.assertTrue(obj.test_bool_type())
        self.assertEqual(obj.check_bool_type(), obj)
        self.assertEqual(obj.unfold_bool_type(), args)
        self.assertEqual(obj.unpack_bool_type(), args)

    # -- FunctionType ------------------------------------------------------

    def assert_function_type(
            self, obj, args, unfold, unpack, kwargs={}):
        self.assert_type_application(obj, args, (args[0], *unfold), kwargs)
        self.assertTrue(obj.is_function_type())
        self.assertTrue(obj.test_function_type())
        self.assertEqual(obj.check_function_type(), obj)
        self.assertEqual(obj.unfold_function_type(), unfold)
        self.assertEqual(obj.unpack_function_type(), unpack)

    # -- Formula -----------------------------------------------------------

    def assert_formula(self, obj, args, kwargs={}):
        self.assert_term(obj, args, kwargs)
        self.assertTrue(obj.is_formula())
        self.assertTrue(obj.test_formula())
        self.assertEqual(obj.check_formula(), obj)
        self.assertEqual(obj.unfold_formula(), args)
        self.assertEqual(obj.unpack_formula(), args)
        self.assertEqual(obj.type, BoolType())

    # -- Equal -------------------------------------------------------------

    def assert_equal(self, obj, args, kwargs={}):
        self.assert_application(
            obj, args, (*args[0], args[1]), BoolType(), kwargs)
        self.assertTrue(obj.is_equal())
        self.assertTrue(obj.test_equal())
        self.assertEqual(obj.check_equal(), obj)
        self.assertEqual(obj.unfold_equal(), (args[0][1], args[1]))
        self.assertEqual(obj.unpack_equal(), (args[0][1], args[1]))
        self.assertEqual(obj[0][1].type, obj[1].type)
        self.assertEqual(
            obj[0][0].type,
            FunctionType(obj[0][1].type, obj[1].type, BoolType()))

    # -- Iff ---------------------------------------------------------------

    def assert_iff(self, obj, args, kwargs={}):
        self.assert_equal(obj, args, kwargs)
        self.assertTrue(obj.is_iff())
        self.assertTrue(obj.test_iff())
        self.assertEqual(obj.check_iff(), obj)
        self.assertEqual(obj.unfold_iff(), obj.unfold_equal())
        self.assertEqual(obj.unpack_iff(), obj.unpack_equal())
        self.assertEqual(obj[0][1].type, BoolType())
        self.assertEqual(obj[1].type, BoolType())
        self.assertEqual(obj.type, BoolType())

    # -- DefinedTerm -------------------------------------------------------

    def assert_defined_term(self, obj, args, kwargs={}):
        self.assert_term(obj, args, kwargs)
        self.assertTrue(obj.is_defined_term())
        self.assertTrue(obj.test_defined_term())
        self.assertEqual(obj.check_defined_term(), obj)
        self.assertEqual(obj.unfold_defined_term(), args)
        self.assertEqual(obj.unpack_defined_term(), args)

    def _assert_defined_helper(self, obj, cls):
        self.assertTrue(
            obj._thy().lookup_constant(obj.id).type.matches(obj.type))
        seq = obj._thy().lookup_definition(obj.id)
        self.assertTrue(len(seq.hypotheses) == 0)
        self.assertTrue(seq.conclusion.is_equal())
        l, r = seq.conclusion.unpack_equal()
        self.assertEqual(l, cls.constructor)
        self.assertEqual(l, cls.definiendum)
        self.assertEqual(r, cls.definiens)

    # -- DefinedConstant ---------------------------------------------------

    def assert_defined_constant(self, cls, obj, args, kwargs={}):
        self.assert_defined_term(obj, args, kwargs)
        self._assert_defined_helper(obj, cls)
        self.assert_constant(obj, args, kwargs)
        self.assertTrue(obj.is_defined_constant())
        self.assertTrue(obj.test_defined_constant())
        self.assertEqual(obj.check_defined_constant(), obj)
        self.assertEqual(obj.unfold_defined_constant(), args)
        self.assertEqual(obj.unpack_defined_constant(), args)

    # -- Truth -------------------------------------------------------------

    def assert_truth(self, obj, kwargs={}):
        args = (Truth().id, BoolType())
        self.assert_defined_constant(obj.Truth, obj, args, kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_truth())
        self.assertTrue(obj.test_truth())
        self.assertEqual(obj.check_truth(), obj)
        self.assertEqual(obj.unfold_truth(), args)
        self.assertEqual(obj.unpack_truth(), args)
        self.assertEqual(obj.type, BoolType())

    # -- Falsity -----------------------------------------------------------

    def assert_falsity(self, obj, kwargs={}):
        args = (Falsity().id, BoolType())
        self.assert_defined_constant(obj.Falsity, obj, args, kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_falsity())
        self.assertTrue(obj.test_falsity())
        self.assertEqual(obj.check_falsity(), obj)
        self.assertEqual(obj.unfold_falsity(), args)
        self.assertEqual(obj.unpack_falsity(), args)
        self.assertEqual(obj.type, BoolType())

    # -- DefinedPrefixOperator ---------------------------------------------

    def assert_defined_prefix_operator(
            self, cls, obj, args, type, kwargs={}):
        self.assert_defined_term(obj, args, kwargs)
        self.assert_application(obj, args, args, type, kwargs)
        const = obj.left
        self._assert_defined_helper(const, cls)
        self.assertTrue(obj.is_defined_prefix_operator())
        self.assertTrue(obj.test_defined_prefix_operator())
        self.assertEqual(obj.check_defined_prefix_operator(), obj)
        self.assertEqual(obj.unfold_defined_prefix_operator(), (args[1],))
        self.assertEqual(obj.unpack_defined_prefix_operator(), (args[1],))

    # -- Not ---------------------------------------------------------------

    def assert_not(self, obj, args, kwargs={}):
        self.assert_defined_prefix_operator(
            obj.Not, obj, args, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_not())
        self.assertTrue(obj.test_not())
        self.assertTrue(obj.check_not(), obj)
        self.assertTrue(obj.unfold_not(), args)
        self.assertTrue(obj.unpack_not(), args)
        self.assertTrue(obj.type, BoolType())

    # -- DefinedInfixOperator ----------------------------------------------

    def assert_defined_infix_operator(
            self, cls, obj, args, unpack, type, kwargs={}):
        self.assert_defined_term(obj, args, kwargs)
        self.assert_application(
            obj, args, obj.unfold_application(), type, kwargs)
        const = obj.left.left
        self._assert_defined_helper(const, cls)
        self.assertTrue(obj.is_defined_infix_operator())
        self.assertTrue(obj.test_defined_infix_operator())
        self.assertEqual(obj.check_defined_infix_operator(), obj)
        self.assertEqual(obj.unfold_defined_infix_operator(), unpack)
        self.assertEqual(obj.unpack_defined_infix_operator(), unpack)

    # -- And ---------------------------------------------------------------

    def assert_and(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_infix_operator(
            obj.And, obj, args, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_and())
        self.assertTrue(obj.test_and())
        self.assertTrue(obj.check_and(), obj)
        self.assertTrue(obj.unfold_and(), unfold)
        self.assertTrue(obj.unpack_and(), unpack)
        self.assertTrue(obj.type, BoolType())

    # -- Or ----------------------------------------------------------------

    def assert_or(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_infix_operator(
            obj.Or, obj, args, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_or())
        self.assertTrue(obj.test_or())
        self.assertTrue(obj.check_or(), obj)
        self.assertTrue(obj.unfold_or(), unfold)
        self.assertTrue(obj.unpack_or(), unpack)
        self.assertTrue(obj.type, BoolType())

    # -- Implies -----------------------------------------------------------

    def assert_implies(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_infix_operator(
            obj.Implies, obj, args, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_implies())
        self.assertTrue(obj.test_implies())
        self.assertTrue(obj.check_implies(), obj)
        self.assertTrue(obj.unfold_implies(), unpack)
        self.assertTrue(obj.unpack_implies(), unpack)
        self.assertTrue(obj.type, BoolType())

    # -- DefinedBinder -----------------------------------------------------

    def assert_defined_binder(
            self, cls, obj, args, unfold, unpack, type, kwargs={}):
        self.assert_defined_term(obj, args, kwargs)
        self.assert_application(
            obj, args, obj.unfold_application(), type, kwargs)
        const = obj.left
        self._assert_defined_helper(const, cls)
        self.assertTrue(obj.is_defined_binder())
        self.assertTrue(obj.test_defined_binder())
        self.assertEqual(obj.check_defined_binder(), obj)
        self.assertEqual(obj.unfold_defined_binder(), unfold)
        self.assertEqual(obj.unpack_defined_binder(), unpack)

    # -- Exists ------------------------------------------------------------

    def assert_exists(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_binder(
            obj.Exists, obj, args, unfold, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_exists())
        self.assertTrue(obj.test_exists())
        self.assertEqual(obj.check_exists(), obj)
        self.assertEqual(obj.unfold_exists(), unfold)
        self.assertEqual(obj.unpack_exists(), unpack)
        self.assertEqual(obj.type, BoolType())

    # -- Exists1 -----------------------------------------------------------

    def assert_exists1(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_binder(
            obj.Exists1, obj, args, unfold, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_exists1())
        self.assertTrue(obj.test_exists1())
        self.assertEqual(obj.check_exists1(), obj)
        self.assertEqual(obj.unfold_exists1(), unfold)
        self.assertEqual(obj.unpack_exists1(), unpack)
        self.assertEqual(obj.type, BoolType())

    # -- Forall ------------------------------------------------------------

    def assert_forall(self, obj, args, unfold, unpack, kwargs={}):
        self.assert_defined_binder(
            obj.Forall, obj, args, unfold, unpack, BoolType(), kwargs)
        self.assert_formula(obj, args, kwargs)
        self.assertTrue(obj.is_forall())
        self.assertTrue(obj.test_forall())
        self.assertEqual(obj.check_forall(), obj)
        self.assertEqual(obj.unfold_forall(), unfold)
        self.assertEqual(obj.unpack_forall(), unpack)
        self.assertEqual(obj.type, BoolType())

    # -- Sequent -----------------------------------------------------------

    def assert_sequent(self, obj, args, kwargs={}):
        self.assert_object(obj, args, kwargs)
        self.assertIsInstance(obj, Sequent)
        self.assertTrue(obj.is_sequent())
        self.assertTrue(obj.test_sequent())
        self.assertEqual(obj.check_sequent(), obj)
        self.assertEqual(obj.unfold_sequent(), args)
        self.assertEqual(obj.unpack_sequent(), args)
        self.assertEqual(obj.hypotheses, obj[0])
        self.assertEqual(obj.conclusion, obj[1])

    # -- Rule --------------------------------------------------------------

    def assert_rule(self, obj, args, kwargs={}):
        self.assert_sequent(obj, args, kwargs)
        self.assertTrue(obj.is_rule())
        self.assertTrue(obj.test_rule())
        self.assertEqual(obj.check_rule(), obj)
        self.assertEqual(obj.unfold_rule(), args)
        self.assertEqual(obj.unpack_rule(), args)

    # -- RuleAssume --------------------------------------------------------

    def assert_rule_assume(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_assume())
        self.assertTrue(obj.test_rule_assume())
        self.assertEqual(obj.check_rule_assume(), obj)
        self.assertEqual(obj.unfold_rule_assume(), args)
        self.assertEqual(obj.unpack_rule_assume(), args)

    # -- RuleRefl ----------------------------------------------------------

    def assert_rule_refl(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_refl())
        self.assertTrue(obj.test_rule_refl())
        self.assertEqual(obj.check_rule_refl(), obj)
        self.assertEqual(obj.unfold_rule_refl(), args)
        self.assertEqual(obj.unpack_rule_refl(), args)

    # -- RuleTrans ---------------------------------------------------------

    def assert_rule_trans(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_trans())
        self.assertTrue(obj.test_rule_trans())
        self.assertEqual(obj.check_rule_trans(), obj)
        self.assertEqual(obj.unfold_rule_trans(), args)
        self.assertEqual(obj.unpack_rule_trans(), args)

    # -- RuleMkComb --------------------------------------------------------

    def assert_rule_mk_comb(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_mk_comb())
        self.assertTrue(obj.test_rule_mk_comb())
        self.assertEqual(obj.check_rule_mk_comb(), obj)
        self.assertEqual(obj.unfold_rule_mk_comb(), args)
        self.assertEqual(obj.unpack_rule_mk_comb(), args)

    # -- RuleAbs -----------------------------------------------------------

    def assert_rule_abs(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_abs())
        self.assertTrue(obj.test_rule_abs())
        self.assertEqual(obj.check_rule_abs(), obj)
        self.assertEqual(obj.unfold_rule_abs(), args)
        self.assertEqual(obj.unpack_rule_abs(), args)

    # -- RuleBeta ----------------------------------------------------------

    def assert_rule_beta(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_beta())
        self.assertTrue(obj.test_rule_beta())
        self.assertEqual(obj.check_rule_beta(), obj)
        self.assertEqual(obj.unfold_rule_beta(), args)
        self.assertEqual(obj.unpack_rule_beta(), args)

    # -- RuleEqMP ----------------------------------------------------------

    def assert_rule_eq_mp(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_eq_mp())
        self.assertTrue(obj.test_rule_eq_mp())
        self.assertEqual(obj.check_rule_eq_mp(), obj)
        self.assertEqual(obj.unfold_rule_eq_mp(), args)
        self.assertEqual(obj.unpack_rule_eq_mp(), args)

    # -- RuleDeductAntisym -------------------------------------------------

    def assert_rule_deduct_antisym(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_deduct_antisym())
        self.assertTrue(obj.test_rule_deduct_antisym())
        self.assertEqual(obj.check_rule_deduct_antisym(), obj)
        self.assertEqual(obj.unfold_rule_deduct_antisym(), args)
        self.assertEqual(obj.unpack_rule_deduct_antisym(), args)

    # -- RuleInstType ------------------------------------------------------

    def assert_rule_inst_type(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_inst_type())
        self.assertTrue(obj.test_rule_inst_type())
        self.assertEqual(obj.check_rule_inst_type(), obj)
        self.assertEqual(obj.unfold_rule_inst_type(), args)
        self.assertEqual(obj.unpack_rule_inst_type(), args)

    # -- RuleSubst ---------------------------------------------------------

    def assert_rule_subst(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_subst())
        self.assertTrue(obj.test_rule_subst())
        self.assertEqual(obj.check_rule_subst(), obj)
        self.assertEqual(obj.unfold_rule_subst(), args)
        self.assertEqual(obj.unpack_rule_subst(), args)

    # -- DerivedRule -------------------------------------------------------

    def assert_derived_rule(self, obj, args, kwargs={}):
        self.assert_rule(obj, args, kwargs)
        self.assertTrue(obj.is_derived_rule())
        self.assertTrue(obj.test_derived_rule())
        self.assertEqual(obj.check_derived_rule(), obj)
        self.assertEqual(obj.unfold_derived_rule(), args)
        self.assertEqual(obj.unpack_derived_rule(), args)

    # -- RuleCut -----------------------------------------------------------

    def assert_rule_cut(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_cut())
        self.assertTrue(obj.test_rule_cut())
        self.assertEqual(obj.check_rule_cut(), obj)
        self.assertEqual(obj.unfold_rule_cut(), args)
        self.assertEqual(obj.unpack_rule_cut(), args)

    # -- RuleWeaken --------------------------------------------------------

    def assert_rule_weaken(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_weaken())
        self.assertTrue(obj.test_rule_weaken())
        self.assertEqual(obj.check_rule_weaken(), obj)
        self.assertEqual(obj.unfold_rule_weaken(), args)
        self.assertEqual(obj.unpack_rule_weaken(), args)

    # -- RuleApTerm --------------------------------------------------------

    def assert_rule_ap_term(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_ap_term())
        self.assertTrue(obj.test_rule_ap_term())
        self.assertEqual(obj.check_rule_ap_term(), obj)
        self.assertEqual(obj.unfold_rule_ap_term(), args)
        self.assertEqual(obj.unpack_rule_ap_term(), args)

    # -- RuleApThm ---------------------------------------------------------

    def assert_rule_ap_thm(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_ap_thm())
        self.assertTrue(obj.test_rule_ap_thm())
        self.assertEqual(obj.check_rule_ap_thm(), obj)
        self.assertEqual(obj.unfold_rule_ap_thm(), args)
        self.assertEqual(obj.unpack_rule_ap_thm(), args)

    # -- RuleSym -----------------------------------------------------------

    def assert_rule_sym(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_sym())
        self.assertTrue(obj.test_rule_sym())
        self.assertEqual(obj.check_rule_sym(), obj)
        self.assertEqual(obj.unfold_rule_sym(), args)
        self.assertEqual(obj.unpack_rule_sym(), args)

    # -- RuleAlpha ---------------------------------------------------------

    def assert_rule_alpha(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_alpha())
        self.assertTrue(obj.test_rule_alpha())
        self.assertEqual(obj.check_rule_alpha(), obj)
        self.assertEqual(obj.unfold_rule_alpha(), args)
        self.assertEqual(obj.unpack_rule_alpha(), args)

    # -- RuleAlphaRename ---------------------------------------------------

    def assert_rule_alpha_rename(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_alpha_rename())
        self.assertTrue(obj.test_rule_alpha_rename())
        self.assertEqual(obj.check_rule_alpha_rename(), obj)
        self.assertEqual(obj.unfold_rule_alpha_rename(), args)
        self.assertEqual(obj.unpack_rule_alpha_rename(), args)

    # -- RuleTruth ---------------------------------------------------------

    def assert_rule_truth(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_truth())
        self.assertTrue(obj.test_rule_truth())
        self.assertEqual(obj.check_rule_truth(), obj)
        self.assertEqual(obj.unfold_rule_truth(), args)
        self.assertEqual(obj.unpack_rule_truth(), args)

    # -- RuleEqTruthIntro --------------------------------------------------

    def assert_rule_eq_truth_intro(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_eq_truth_intro())
        self.assertTrue(obj.test_rule_eq_truth_intro())
        self.assertEqual(obj.check_rule_eq_truth_intro(), obj)
        self.assertEqual(obj.unfold_rule_eq_truth_intro(), args)
        self.assertEqual(obj.unpack_rule_eq_truth_intro(), args)

    # -- RuleEqTruthElim ---------------------------------------------------

    def assert_rule_eq_truth_elim(self, obj, args, kwargs={}):
        self.assert_derived_rule(obj, args, kwargs)
        self.assertTrue(obj.is_rule_eq_truth_elim())
        self.assertTrue(obj.test_rule_eq_truth_elim())
        self.assertEqual(obj.check_rule_eq_truth_elim(), obj)
        self.assertEqual(obj.unfold_rule_eq_truth_elim(), args)
        self.assertEqual(obj.unpack_rule_eq_truth_elim(), args)
