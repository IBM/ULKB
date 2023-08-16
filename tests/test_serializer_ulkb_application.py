# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Application(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        hc = Variable('h', FunctionType(c(a), bool))
        self.assert_to_ulkb(
            (Application(f, x),
             '(f : 𝔹 → 𝔹) (x : 𝔹) : 𝔹'),
            (Application(g, y, x),
             '(g : 𝔹 → 𝔹 → 𝔹) (y : 𝔹) (x : 𝔹) : 𝔹'),
            (Application(g, y, ha(x@a)), '\
(g : 𝔹 → 𝔹 → 𝔹) (y : 𝔹) ((h : a → 𝔹) (x : a)) : 𝔹'),
            (Application(hc, y@c(a)),
             '(h : c a → 𝔹) (y : c a) : 𝔹'),
            ((f@FunctionType(bool, bool, bool, bool))(x, y, ha(x@a)), '\
(f : 𝔹 → 𝔹 → 𝔹 → 𝔹) \
(x : 𝔹) (y : 𝔹) ((h : a → 𝔹) (x : a)) : 𝔹'))

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        hc = Variable('h', FunctionType(c(a), bool))
        self.assert_to_ulkb(
            (Variable('𝜄', FunctionType(a, bool))(Constant('𝛼', a)),
             '(\\U0001d704 : a -> bool) (\\U0001d6fc : a) : bool'),
            ensure_ascii=True)

        self.assert_to_ulkb(
            (Variable('𝜄', FunctionType(a, bool))(Constant('𝛼', a)),
             '\\U0001d704 \\U0001d6fc : bool'),
            ensure_ascii=True,
            omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        hc = Variable('h', FunctionType(c(a), bool))
        self.assert_to_ulkb(
            (f(y, j={'a': (1,)}),
             '(f : 𝔹 → 𝔹) (y : 𝔹) : 𝔹'),
            (f(f(y, j={'a': (1,)}), k={}),
             '(f : 𝔹 → 𝔹) ((f : 𝔹 → 𝔹) (y : 𝔹)) : 𝔹'),
            show_annotations=False)

        self.assert_to_ulkb(
            (f(y, j={'a': (1,)}),
             "(f : 𝔹 → 𝔹) (y : 𝔹) {j={'a': (1,)}} : 𝔹"),
            (f(f(y, j={'a': (1,)}), k={}, l=[]), "\
(f : 𝔹 → 𝔹) \
((f : 𝔹 → 𝔹) (y : 𝔹) {j={'a': (1,)}}) {k={}, l=[]} : 𝔹"),
            show_annotations=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        hc = Variable('h', FunctionType(c(a), bool))
        self.assert_to_ulkb(
            (f(y),
             '(f : 𝔹 → 𝔹) (y : 𝔹) : 𝔹'),
            (g(y, g(x, y)), '\
((g : 𝔹 → (𝔹 → 𝔹)) (y : 𝔹)) \
(((g : 𝔹 → (𝔹 → 𝔹)) (x : 𝔹)) (y : 𝔹)) : 𝔹'),
            ((f@FunctionType(bool, bool, bool, bool))(x, y, ha(x@a)), '\
(((f : 𝔹 → (𝔹 → (𝔹 → 𝔹))) (x : 𝔹)) (y : 𝔹)) \
((h : a → 𝔹) (x : a)) : 𝔹'),
            show_parentheses=True)

        self.assert_to_ulkb(
            (f(y),
             'f y : 𝔹'),
            (g(y, g(x, y)),
             '(g y) ((g x) y) : 𝔹'),
            ((f@FunctionType(bool, bool, bool, bool))(x, y, ha(x@a)),
             '((f x) y) (h x) : 𝔹'),
            show_parentheses=True, show_types=False)

        self.assert_to_ulkb(
            ((f@FunctionType(bool, bool, bool, bool))(x, y, ha(x@a)),
             'f x y (h x) : 𝔹'),
            show_parentheses=False, show_types=False)

    def test_show_types(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        hc = Variable('h', FunctionType(c(a), bool))
        self.assert_to_ulkb(
            (g(x, f(y)), '\
(g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) ((f : 𝔹 → 𝔹) (y : 𝔹)) : 𝔹'),
            show_types=True)

        self.assert_to_ulkb(
            (g(x, f(y)),
             'g x (f y) : 𝔹'),
            show_types=False)

    def test_misc(self):
        int = BaseType('int')
        f = Constant('f', FunctionType(int, int, int))
        t = f(Constant(1, int, k=0),
              f(Constant(2, int), i='abc')(Constant(3, int)), j=(-1, 1))
        self.assert_to_ulkb(
            (t, '\
(f : ℤ → ℤ → ℤ) (1 : ℤ) \
((f : ℤ → ℤ → ℤ) (2 : ℤ) (3 : ℤ)) : ℤ'))

        self.assert_to_ulkb(
            (t, "\
(f : ℤ → ℤ → ℤ) (1 {k=0} : ℤ) \
(((f : ℤ → ℤ → ℤ) (2 : ℤ) {i='abc'}) (3 : ℤ)) {j=(-1, 1)} : ℤ"),
            show_annotations=True)

        self.assert_to_ulkb(
            (t, "\
(f : int -> int -> int) (1 {k=0} : int) \
(((f : int -> int -> int) (2 : int) {i='abc'}) (3 : int)) {j=(-1, 1)} : int"),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t, "\
((f : ℤ → (ℤ → ℤ)) (1 {k=0} : ℤ)) \
(((f : ℤ → (ℤ → ℤ)) (2 : ℤ) {i='abc'}) (3 : ℤ)) {j=(-1, 1)} : ℤ"),
            omit_parentheses=False, show_annotations=True)

        self.assert_to_ulkb(
            (t, "f (1 {k=0}) ((f 2 {i='abc'}) 3) {j=(-1, 1)} : ℤ"),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (t, '\
(f : ℤ → ℤ → ℤ) (1 : ℤ) \
((f : ℤ → ℤ → ℤ) (2 : ℤ) (3 : ℤ)) : ℤ'),
            omit_annotations=True)

        self.assert_to_ulkb(
            (t,
             'f 1 (f 2 3) : ℤ'),
            omit_types=True, omit_annotations=True)

        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        x, y, z, w = Variables('x', 'y', 'z', 'w', a)
        self.assert_to_ulkb(
            (f,
             'f : a → a'),
            (x,
             'x : a'),
            (f(x),
             'f x : a'),
            (g(g(x, y), g(z, w)),
             'g (g x y) (g z w) : a'),
            (f(f(f(x))),
             'f (f (f x)) : a'),
            (g(x)(f(x)),
             'g x (f x) : a'),
            ((f@FunctionType(bool, a))(Equal(x, x)),
             'f (x = x) : a'),
            show_types=False)


if __name__ == '__main__':
    main()
