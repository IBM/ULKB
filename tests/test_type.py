# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestType(ULKB_TestCase):

    def test_type_variable(self):
        self.assertRaises(TypeError, TypeVariable, None)
        self.assertRaisesRegex(
            TypeError, '(invalid id)', TypeVariable, BoolType())

        a = TypeVariable('a', i=1, j=2)
        self.assert_type_variable(a, ('a',), {'i': 1, 'j': 2})
        self.assert_deep_equal(a, TypeVariable('a', i=1, j=2))
        self.assertEqual(a, TypeVariable('a', abc='def'))
        self.assert_equal_but_not_deep_equal(
            a, TypeVariable('a', abc='def'))

        b = TypeVariable('b', a=a, i=1, j=2)
        self.assert_type_variable(b, ('b',), {'a': a, 'i': 1, 'j': 2})
        self.assertNotEqual(a, b)

        a, b, c = TypeVariables('a', 'b', 'c', i=1, j=2)
        self.assert_type_variable(a, ('a',), {'i': 1, 'j': 2})
        self.assert_type_variable(b, ('b',), {'i': 1, 'j': 2})
        self.assert_type_variable(c, ('c',), {'i': 1, 'j': 2})

    def test_type_application(self):
        self.assertRaises(TypeError, TypeApplication, None)
        self.assertRaises(
            TypeError, TypeApplication, TypeVariable('x'))
        self.assertRaises(
            ValueError, TypeApplication, TypeConstructor('c', 1))
        self.assertRaises(
            TypeError, TypeApplication, TypeConstructor('c', 1), None)
        self.assertRaises(
            TypeError, TypeApplication, TypeConstructor('c', 1),
            BoolType.constructor)
        self.assertRaises(
            TypeError, TypeApplication, TypeConstructor('c', 1), "abc")
        self.assertRaisesRegex(
            ValueError, '(too few arguments: expected 1, got 0)',
            TypeApplication, TypeConstructor('c', 1))

        c0 = TypeConstructor('c0', 0)
        c1 = TypeConstructor('c1', 1)
        c2 = TypeConstructor('c2', 2)

        t = TypeApplication(c0, i=1, j=2)
        self.assert_type_application(t, (c0,), (c0,), {'i': 1, 'j': 2})
        self.assert_deep_equal(t, c0(i=1, j=2))

        s = TypeApplication(c1, t, i=1, j=2, t=t)
        self.assert_type_application(
            s, (c1, t), (c1, t), {'i': 1, 'j': 2, 't': t})
        self.assert_deep_equal(s, c1(t, i=1, j=2, t=t))

        r = TypeApplication(c2, t, s, i=1, j=2)
        self.assert_type_application(
            r, (c2, t, s), (c2, t, s), {'i': 1, 'j': 2})
        self.assert_deep_equal(r, c2(t, s, i=1, j=2))

    def test_base_type(self):
        self.assertRaises(TypeError, BaseType, BoolType())
        self.assert_base_type(
            BaseType('x', i=1, j=2),
            (TypeConstructor('x', 0),), {'i': 1, 'j': 2})

    def test_bool_type(self):
        self.assert_bool_type(
            BoolType(i=1, j=2), (BoolType.constructor,), {'i': 1, 'j': 2})

    def test_function_type(self):
        self.assertRaises(TypeError, FunctionType, 1, 2)
        self.assert_function_type(
            FunctionType(BoolType(), BoolType(), i=1, j=2),
            (FunctionType.constructor, BoolType(), BoolType()),
            (BoolType(), BoolType()),
            (BoolType(), BoolType()),
            {'i': 1, 'j': 2})
        a, b, c = TypeVariables('a', 'b', 'c')
        self.assert_function_type(
            a >> b,
            (FunctionType.constructor, a, b),
            (a, b),
            (a, b))
        self.assert_function_type(
            b << a,
            (FunctionType.constructor, a, b),
            (a, b),
            (a, b))
        self.assert_function_type(
            (a, b) >> c,
            (FunctionType.constructor, a, FunctionType(b, c)),
            (a, b, c),
            (a, FunctionType(b, c)))
        self.assert_function_type(
            c << (a, b),
            (FunctionType.constructor, a, FunctionType(b, c)),
            (a, b, c),
            (a, FunctionType(b, c)))
        self.assertEqual(a >> (b >> c), FunctionType(a, b, c))
        self.assertEqual((a, b) >> c, FunctionType(a, b, c))
        self.assertEqual(
            (a, b >> c) >> c, FunctionType(a, FunctionType(b, c), c))

    def test_match(self):
        a, b, c = TypeVariables('a', 'b', 'c')
        i, j, k = BaseTypes('i', 'j', 'k')

        self.assertRaises(TypeError, a.match, Truth())

        self.assert_match(a, a, {a: a})
        self.assert_match(a, b, {a: b})
        self.assert_match(a, i, {a: i})
        self.assert_match(i, a, None)
        self.assert_match((a >> a), a, None)
        self.assert_match((a >> b), a, None)
        self.assert_match((a >> b), c, None)
        self.assert_match(a >> b, c >> a, {a: c, b: a})
        self.assert_match(a >> (a >> b), b >> (c >> a), None)
        self.assert_match(a >> (a >> b), b >> (b >> c), {a: b, b: c})
        self.assert_match(b >> i, a >> (j >> i), None)
        self.assert_match(b >> i, (i >> j) >> i, {b: i >> j})
        self.assert_match(a, BoolType(), {a: BoolType()})


if __name__ == '__main__':
    main()
