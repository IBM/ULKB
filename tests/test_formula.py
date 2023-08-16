# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestFormula(ULKB_TestCase):

    def test_formula(self):
        x, y = Variables('x', 'y', bool, i=1, j=2)
        k = Constant('k', bool, i=3)
        f = Constant('f', FunctionType(bool, bool), j=4)

        self.assert_formula(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_formula(k, ('k', BoolType()), {'i': 3})
        self.assert_formula(f(x), (f, x), {})
        self.assertFalse(Constant('x', BaseType('t')).is_formula())

    def test_equal(self):
        self.assertRaises(TypeError, Equal, BoolType(), BoolType())
        self.assertRaises(
            TypeError, Equal, Constant('x', bool), TypeVariable('a'))

        self.assertEqual(equal, Equal.constructor)

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> b)
        g = Constant('g', type=(a, b) >> a)

        t = Equal(x, y, i=1, j=2)
        self.assert_equal(t, (Equal.constructor(x), y), {'i': 1, 'j': 2})

        t = Equal(g(x, f(x)), g(y, f(g(x, k))), i=1, j=2)
        self.assert_equal(
            t, (equal(g(x, f(x))), g(y, f(g(x, k)))),
            {'i': 1, 'j': 2})

        # misc
        self.assertRaises(TypeError, Equal)
        self.assertRaises(TypeError, Equal, 0)
        self.assertRaises(TypeError, Equal, 0, 1, 2)
        self.assertRaises(ValueError, Equal, 0, True)
        self.assertRaises(
            ValueError, Equal,
            Constant('x', type=BaseType('t')),
            Constant('y', type=BaseType('s')))
        obj = Equal(Constant('x', bool), Constant('y', bool))
        self.assertTrue(obj.is_formula())
        self.assertTrue(obj.is_equal())
        self.assertEqual(obj[0][1], Constant('x', bool))
        self.assertEqual(obj[1], Constant('y', bool))
        self.assertEqual(obj.type, BaseType('bool'))

    def test_iff(self):
        self.assertRaises(TypeError, Iff, None, None)
        self.assertRaises(TypeError, Iff, BoolType(), BoolType())
        self.assertRaises(TypeError, Iff, Truth(), BoolType())
        self.assertRaises(
            TypeError, Iff, Constant('x', BaseType('a')), Truth())

        self.assertEqual(iff, Iff.constructor)

        x = Variable('x', bool)
        t = Iff(x, Truth(), i=1, j=2)
        self.assert_iff(
            t, (iff(x), Truth()), {'i': 1, 'j': 2})

        t = Iff(x, Truth(), i=1, j=2)
        self.assert_iff(
            t, (iff(x), Truth()), {'i': 1, 'j': 2})

        t = Iff(x, Truth(), x, Truth(), i=1, j=2)
        self.assert_iff(
            t, (iff(x), iff(Truth(), iff(x, Truth()))), {'i': 1, 'j': 2})

        self.assertTrue(t.is_formula())
        self.assertTrue(t.is_equal())
        self.assertTrue(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_truth(self):
        t = Truth(i=1, j=2)
        self.assert_truth(t, {'i': 1, 'j': 2})

        self.assertEqual(true, Truth.constructor)

        x = Variable('x', bool)
        self.assertTrue(Truth, Equal(x >> x, x >> x))
        self.assertEqual(Truth(), true())
        self.assertEqual(Truth(), true)

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertTrue(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_falsity(self):
        t = Falsity(i=1, j=2)
        self.assert_falsity(t, {'i': 1, 'j': 2})

        self.assertEqual(false, Falsity.constructor)

        y = Variable('y', bool)
        self.assertTrue(Falsity, Forall(y, y))
        self.assertEqual(Falsity(), false())
        self.assertEqual(Falsity(), false)

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertTrue(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_not(self):
        self.assertRaises(TypeError, Not, None)
        self.assertRaises(TypeError, And, BoolType())
        self.assertRaises(
            ValueError, Not, Constant('x', BaseType('a')))

        self.assertEqual(not_, Not.constructor)

        x = Variable('x', bool)
        t = Not(x, i=1, j=2)
        self.assert_not(t, (not_, x), {'i': 1, 'j': 2})

        t = Not(Not(Truth()), i=1, j=2)
        self.assert_not(
            t, (not_, not_(Truth())), {'i': 1, 'j': 2})

        x = Variable('x', bool)
        self.assertEqual(Not.definiens, x >> Implies(x, Falsity()))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertTrue(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_and(self):
        self.assertRaises(TypeError, And, None, None)
        self.assertRaises(TypeError, And, BoolType(), BoolType())
        self.assertRaises(TypeError, And, Truth(), BoolType())
        self.assertRaises(
            ValueError, And, Constant('x', BaseType('a')), Truth())

        self.assertEqual(and_, And.constructor)

        x = Variable('x', bool)
        t = And(x, Truth(), i=1, j=2)
        self.assert_and(
            t,
            (and_(x), Truth()),
            (x, Truth()),
            (x, Truth()),
            {'i': 1, 'j': 2})

        t = And(x, Truth(), x, Truth(), i=1, j=2)
        self.assert_and(
            t,
            (and_(x), and_(Truth(), and_(x, Truth()))),
            (x, Truth(), x, Truth()),
            (x, and_(Truth(), and_(x, Truth()))),
            {'i': 1, 'j': 2})

        x, y = Variables('x', 'y', bool)
        g = Variable('g', FunctionType(bool, bool, bool))
        self.assertEqual(
            And.definiens,
            (x, y) >> Equal(g >> g(x, y), g >> g(Truth(), Truth())))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertTrue(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_or(self):
        self.assertRaises(TypeError, Or, None, None)
        self.assertRaises(TypeError, Or, BoolType(), BoolType())
        self.assertRaises(TypeError, Or, Truth(), BoolType())
        self.assertRaises(
            ValueError, Or, Constant('x', BaseType('a')), Truth())

        self.assertEqual(or_, Or.constructor)

        x = Variable('x', bool)
        t = Or(x, Truth(), i=1, j=2)
        self.assert_or(
            t,
            (or_(x), Truth()),
            (x, Truth()),
            (x, Truth()),
            {'i': 1, 'j': 2})

        t = Or(x, Truth(), x, Truth(), i=1, j=2)
        self.assert_or(
            t,
            (or_(x), or_(Truth(), or_(x, Truth()))),
            (x, Truth(), x, Truth()),
            (x, or_(Truth(), or_(x, Truth()))),
            {'i': 1, 'j': 2})

        x, y, z = Variables('x', 'y', 'a', bool)
        self.assertEqual(
            Or.definiens,
            (x, y) >> Forall(z, Implies(Implies(x, z), Implies(y, z), z)))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertTrue(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_implies(self):
        self.assertRaises(TypeError, Implies, None, None)
        self.assertRaises(TypeError, Implies, BoolType(), BoolType())
        self.assertRaises(TypeError, Implies, Truth(), BoolType())
        self.assertRaises(
            ValueError, Implies, Constant('x', BaseType('a')), Truth())

        self.assertEqual(implies, Implies.constructor)

        x = Variable('x', bool)
        t = Implies(x, Truth(), i=1, j=2)
        self.assert_implies(
            t,
            (implies(x), Truth()),
            (x, Truth()),
            (x, Truth()),
            {'i': 1, 'j': 2})

        t = Implies(x, Truth(), x, Truth(), i=1, j=2)
        self.assert_implies(
            t,
            (implies(x), implies(Truth(), implies(x, Truth()))),
            (x, Truth(), x, Truth()),
            (x, implies(Truth(), implies(x, Truth()))),
            {'i': 1, 'j': 2})

        x, y = Variables('x', 'y', bool)
        self.assertEqual(Implies.definiens, (x, y) >> Iff(And(x, y), x))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertTrue(t.is_implies())
        self.assertFalse(t.is_forall())

    def test_exists(self):
        self.assertRaises(TypeError, Exists, None, None)
        self.assertRaises(TypeError, Exists, BoolType(), BoolType())
        self.assertRaises(TypeError, Exists, Truth(), BoolType())
        self.assertRaises(TypeError, Exists, Truth(), Truth())
        self.assertRaises(
            ValueError, Exists, Variable('x', BaseType('a')),
            Variable('x', BaseType('a')))

        self.assertEqual(exists, Exists.constructor)

        a, b = BaseTypes('ta', 'tb')
        x, z = Variables('x', 'z', a)
        y = Variable('y', b)
        f = Constant('f', FunctionType(a, b))
        g = Constant('g', FunctionType(a, a, bool))
        h = Constant('h', FunctionType(b, b, a))

        t = Exists(x, g(x, x), i=1, j=2)
        self.assert_exists(
            t,
            (exists@FunctionType(FunctionType(a, bool), bool),
             (x >> g(x, x)),),
            (x, g(x, x)),
            (x, g(x, x)),
            {'i': 1, 'j': 2})

        t = Exists(x, y, g(z, h(y, f(x))), i=1, j=2)
        self.assert_exists(
            t,
            (exists.instantiate(exists.type.match(t[0].type)),
             (x >> Exists(y, g(z, h(y, f(x)))))),
            (x, y, g(z, h(y, f(x)))),
            (x, Exists(y, g(z, h(y, f(x))))),
            {'i': 1, 'j': 2})

        self.assertEqual(t.free_variables, {z})
        self.assertEqual(t.left, exists.instantiate(
            exists.type.match(t[0].type)))

        a = TypeVariable('a')
        v = Variable('v', a)
        p = Variable('p', bool)
        f = Variable('f', FunctionType(a, bool))
        self.assertEqual(
            Exists.definiens,
            f >> Forall(p, Implies(Forall(v, Implies(f(v), p)), p)))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertTrue(t.is_exists())
        self.assertFalse(t.is_forall())

    def test_exists1(self):
        self.assertRaises(TypeError, Exists1, None, None)
        self.assertRaises(TypeError, Exists1, BoolType(), BoolType())
        self.assertRaises(TypeError, Exists1, Truth(), BoolType())
        self.assertRaises(TypeError, Exists1, Truth(), Truth())
        self.assertRaises(
            ValueError, Exists1, Variable('x', BaseType('a')),
            Variable('x', BaseType('a')))

        self.assertEqual(exists1, Exists1.constructor)

        a, b = BaseTypes('ta', 'tb')
        x, z = Variables('x', 'z', a)
        y = Variable('y', b)
        f = Constant('f', FunctionType(a, b))
        g = Constant('g', FunctionType(a, a, bool))
        h = Constant('h', FunctionType(b, b, a))

        t = Exists1(x, g(x, x), i=1, j=2)
        self.assert_exists1(
            t,
            (exists1@FunctionType(FunctionType(a, bool), bool),
             (x >> g(x, x)),),
            (x, g(x, x)),
            (x, g(x, x)),
            {'i': 1, 'j': 2})

        t = Exists1(x, y, g(z, h(y, f(x))), i=1, j=2)
        self.assert_exists1(
            t,
            (exists1.instantiate(exists1.type.match(t[0].type)),
             (x >> Exists1(y, g(z, h(y, f(x)))))),
            (x, y, g(z, h(y, f(x)))),
            (x, Exists1(y, g(z, h(y, f(x))))),
            {'i': 1, 'j': 2})

        self.assertEqual(t.free_variables, {z})
        self.assertEqual(t.left, exists1.instantiate(
            exists1.type.match(t[0].type)))

        a = TypeVariable('a')
        u, v = Variables('u', 'v', a)
        f = Variable('f', FunctionType(a, bool))
        self.assertEqual(
            Exists1.definiens,
            f >> And(
                Exists.constructor(f),
                Forall(u, v, Implies(And(f(u), f(v)), Equal(u, v)))))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertFalse(t.is_exists())
        self.assertTrue(t.is_exists1())
        self.assertFalse(t.is_forall())

    def test_forall(self):
        self.assertRaises(TypeError, Forall, None, None)
        self.assertRaises(TypeError, Forall, BoolType(), BoolType())
        self.assertRaises(TypeError, Forall, Truth(), BoolType())
        self.assertRaises(TypeError, Forall, Truth(), Truth())
        self.assertRaises(
            ValueError, Forall, Variable('x', BaseType('a')),
            Variable('x', BaseType('a')))

        self.assertEqual(forall, Forall.constructor)

        a, b = BaseTypes('ta', 'tb')
        x, z = Variables('x', 'z', a)
        y = Variable('y', b)
        f = Constant('f', FunctionType(a, b))
        g = Constant('g', FunctionType(a, a, bool))
        h = Constant('h', FunctionType(b, b, a))

        t = Forall(x, g(x, x), i=1, j=2)
        self.assert_forall(
            t,
            (forall@FunctionType(FunctionType(a, bool), bool),
             (x >> g(x, x)),),
            (x, g(x, x)),
            (x, g(x, x)),
            {'i': 1, 'j': 2})

        t = Forall(x, y, g(z, h(y, f(x))), i=1, j=2)
        theta = forall.type.match(t[0].type)
        self.assert_forall(
            t,
            (forall.instantiate(theta),
                (x >> Forall(y, g(z, h(y, f(x)))))),
            (x, y, g(z, h(y, f(x)))),
            (x, Forall(y, g(z, h(y, f(x))))),
            {'i': 1, 'j': 2})

        self.assertEqual(t.free_variables, {z})
        self.assertEqual(t.left, forall.instantiate(
            forall.type.match(t[0].type)))

        a = TypeVariable('a')
        v = Variable('v', a)
        f = Variable('f', FunctionType(a, bool))
        self.assertEqual(Forall.definiens, f >> Equal(f, v >> Truth()))

        self.assertTrue(t.is_formula())
        self.assertFalse(t.is_iff())
        self.assertFalse(t.is_truth())
        self.assertFalse(t.is_falsity())
        self.assertFalse(t.is_not())
        self.assertFalse(t.is_and())
        self.assertFalse(t.is_or())
        self.assertFalse(t.is_implies())
        self.assertTrue(t.is_forall())


if __name__ == '__main__':
    main()
