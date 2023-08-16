# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestTerm(ULKB_TestCase):

    def test_variable(self):
        self.assertRaises(TypeError, Variable, None)
        self.assertRaisesRegex(
            ValueError, '(no such type alias)', Variable, 'x', list)
        self.assertRaisesRegex(
            TypeError, '(invalid id)', Variable, BoolType())
        self.assertRaises(TypeError, Variable, 'x', BoolType.constructor)

        a = TypeVariable('a', k=1)
        b = TypeVariable('b', k=2)
        x = Variable('x', type=a, i=1, j=2)
        self.assert_variable(x, ('x', a), {'i': 1, 'j': 2})
        self.assert_deep_equal(x, Variable('x', a, i=1, j=2))
        self.assert_equal_but_not_deep_equal(
            x, Variable('x', a, i=2, j=2))
        self.assertNotEqual(x, Variable('x', TypeVariable('b')))
        self.assertFalse(x.equal(Variable('x', type=b)))
        self.assertTrue(x.equal(Variable('x', type=a, i=2)))
        self.assertFalse(x.equal(Variable('x', type=a, i=2), deep=True))

        x, y, z = Variables('x', 'y', 'z', type=bool, i=1, j=2)
        self.assert_variable(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_variable(y, ('y', BoolType()), {'i': 1, 'j': 2})
        self.assert_variable(z, ('z', BoolType()), {'i': 1, 'j': 2})

        self.assert_deep_equal(x@b, Variable('x', type=b, i=1, j=2))
        self.assert_deep_equal(x@{'i': 2}, Variable('x', type=bool, i=2))

    def test_variable_get_variant(self):
        a = TypeVariable('a')
        x, y, z = Variables('x', 'y', 'z', type=a)
        self.assertEqual(x.get_variant(lambda v: v != x), x)
        self.assertEqual(x.get_variant(lambda v: v == x), Variable('x0', a))
        self.assertEqual(
            x.get_variant(lambda v: v == x or int(v.id[-1]) <= 5),
            Variable('x6', a))

    def test_variable_get_variant_not_in(self):
        a = TypeVariable('a')
        x, x0, x1, y, z = Variables('x', 'x0', 'x1', 'y', 'z', type=a)
        self.assertEqual(x.get_variant_not_in([]), x)
        self.assertIs(x.get_variant_not_in({x0, x1, y, z}), x)
        self.assertEqual(x.get_variant_not_in({x, y, z}), x0)
        self.assertEqual(x.get_variant_not_in({x, x0}), x1)
        self.assertEqual(x.get_variant_not_in({x, x1, y}), x0)

    def test_variable_get_variant_not_bound_in(self):
        a = TypeVariable('a')
        x, x0, x1, y, z = Variables('x', 'x0', 'x1', 'y', 'z', type=a)
        self.assertEqual(x.get_variant_not_bound_in([]), x)
        self.assertIs(x.get_variant_not_bound_in({x0, x1, y, z}), x)
        self.assertEqual(x.get_variant_not_bound_in({x, y, z}), x)
        self.assertEqual(x.get_variant_not_bound_in({x >> x, x0 >> x}), x1)
        self.assertEqual(x.get_variant_not_bound_in({x >> x, x1, y}), x0)

    def test_variable_get_variant_not_free_in(self):
        a = TypeVariable('a')
        x, x0, x1, y, z = Variables('x', 'x0', 'x1', 'y', 'z', type=a)
        self.assertEqual(x.get_variant_not_free_in([]), x)
        self.assertIs(x.get_variant_not_free_in({x0, x1, y, z}), x)
        self.assertEqual(x.get_variant_not_free_in({x, y, z}), x0)
        self.assertEqual(x.get_variant_not_free_in({x >> x, x0 >> x0}), x)
        self.assertEqual(x.get_variant_not_free_in({x, x0 >> x0, y}), x0)

    def test_constant(self):
        self.assertRaises(TypeError, Constant, None)
        self.assertRaisesRegex(
            ValueError, '(no such type alias)', Constant, 'x', list)
        self.assertRaisesRegex(
            TypeError, '(invalid id)', Constant, BoolType())
        self.assertRaises(TypeError, Constant, 'x', BoolType.constructor)

        a = TypeVariable('a', k=1)
        b = TypeVariable('b', k=2)
        k = Constant('k', type=a, i=1, j=2)
        self.assert_constant(k(i=8), ('k', a), {'i': 8})
        self.assert_constant(k, ('k', a), {'i': 1, 'j': 2})
        self.assert_deep_equal(k, Constant('k', a, i=1, j=2))
        self.assert_equal_but_not_deep_equal(
            k, Constant('k', a, i=1, j=2, k=k))
        self.assertNotEqual(k, Constant('k', TypeVariable('b')))

        x, y, z = Constants('x', 'y', 'z', type=bool, i=1, j=2)
        self.assert_constant(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(y, ('y', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(z, ('z', BoolType()), {'i': 1, 'j': 2})

        self.assert_deep_equal(x@b, Constant('x', type=b, i=1, j=2))
        self.assert_deep_equal(x@{'i': 2}, Constant('x', type=bool, i=2))

        x, y, z = Constants('x', 'y', 'z', bool, i=1, j=2)
        self.assert_constant(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(y, ('y', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(z, ('z', BoolType()), {'i': 1, 'j': 2})

    def test_application(self):
        self.assertRaises(TypeError, Application, None)
        self.assertRaises(
            TypeError, Application,
            Constant('c', type=FunctionType(bool, bool)))
        self.assertRaises(
            TypeError, Application,
            Constant('c', type=FunctionType(bool, bool)), None)
        self.assertRaisesRegex(
            ValueError, '(not a function)', Application,
            Constant('c', type=bool), Constant('d', type=bool))
        self.assertRaisesRegex(
            ValueError, r"expected '𝔹 : \*', got 'a : \*'",
            Application,
            Constant('c', type=FunctionType(bool, bool)),
            Constant('d', type=BaseType('a')))

        a = BaseType('a')
        f = Variable('f', FunctionType(bool, bool, bool), i=1, j=2)
        g = Variable('g', FunctionType(a, bool))
        k = Constant('k', a)
        x = Variable('x', bool)

        t = Application(f, Application(g, k, i=1), x, i=1, j=2)
        self.assert_application(
            t, (f(g(k)), x), (f, g(k), x), BoolType(), {'i': 1, 'j': 2})
        self.assert_deep_equal(t, f(g(k, i=1), x, i=1, j=2))
        self.assert_equal_but_not_deep_equal(t, f(g(k), x, i=1, j=2))
        self.assertNotEqual(t, f(g(Constant("k'", a))))

    def test_beta_redex(self):
        a = BaseType('a')
        x = Variable('x', a)
        f = Variable('f', FunctionType(a, bool))
        self.assertRaises(TypeError, BetaRedex, None)
        self.assertRaises(TypeError, BetaRedex, x)
        self.assertRaises(TypeError, BetaRedex, x, x)
        self.assertRaises(TypeError, BetaRedex, f, x)
        self.assert_beta_redex(
            BetaRedex(x >> x, x, i=1, j=2),
            ((x >> x), x),
            ((x >> x), x),
            a,
            {'i': 1, 'j': 2})
        self.assertFalse(f(x).is_beta_redex())

    def test_abstraction(self):
        self.assertRaises(TypeError, Abstraction, None)
        self.assertRaises(TypeError, Abstraction, Variable('x', bool))
        self.assertRaises(TypeError, Abstraction, Variable('x', bool), None)
        self.assertRaises(
            TypeError, Abstraction, Constant('x', bool),
            Variable('y', bool))

        a = BaseType('a')
        g = Variable('g', a >> bool)
        k = Constant('k', a)
        x, y = Variables('x', 'y', type=bool)

        t = Abstraction(x, y, g(k, i=1), i=1, j=2)
        self.assert_abstraction(
            t,
            (x, Abstraction(y, g(k))),
            (x, y, g(k)),
            (bool, bool) >> BoolType(),
            {'i': 1, 'j': 2})
        self.assert_deep_equal(t, Abstraction(x, y, g(k, i=1), i=1, j=2))

        self.assertEqual(x >> y, Abstraction(x, y))
        self.assertEqual(y << x, Abstraction(x, y))
        self.assertEqual((x, y) >> g, Abstraction(x, y, g))
        self.assertEqual(g << (x, y), Abstraction(x, y, g))
        self.assertEqual(g >> (x >> y), Abstraction(g, x, y))

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z = Variables('x', 'y', 'z', a)
        f = Constant('f', (a, a) >> a)

        t = x >> x
        s = t.rename(y)
        self.assertEqual(s, y >> y)
        self.assertEqual(s.left, y)
        self.assertEqual(s.right, y)

        t = x >> y
        s = t.rename(y)
        self.assertEqual(s, t)
        self.assertEqual(s, z >> y)
        self.assertEqual(s.left.id, 'y0')
        self.assertEqual(s.right, y)

        t = (x, y) >> f(y, z)
        s = t.rename(y)
        self.assertEqual(s, t)
        self.assertEqual(s.left.id, 'y0')
        self.assertEqual(s.right, t.right)

    def test_get_constants(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        k = Constant('k', a)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_constants(x, set())
        self.assert_constants(c, {c})
        self.assert_constants(k, {k})
        self.assert_constants(g(x, c), {g, c})
        self.assert_constants(g(k, d), {g, k, d})
        self.assert_constants(g(y, f(g(x, d))), {d, g, f})
        self.assert_constants(x >> c, {c})
        self.assert_constants(x >> g(x, d), {g, d})
        self.assert_constants(x >> g(y, d), {g, d})
        self.assert_constants(z >> g(y, f(g(x, d))), {g, f, d})
        self.assert_constants((z, y) >> g(y, f(g(x, d))), {g, f, d})
        self.assert_constants((z, y, x) >> g(y, f(g(x, d))), {g, f, d})

    def test_get_variables(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        k = Constant('k', a)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_variables(x, {x})
        self.assert_variables(x >> x, {x})
        self.assert_variables((x, x) >> x, {x})
        self.assert_variables(c, set())
        self.assert_variables(g(x, c), {x})
        self.assert_variables(y >> g(x, c), {x, y})
        self.assert_variables(g(k, d), set())
        self.assert_variables(g(y, f(g(x, d))), {x, y})
        self.assert_variables(g(y, y >> f(g(x, d))), {x, y})
        self.assert_variables(x >> c, {x})
        self.assert_variables(x >> g(x, d), {x})
        self.assert_variables(x >> g(y, d), {x, y})
        self.assert_variables(z >> g(y, f(g(x, d))), {x, y, z})
        self.assert_variables((z, y) >> g(y, f(g(x, d))), {x, y, z})
        self.assert_variables((z, y, x) >> g(y, f(g(x, d))), {x, y, z})

    def test_get_bound_variables(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        k = Constant('k', a)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_bound_variables(x, set())
        self.assert_bound_variables(x >> x, {x})
        self.assert_bound_variables((x, x) >> x, {x})
        self.assert_bound_variables(c, set())
        self.assert_bound_variables(g(x, c), set())
        self.assert_bound_variables(y >> g(x, c), {y})
        self.assert_bound_variables(g(k, d), set())
        self.assert_bound_variables(g(y, f(g(x, d))), set())
        self.assert_bound_variables(g(y, y >> f(g(x, d))), {y})
        self.assert_bound_variables(x >> c, {x})
        self.assert_bound_variables(x >> g(x, d), {x})
        self.assert_bound_variables(x >> g(y, d), {x})
        self.assert_bound_variables(z >> g(y, f(g(x, d))), {z})
        self.assert_bound_variables((z, y) >> g(y, f(g(x, d))), {z, y})
        self.assert_bound_variables(
            (z, y, x) >> g(y, f(g(x, d))), {x, y, z})

    def test_get_free_variables(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', type=a)
        c, d, e = Constants('c', 'd', 'e', type=b)
        k = Constant('k', a)
        f = Constant('f', a >> b)
        g = Constant('g', (a, b) >> a)

        self.assert_free_variables(x, {x})
        self.assert_free_variables(c, set())
        self.assert_free_variables(g(x, c), {x})
        self.assert_free_variables(g(k, d), set())
        self.assert_free_variables(g(y, f(g(x, d))), {x, y})
        self.assert_free_variables(x >> c, set())
        self.assert_free_variables(x >> g(x, d), set())
        self.assert_free_variables(x >> g(y, d), {y})
        self.assert_free_variables(z >> g(y, f(g(x, d))), {x, y})
        self.assert_free_variables((z, y) >> g(y, f(g(x, d))), {x})
        self.assert_free_variables((z, y, x) >> g(y, f(g(x, d))), set())

    def test_alpha_equal(self):
        a, b = TypeVariables('a', 'b')
        x, y, z = Variables('x', 'y', 'z', a)
        k = Constant('k', b)
        f = Constant('f', a >> b)
        g = Constant('g', type=(a, b) >> a)

        self.assertEqual(x, x)
        self.assertEqual(x, x@{'j': 3})
        self.assertNotEqual(x, x@bool)
        self.assertEqual((x@bool), x@bool)
        self.assertNotEqual(x, y)
        self.assertNotEqual(y, x)
        self.assertNotEqual(x, k)
        self.assertNotEqual(k, x)
        self.assertEqual(k, k)
        self.assertEqual(f(x), f(x))
        self.assertEqual(g(x, f(y)), g(x, f(y)))
        self.assertNotEqual(g(x, f(y)), g(y, f(y)))
        self.assertEqual((x >> g(x, f(z))), y >> g(y, f(z)))
        self.assertEqual(((x, y) >> g(x, f(y))), (y, x) >> g(y, f(x)))

    def test_substitute(self):
        nat = BaseType('nat')
        f = Constant('f', (nat, nat, nat) >> nat)
        g = Variable('g', nat >> nat)
        x, y = Variables('x', 'y', type=nat)
        k = Constant('k', nat)

        self.assertRaisesRegex(
            ValueError, '(invalid theta)', x.substitute, {1: 2})
        self.assertRaisesRegex(
            ValueError, '(invalid theta)', x.substitute, {nat: x})
        self.assertRaisesRegex(
            ValueError, '(invalid theta)', x.substitute, {x: nat})
        self.assertRaisesRegex(
            ValueError, '(invalid theta)',
            x.substitute, {x: x@bool})

        t = f(x, g(k, i=1), g(g(y, j=2)), k=3)
        self.assertIs(t.substitute({}), t)
        self.assertEqual(t.substitute({Variable('d', nat): x}), t)
        self.assert_deep_equal(
            t.substitute({y: k}), f(x, g(k, i=1), g(g(k, j=2)), k=3))
        self.assert_equal_but_not_deep_equal(
            t.substitute({y: k}), f(x, g(k, i=1), g(g(k, j=-2)), k=3))
        self.assert_deep_equal(
            t.substitute({x: y, g: f(k, k)}),
            f(y, f(k, k)(k, i=1), f(k, k)(f(k, k)(y, j=2)), k=3))

        z = Variable('z', type=nat, abc=123)
        t = z >> g(f(x, g(z, i=1), k), j=2)
        z1 = z.with_args("z0", z.type)
        self.assertEqual(z.annotations, z1.annotations)
        self.assertIs(t.substitute({}), t)
        self.assertEqual(t.substitute({Variable('d', nat): x}), t)
        self.assert_deep_equal(
            t.substitute({x: z}),
            z1 >> g(f(z, g(z1, i=1), k), j=2))

        h = Constant('h', (nat, nat) >> nat)
        x, x0, x1, x2, y = Variables('x', "x0", "x1", "x2", 'y', type=nat)

        t = (x, x0) >> x
        s = t.substitute({x: y})
        self.assertEqual(s, t)
        self.assertEqual(s.left, t.left)
        self.assertEqual(s.right, t.right)

        t = (x, x0) >> h(x, y)
        s = t.substitute({x: y})
        self.assertEqual(s, t)
        self.assertEqual(s.left, t.left)
        self.assertEqual(s.right, t.right)

        s = t.substitute({x: y, x0: y})
        self.assertEqual(s, t)
        self.assertEqual(s.left, t.left)
        self.assertEqual(s.right, t.right)
        self.assertIs(t.substitute({x: y, x0: y}), t)

        s = t.substitute({y: x})
        self.assertEqual(s, (x1, x0) >> h(x1, x))
        self.assertEqual(s.left.id, 'x1')
        self.assertEqual(s.right, x0 >> h(x1, x))

        t = (x, x0) >> y
        s = t.substitute({y: x})
        self.assertEqual(s, (x2, x1) >> x)
        self.assertEqual(s.left, x1)
        self.assertEqual(s.right, x0 >> x)

        x = Variable('x', bool)
        u, v = Variables('u', 'v', bool)
        f = Constant('f', FunctionType(bool, bool))

        t = ((x >> u)(x))
        s = t.substitute({x: f(v)})
        self.assertEqual(s, (x >> u)(f(v)))

        s = t.substitute({u: f(x)})
        self.assertEqual(s, (x0@bool >> f(x))(x))
        self.assertEqual(s.left.left.id, 'x0')


if __name__ == '__main__':
    main()
