# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestSanity(ULKB_TestCase):

    def test_sanity(self):

        # -- Expression --

        tc0 = TypeConstructor('tc0', 0, i=1, j=2)
        self.assert_type_constructor(tc0, ('tc0', 0, None), {'i': 1, 'j': 2})

        tc1 = TypeConstructor('tc1', 1, abc='def')
        self.assert_type_constructor(tc1, ('tc1', 1, None), {'abc': 'def'})

        tc2 = TypeConstructor('tc2', 2, 'left')
        self.assert_type_constructor(tc2, ('tc2', 2, 'left'))

        tv = TypeVariable('tv', i=1, j=2)
        self.assert_type_variable(tv, ('tv',), {'i': 1, 'j': 2})

        tap0 = TypeApplication(tc0, i=1, j=2)
        self.assert_type_application(
            tap0, (TypeConstructor('tc0', 0),),
            (TypeConstructor('tc0', 0),), {'i': 1, 'j': 2})

        tap1 = TypeApplication(tc1, tap0, i=1, j=2)
        self.assert_type_application(
            tap1, (TypeConstructor('tc1', 1), tap0),
            (TypeConstructor('tc1', 1), tap0),
            {'i': 1, 'j': 2})

        tap2 = tc2(tap1, tv, i=1, j=2)
        self.assert_type_application(
            tap2,
            (TypeConstructor('tc2', 2, 'left'), tap1, TypeVariable('tv')),
            (TypeConstructor('tc2', 2, 'left'), tap1, TypeVariable('tv')),
            {'i': 1, 'j': 2})

        v0 = Variable('v0', tap0, i=1, j=2)
        self.assert_variable(v0, ('v0', tap0), {'i': 1, 'j': 2})

        v1 = Variable('v1', FunctionType(tap0, tap1, bool), i=1, j=2)
        self.assert_variable(
            v1, ('v1', FunctionType(tap0, tap1, bool)), {'i': 1, 'j': 2})

        c1 = Constant('c1', tap1, i=1, j=2)
        self.assert_constant(c1, ('c1', tap1), {'i': 1, 'j': 2})

        app0 = Application(v1, v0, c1, i=1, j=2)
        self.assert_application(
            app0, (v1(v0), c1), (v1, v0, c1), BoolType(), {'i': 1, 'j': 2})

        abs0 = Abstraction(v1, v0, c1, i=1, j=2)
        self.assert_abstraction(
            abs0, (v1, v0 >> c1), (v1, v0, c1),
            FunctionType(FunctionType(tap0, tap1, bool), tap0, tap1),
            {'i': 1, 'j': 2})

        # -- BoolType --

        abc = BaseType('abc')
        var = TypeVariable('var')

        tc_bool = TypeConstructor('bool', 0)
        self.assertEqual(lookup_type_constructor('bool'), tc_bool)
        self.assert_type_application(BoolType(), (tc_bool,), (tc_bool,))
        self.assert_type_application(
            TypeApplication(tc_bool), (tc_bool,), (tc_bool,))

        self.assert_bool_type(BoolType(), (tc_bool,))
        self.assert_bool_type(
            BoolType(i=1, j=2), (tc_bool,), {'i': 1, 'j': 2})
        self.assertTrue(BoolType().is_bool_type())
        self.assertTrue(Object.test_bool_type(BoolType()))
        self.assertFalse(tc_bool.is_bool_type())
        self.assertFalse(abc.is_bool_type())
        self.assertFalse(Object.test_bool_type(var))

        self.assertEqual(Object.check_bool_type(BoolType()), BoolType())
        self.assertEqual(BoolType().check_bool_type(), BoolType())
        self.assertRaises(TypeError, tc_bool.check_bool_type)
        self.assertRaises(TypeError, Expression.check_bool_type, tc_bool)
        self.assertRaises(TypeError, abc.check_bool_type)
        self.assertRaises(TypeError, Theory.check_bool_type, abc)
        self.assertRaises(TypeError, var.check_bool_type)
        self.assertRaises(TypeError, Type.check_bool_type, var)

        self.assertEqual(BoolType().unpack_bool_type(), (tc_bool,))
        self.assertRaises(TypeError, Expression.unpack_bool_type, var)
        self.assertRaises(TypeError, Expression.unpack_bool_type, abc)

        # -- FunctionType --

        abc = BaseType('abc')
        var = TypeVariable('var')

        tc_fun = TypeConstructor('fun', 2, 'right')
        self.assertEqual(lookup_type_constructor('fun'), tc_fun)
        self.assert_type_application(
            FunctionType(abc, var, i=1, j=2),
            (tc_fun, abc, var),
            (tc_fun, abc, var),
            {'i': 1, 'j': 2})

        self.assert_function_type(
            FunctionType(bool, bool, i=1, j=2),
            (tc_fun, BoolType(), BoolType()),
            (BoolType(), BoolType()),
            (BoolType(), BoolType()),
            {'i': 1, 'j': 2})
        fun = FunctionType(var, FunctionType(abc, bool))
        self.assertEqual(fun, FunctionType(var, abc, bool))
        self.assert_function_type(
            fun,
            (tc_fun, var, FunctionType(abc, bool)),
            (var, abc, tc_bool()),
            (var, FunctionType(abc, bool)))
        self.assert_function_type(
            fun[2],
            (tc_fun, abc, BoolType()),
            (abc, BoolType()),
            (abc, BoolType()))

        self.assertTrue(fun.is_function_type())
        self.assertTrue(Object.is_function_type(fun))
        self.assertFalse(abc.is_function_type())
        self.assertFalse(Theory.test_bool_type(var))

        self.assertEqual(fun.check_function_type(), fun)
        self.assertEqual(Type.check_function_type(fun), fun)
        self.assertRaises(TypeError, BoolType.check_function_type, BoolType)
        self.assertRaises(TypeError, abc.check_function_type)
        self.assertRaises(TypeError, abc.check_function_type)
        self.assertRaises(TypeError, Expression.check_function_type, var)

        self.assertEqual(
            fun.unpack_function_type(), (var, FunctionType(abc, bool)))
        self.assertRaises(TypeError, Theory.unpack_function_type, var)
        self.assertRaises(TypeError, Object.unpack_function_type, abc)

    def test_get_free_variables(self):
        a = TypeVariable('a')
        b = BaseType('b')
        c = Constant('x', a)
        f = Variable('f', type=FunctionType(a, bool))
        self.assertEqual(c.get_free_variables(), set())
        self.assertTrue(f.has_free_variables())
        self.assertEqual(f.get_free_variables(), {f})
        self.assertEqual(f(c).get_free_variables(), {f})
        self.assertEqual((f >> c).get_free_variables(), set())

    def test_has_free_occurrence_of(self):
        t = TypeVariable('t')
        a = Variable('a', t)
        b = Variable('b', t)
        c = Constant('c', t)
        f = Variable('f', type=FunctionType(t, bool))
        self.assertTrue(a.has_free_occurrence_of(a))
        self.assertFalse(c.has_free_occurrence_of(a))
        self.assertFalse(f.has_free_occurrence_of(a))
        self.assertFalse(f(c).has_free_occurrence_of(a))
        self.assertTrue(f(a).has_free_occurrence_of(a))
        self.assertFalse((a >> f(a)).has_free_occurrence_of(a))
        self.assertFalse(((a, b) >> f(a)).has_free_occurrence_of(a))
        self.assertTrue(((a, a, a) >> f(b)).has_free_occurrence_of(b))

    def test_get_type_constructors(self):
        a = TypeVariable('a')
        b = BaseType('b')
        c = Constant('x', a)
        f = Variable('f', type=FunctionType(a, bool))
        self.assertTrue(BoolType().has_type_constructors())
        self.assertEqual(
            BoolType().get_type_constructors(),
            {BoolType.constructor})
        self.assertFalse(a.has_type_constructors())
        self.assertEqual(a.get_type_constructors(), set())
        self.assertEqual(
            b.get_type_constructors(), {TypeConstructor('b', 0)})
        self.assertEqual(c.get_type_constructors(), set())
        self.assertEqual(
            f.get_type_constructors(),
            {BoolType.constructor, FunctionType.constructor})
        self.assertEqual(
            f(c).get_type_constructors(),
            {BoolType.constructor, FunctionType.constructor})
        self.assertEqual(
            f(f >> c).get_type_constructors(),
            {BoolType.constructor, FunctionType.constructor})

    def test_get_type_variables(self):
        a = TypeVariable('a')
        b = BaseType('b')
        c = Constant('x', a)
        f = Variable('f', type=FunctionType(a, bool))
        self.assertFalse(BoolType().has_type_variables())
        self.assertEqual(BoolType().get_type_variables(), set())
        self.assertTrue(a.has_type_variables())
        self.assertEqual(a.get_type_variables(), {a})
        self.assertEqual(b.get_type_variables(), set())
        self.assertEqual(c.get_type_variables(), {a})
        self.assertEqual(f.get_type_variables(), {a})
        self.assertEqual(f(c).get_type_variables(), {a})
        self.assertEqual(f(f >> c).get_type_variables(), {a})


if __name__ == '__main__':
    main()
