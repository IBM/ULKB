# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Exists1(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x, x),
             '(∃! x, x) : 𝔹'),
            (Exists1(x, y, g(x, y)),
             '(∃! x y, g x y) : 𝔹'),
            (Exists1(x, Exists1(y, g(x, y))),
             '(∃! x y, g x y) : 𝔹'),
            (Exists1(z, g(z, Exists1(x, y, g(x, y)))),
             '(∃! z, g z (∃! x y, g x y)) : 𝔹'),
            omit_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x, x),
             '(exists1 x, x) : bool'),
            (Exists1(x, y, g(x, y)),
             '(exists1 x y, g x y) : bool'),
            (Exists1(x, Exists1(y, g(x, y))),
             '(exists1 x y, g x y) : bool'),
            (Exists1(z, g(z, Exists1(x, y, g(x, y)))),
             '(exists1 z, g z (exists1 x y, g x y)) : bool'),
            (Exists1(Variable('𝛼', a), x),
             '(exists1 \\U0001d6fc, x) : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∃! (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Exists1(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∃! (x {i=1}) (y {j=2}), z) {k=3} : 𝔹'),
            (Exists1(x, Exists1(y, z, k=3)),
             '(∃! x, ((∃! y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Exists1(y, z, k=3)),
             '(𝜆 x ⇒ ((∃! y, z) {k=3})) : 𝔹 → 𝔹'),
            (Exists1(x, Abstraction(y, z, k=3)(y)),
             '(∃! x, ((𝜆 y ⇒ z) {k=3}) y) : 𝔹'),
            (Exists1(x@{'i': 1}, Exists1(y@{'j': 2}, z, k=3)),
             '(∃! (x {i=1}), ((∃! (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Exists1(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∃! (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Exists1(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∃! (x {i=1}), (∃! (y {j=2}), z)) {k=3} : 𝔹'),
            (Exists1(x, Exists1(y, z, k=3)),
             '(∃! x, ((∃! y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Exists1(y, z, k=3)),
             '(𝜆 x ⇒ ((∃! y, z) {k=3})) : 𝔹 → 𝔹'),
            (Exists1(x, Abstraction(y, z, k=3)(y)),
             '(∃! x, (((𝜆 y ⇒ z) {k=3}) y)) : 𝔹'),
            (Exists1(x@{'i': 1}, Exists1(y@{'j': 2}, z, k=3)),
             '(∃! (x {i=1}), ((∃! (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x, x),
             '(∃! x, x) : 𝔹'),
            (Exists1(x, y, g(x, y)),
             '(∃! x, (∃! y, ((g x) y))) : 𝔹'),
            (Exists1(x, Exists1(y, g(x, y))),
             '(∃! x, (∃! y, ((g x) y))) : 𝔹'),
            (Exists1(z, g(z, Exists1(x, y, g(x, y)))),
             '(∃! z, ((g z) (∃! x, (∃! y, ((g x) y))))) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x, g(x, x)), '\
(∃! (x : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (x : 𝔹)) : 𝔹'),
            (Exists1(x, y, g(x, y)), '\
(∃! (x : 𝔹) (y : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹)) : 𝔹'),
            (Exists1(x, f(Exists1(y, g(x, y)))), '\
(∃! (x : 𝔹), (f : 𝔹 → 𝔹) (∃! (y : 𝔹), \
(g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹))) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Exists1(x, x)),
             'f (∃! x, x) : 𝔹'),
            (Exists1(x, f(x)),
             '(∃! x, f x) : 𝔹'),
            (Exists1(x, f(y)),
             '(∃! x, f y) : 𝔹'),
            (Exists1(x, f(Exists1(y, y))),
             '(∃! x, f (∃! y, y)) : 𝔹'),
            omit_types=True)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        b = Variable('b', bool)
        self.assert_to_ulkb(
            (Abstraction(z, Exists1(x, b)),
             '(𝜆 z ⇒ ∃! x, b) : 𝔹 → 𝔹'),
            (Exists1(x, Abstraction(z, Exists1(y, g(y, z)))(z)),
             '(∃! x, (𝜆 z ⇒ ∃! y, g y z) z) : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists1(x, Not(x)),
             '(∃! x, ¬x) : 𝔹'),
            (Not(Exists1(x, x)),
             '¬(∃! x, x) : 𝔹'),
            (Not(Exists1(x, Not(x))),
             '¬(∃! x, ¬x) : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Exists1(x, y), z),
             '(∃! x, y) ∧ z : 𝔹'),
            (Exists1(x, And(y, z)),
             '(∃! x, y ∧ z) : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Exists1(x, y), z),
             '(∃! x, y) ∨ z : 𝔹'),
            (Exists1(x, Or(y, z)),
             '(∃! x, y ∨ z) : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Exists1(x, y), z),
             '(∃! x, y) → z : 𝔹'),
            (Exists1(x, Implies(y, z)),
             '(∃! x, y → z) : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Exists1(x, y), z),
             '(∃! x, y) ↔ z : 𝔹'),
            (Exists1(x, Iff(y, z)),
             '(∃! x, y ↔ z) : 𝔹'),
            omit_types=True)

    def test_forall(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Forall(x, Exists1(y, z)),
             '(∀ x, ∃! y, z) : 𝔹'),
            (Forall(x, y, Exists1(z, h(x, y, z))),
             '(∀ x y, ∃! z, h x y z) : 𝔹'),
            (Forall(x, Exists1(y, z, h(x, y, z))),
             '(∀ x, ∃! y z, h x y z) : 𝔹'),
            (Exists1(x, Forall(y, z)),
             '(∃! x, ∀ y, z) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Exists(x, Exists1(y, z)),
             '(∃ x, ∃! y, z) : 𝔹'),
            (Exists(x, y, Exists1(z, h(x, y, z))),
             '(∃ x y, ∃! z, h x y z) : 𝔹'),
            (Exists(x, Exists1(y, z, h(x, y, z))),
             '(∃ x, ∃! y z, h x y z) : 𝔹'),
            (Exists1(x, Exists(y, z)),
             '(∃! x, ∃ y, z) : 𝔹'),
            omit_types=True)

    def test_misc(self):
        a = TypeVariable('a')
        b = TypeVariable('b')
        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        A, B = Variables('A', 'B', bool)
        P, Q, R, = Constants('P', 'Q', 'R', bool)
        x, y, z = Variables('x', 'y', 'z', bool)
        t = Exists1(x, y, Implies(g(x, y), g(y, x)))
        self.assert_to_ulkb(
            (t,
             '(∃! x y, g x y → g y x) : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Exists1(x, y, z, And(P, Q)),
             '(∃! x y z, P ∧ Q) : 𝔹'),
            (Exists1(x, y, And(Forall(z, And(P, Q)), R)),
             '(∃! x y, (∀ z, P ∧ Q) ∧ R) : 𝔹'),
            (Exists1(x, Abstraction(y, g(x, y))(f(x))),
             '(∃! x, (𝜆 y ⇒ g x y) (f x)) : 𝔹'),
            (Exists1(x, And(Abstraction(y, g(x, y))(f(x)), Falsity())),
             '(∃! x, (𝜆 y ⇒ g x y) (f x) ∧ ⊥) : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Exists1(x, y, z, P),
             '(∃! x, (∃! y, (∃! z, P))) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Exists1(x, y, g(g(x, y), z)),
             '(exists1 x y, g (g x y) z) : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
