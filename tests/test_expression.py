# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestExpression(ULKB_TestCase):

    def test_get_unfolded_args(self):
        tc0 = TypeConstructor('tc0', 0, None)
        tc1 = TypeConstructor('tc1', 1, 'left')
        tc2l = TypeConstructor('tc2l', 2, 'left')
        tc2r = TypeConstructor('tc2r', 2, 'right')

        self.assert_unfolded_args(BoolType.constructor, ('bool', 0, None))
        self.assert_unfolded_args(BoolType(), (BoolType.constructor,))
        self.assert_unfolded_args(tc0, ('tc0', 0, None))
        self.assert_unfolded_args(tc0(), (tc0,))
        self.assert_unfolded_args(tc1, ('tc1', 1, 'left'))
        self.assert_unfolded_args(tc1(tc0()), (tc1, tc0()))
        self.assert_unfolded_args(tc2l, ('tc2l', 2, 'left'))

        self.assert_unfolded_args(tc2l(tc0(), tc0()), (tc2l, tc0(), tc0()))
        t = tc2l(tc0(), tc0(), tc0())
        self.assertEqual(t.args, (tc2l, tc2l(tc0(), tc0()), tc0()))
        self.assert_unfolded_args(t, (tc2l, tc0(), tc0(), tc0()))

        self.assert_unfolded_args(tc2r(tc0(), tc0()), (tc2r, tc0(), tc0()))
        t = tc2r(tc0(), tc0(), tc0())
        self.assertEqual(t.args, (tc2r, tc0(), tc2r(tc0(), tc0())))
        self.assert_unfolded_args(t, (tc2r, tc0(), tc0(), tc0()))
        self.assert_unfolded_args(
            tc2r(tc2l(tc0(), tc0(), tc0()), tc0(), tc0()),
            (tc2r, tc2l(tc0(), tc0(), tc0()), tc0(), tc0()))

        a = TypeVariable('a')
        b = BaseType('b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_unfolded_args(a, ('a',))
        self.assert_unfolded_args(x, ('x', a))
        self.assert_unfolded_args(c, ('c', b))
        self.assert_unfolded_args(g(x, c), (g, x, c))
        self.assert_unfolded_args(g(x, d), (g, x, d))
        self.assert_unfolded_args(g(y, f(g(x, d))), (g, y, f(g(x, d))))
        self.assert_unfolded_args(x >> c, (x, c))
        self.assert_unfolded_args(x >> x, (x, x))
        self.assert_unfolded_args(y >> (x >> c), (y, x, c))
        self.assert_unfolded_args(
            (x, y, z) >> g(x, f(z)), (x, y, z, g(x, f(z))))
        self.assert_unfolded_args(x >> g(x, d), (x, g(x, d)))
        self.assert_unfolded_args(x >> g(y, d), (x, g(y, d)))
        self.assert_unfolded_args(
            z >> g(y, f(g(x, d))), (z, g(y, f(g(x, d)))))
        self.assert_unfolded_args(
            (z, y) >> g(y, f(g(x, d))), (z, y, g(y, f(g(x, d)))))
        self.assert_unfolded_args(
            (z, y, x) >> g(y, f(g(x, d))), (z, y, x, g(y, f(g(x, d)))))

    def test_get_type_constructors(self):
        a = TypeVariable('a')
        b = BaseType('b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_type_constructors(
            BoolType.constructor, {BoolType.constructor})
        self.assert_type_constructors(BoolType(), {BoolType.constructor})
        self.assert_type_constructors(a, set())
        self.assert_type_constructors(x, set())
        self.assert_type_constructors(c, {b.head})
        self.assert_type_constructors(
            g(x, c), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            g(x, d), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            g(y, f(g(x, d))), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            x >> c, {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            x >> g(x, d), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            x >> g(y, d), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            z >> g(y, f(g(x, d))), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            (z, y) >> g(y, f(g(x, d))), {FunctionType.constructor, b.head})
        self.assert_type_constructors(
            (z, y, x) >> g(y, f(g(x, d))),
            {FunctionType.constructor, b.head})

    def test_get_type_variables(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c = Constant('c', a)
        d, e = Constants('d', 'e', type=b)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_type_variables(BoolType.constructor, set())
        self.assert_type_variables(a, {a})
        self.assert_type_variables(x, {a})
        self.assert_type_variables(c, {a})
        self.assert_type_variables(BoolType(), set())
        self.assert_type_variables(f(c), {a, b})
        self.assert_type_variables(g(y, f(g(x, d))), {a, b})
        self.assert_type_variables(y >> g(y, f(g(x, d))), {a, b})
        self.assert_type_variables(g(x, d), {a, b})
        self.assert_type_variables(g(y, f(g(x, d))), {a, b})
        self.assert_type_variables(x >> c, {a})
        self.assert_type_variables(x >> f(x), {a, b})
        self.assert_type_variables(x >> g(y, d), {a, b})
        self.assert_type_variables(z >> g(y, f(g(x, d))), {a, b})
        self.assert_type_variables((z, y) >> g(y, f(g(x, d))), {a, b})
        self.assert_type_variables((z, y, x) >> g(y, f(g(x, d))), {a, b})

    def test_instantiate(self):
        f = TypeConstructor('f', 1)
        g = TypeConstructor('g', 3)
        a, b, c, d = TypeVariables('a', 'b', 'c', 'd')
        t = FunctionType(a, f(b, i=1), g(a, b, c, j=2), k=3)

        self.assertIs(f.instantiate({}), f)
        self.assertEqual(f.instantiate({d: BoolType()}), f)

        self.assertIs(t.instantiate({}), t)
        self.assertEqual(t.instantiate({d: BoolType()}), t)

        nat = BaseType('nat')
        s = t.instantiate({a: nat, b: BoolType()})
        self.assert_deep_equal(
            s, FunctionType(nat, f(bool, i=1), g(nat, bool, c, j=2), k=3))
        self.assertEqual(t.get_type_variables(), {a, b, c})
        self.assertEqual(s.get_type_variables(), {c})

        a, b = TypeVariables('a', 'b', i=1, j=2)
        x, y = Variables('x', 'y', type=a, abc='def')
        k = Constant('k', type=b)
        f = Constant('f', type=(a >> b))
        g = Constant('g', type=(a, b) >> a)

        a, b = TypeVariables('a', 'b', i=1, j=2)
        x, y = Variables('x', 'y', type=a, abc='def')
        k = Constant('k', type=b)
        f = Constant('f', type=(a >> b))
        g = Constant('g', type=(a, b) >> a)
        d, e = BaseTypes('d', 'e', a=a)

        t = x
        s = t.instantiate({})
        self.assert_deep_equal(s, t)
        s = t.instantiate({a: d >> e})
        self.assert_deep_equal(s, Variable('x', d >> e, abc='def'))

        t = k
        s = t.instantiate({a: d >> e})
        self.assertIs(s, t)

        t = f(x)
        s = t.instantiate({})
        self.assert_deep_equal(s, t)
        s = t.instantiate({TypeVariable('c'): a})
        self.assert_deep_equal(s, t)
        s = t.instantiate({a: b})
        self.assert_deep_equal(s, (f@(b >> b))(x@b))

        t = g(y, f(x))
        s = t.instantiate({})
        self.assert_deep_equal(s, t)
        s = t.instantiate({TypeVariable('c'): a})
        self.assert_deep_equal(s, t)
        s = t.instantiate({a: a})
        self.assert_deep_equal(s, t)
        s = t.instantiate({b: a, a: b})
        self.assert_deep_equal(s, (g@((b, a) >> b))(y@b, (f@(b >> a))(x@b)))

        t = x >> x
        s = t.instantiate({})
        self.assert_deep_equal(s, t)
        s = t.instantiate({TypeVariable('c'): a})
        self.assert_deep_equal(s, t)
        s = t.instantiate({a: b, b: a})
        self.assert_deep_equal(s, x@b >> x@b)

        t = x >> x@b            # rename to avoid capture
        s = t.instantiate({})
        self.assert_deep_equal(s, t)
        s = t.instantiate({TypeVariable('c'): a})
        self.assert_deep_equal(s, t)
        s = t.instantiate({a: b, b: a})
        self.assert_deep_equal(s, x@b >> x@a)
        s = t.instantiate({a: b})
        self.assert_deep_equal(s, Variable("x0", b, abc='def') >> x@b)

        t = (x, y) >> g(y, x@b)  # rename to avoid capture
        s = t.instantiate({a: b})
        self.assert_deep_equal(
            s, (Variable("x0", b, abc='def'), y@b)
            >> (g@((b, b) >> b))(y@b, x@b))

        f = f@(b >> b)
        t = (x, y) >> g(y, f(x@b))
        s = t.instantiate({a: b, b: a})
        self.assert_deep_equal(
            s, (x@b, y@b) >> (g@((b, a) >> b))(y@b, (f@(a >> a))(x@a)))


if __name__ == '__main__':
    main()
