# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Exists(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x, x),
             '(∃ x, x) : 𝔹'),
            (Exists(x, y, g(x, y)),
             '(∃ x y, g x y) : 𝔹'),
            (Exists(x, Exists(y, g(x, y))),
             '(∃ x y, g x y) : 𝔹'),
            (Exists(z, g(z, Exists(x, y, g(x, y)))),
             '(∃ z, g z (∃ x y, g x y)) : 𝔹'),
            omit_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x, x),
             '(exists x, x) : bool'),
            (Exists(x, y, g(x, y)),
             '(exists x y, g x y) : bool'),
            (Exists(x, Exists(y, g(x, y))),
             '(exists x y, g x y) : bool'),
            (Exists(z, g(z, Exists(x, y, g(x, y)))),
             '(exists z, g z (exists x y, g x y)) : bool'),
            (Exists(Variable('𝛼', a), x),
             '(exists \\U0001d6fc, x) : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∃ (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Exists(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∃ (x {i=1}) (y {j=2}), z) {k=3} : 𝔹'),
            (Exists(x, Exists(y, z, k=3)),
             '(∃ x, ((∃ y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Exists(y, z, k=3)),
             '(𝜆 x ⇒ ((∃ y, z) {k=3})) : 𝔹 → 𝔹'),
            (Exists(x, Abstraction(y, z, k=3)(y)),
             '(∃ x, ((𝜆 y ⇒ z) {k=3}) y) : 𝔹'),
            (Exists(x@{'i': 1}, Exists(y@{'j': 2}, z, k=3)),
             '(∃ (x {i=1}), ((∃ (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Exists(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∃ (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Exists(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∃ (x {i=1}), (∃ (y {j=2}), z)) {k=3} : 𝔹'),
            (Exists(x, Exists(y, z, k=3)),
             '(∃ x, ((∃ y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Exists(y, z, k=3)),
             '(𝜆 x ⇒ ((∃ y, z) {k=3})) : 𝔹 → 𝔹'),
            (Exists(x, Abstraction(y, z, k=3)(y)),
             '(∃ x, (((𝜆 y ⇒ z) {k=3}) y)) : 𝔹'),
            (Exists(x@{'i': 1}, Exists(y@{'j': 2}, z, k=3)),
             '(∃ (x {i=1}), ((∃ (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x, x),
             '(∃ x, x) : 𝔹'),
            (Exists(x, y, g(x, y)),
             '(∃ x, (∃ y, ((g x) y))) : 𝔹'),
            (Exists(x, Exists(y, g(x, y))),
             '(∃ x, (∃ y, ((g x) y))) : 𝔹'),
            (Exists(z, g(z, Exists(x, y, g(x, y)))),
             '(∃ z, ((g z) (∃ x, (∃ y, ((g x) y))))) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x, g(x, x)),
             '(∃ (x : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (x : 𝔹)) : 𝔹'),
            (Exists(x, y, g(x, y)), '\
(∃ (x : 𝔹) (y : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹)) : 𝔹'),
            (Exists(x, f(Exists(y, g(x, y)))), '\
(∃ (x : 𝔹), (f : 𝔹 → 𝔹) (∃ (y : 𝔹), \
(g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹))) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Exists(x, x)),
             'f (∃ x, x) : 𝔹'),
            (Exists(x, f(x)),
             '(∃ x, f x) : 𝔹'),
            (Exists(x, f(y)),
             '(∃ x, f y) : 𝔹'),
            (Exists(x, f(Exists(y, y))),
             '(∃ x, f (∃ y, y)) : 𝔹'),
            omit_types=True)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        b = Variable('b', bool)
        self.assert_to_ulkb(
            (Abstraction(z, Exists(x, b)),
             '(𝜆 z ⇒ ∃ x, b) : 𝔹 → 𝔹'),
            (Exists(x, Abstraction(z, Exists(y, g(y, z)))(z)),
             '(∃ x, (𝜆 z ⇒ ∃ y, g y z) z) : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Exists(x, Not(x)),
             '(∃ x, ¬x) : 𝔹'),
            (Not(Exists(x, x)),
             '¬(∃ x, x) : 𝔹'),
            (Not(Exists(x, Not(x))),
             '¬(∃ x, ¬x) : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Exists(x, y), z),
             '(∃ x, y) ∧ z : 𝔹'),
            (Exists(x, And(y, z)),
             '(∃ x, y ∧ z) : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Exists(x, y), z),
             '(∃ x, y) ∨ z : 𝔹'),
            (Exists(x, Or(y, z)),
             '(∃ x, y ∨ z) : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Exists(x, y), z),
             '(∃ x, y) → z : 𝔹'),
            (Exists(x, Implies(y, z)),
             '(∃ x, y → z) : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Exists(x, y), z),
             '(∃ x, y) ↔ z : 𝔹'),
            (Exists(x, Iff(y, z)),
             '(∃ x, y ↔ z) : 𝔹'),
            omit_types=True)

    def test_forall(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Forall(x, Exists(y, z)),
             '(∀ x, ∃ y, z) : 𝔹'),
            (Forall(x, y, Exists(z, h(x, y, z))),
             '(∀ x y, ∃ z, h x y z) : 𝔹'),
            (Forall(x, Exists(y, z, h(x, y, z))),
             '(∀ x, ∃ y z, h x y z) : 𝔹'),
            (Exists(x, Forall(y, z)),
             '(∃ x, ∀ y, z) : 𝔹'),
            omit_types=True)

    def test_exists1(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Exists1(x, Exists(y, z)),
             '(∃! x, ∃ y, z) : 𝔹'),
            (Exists1(x, y, Exists(z, h(x, y, z))),
             '(∃! x y, ∃ z, h x y z) : 𝔹'),
            (Exists1(x, Exists(y, z, h(x, y, z))),
             '(∃! x, ∃ y z, h x y z) : 𝔹'),
            (Exists(x, Exists1(y, z)),
             '(∃ x, ∃! y, z) : 𝔹'),
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
        t = Exists(x, y, Implies(g(x, y), g(y, x)))
        self.assert_to_ulkb(
            (t,
             '(∃ x y, g x y → g y x) : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Exists(x, y, z, And(P, Q)),
             '(∃ x y z, P ∧ Q) : 𝔹'),
            (Exists(x, y, And(Forall(z, And(P, Q)), R)),
             '(∃ x y, (∀ z, P ∧ Q) ∧ R) : 𝔹'),
            (Exists(x, Abstraction(y, g(x, y))(f(x))),
             '(∃ x, (𝜆 y ⇒ g x y) (f x)) : 𝔹'),
            (Exists(x, And(Abstraction(y, g(x, y))(f(x)), Falsity())),
             '(∃ x, (𝜆 y ⇒ g x y) (f x) ∧ ⊥) : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Exists(x, y, z, P),
             '(∃ x, (∃ y, (∃ z, P))) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Exists(x, y, g(g(x, y), z)),
             '(exists x y, g (g x y) z) : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
