# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Forall(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x, x),
             '(∀ x, x) : 𝔹'),
            (Forall(x, y, g(x, y)),
             '(∀ x y, g x y) : 𝔹'),
            (Forall(x, Forall(y, g(x, y))),
             '(∀ x y, g x y) : 𝔹'),
            (Forall(z, g(z, Forall(x, y, g(x, y)))),
             '(∀ z, g z (∀ x y, g x y)) : 𝔹'),
            omit_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x, x),
             '(forall x, x) : bool'),
            (Forall(x, y, g(x, y)),
             '(forall x y, g x y) : bool'),
            (Forall(x, Forall(y, g(x, y))),
             '(forall x y, g x y) : bool'),
            (Forall(z, g(z, Forall(x, y, g(x, y)))),
             '(forall z, g z (forall x y, g x y)) : bool'),
            (Forall(Variable('𝛼', bool), x),
             '(forall \\U0001d6fc, x) : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∀ (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Forall(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∀ (x {i=1}) (y {j=2}), z) {k=3} : 𝔹'),
            (Forall(x, Forall(y, z, k=3)),
             '(∀ x, ((∀ y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Forall(y, z, k=3)),
             '(𝜆 x ⇒ ((∀ y, z) {k=3})) : 𝔹 → 𝔹'),
            (Forall(x, Abstraction(y, z, k=3)(y)),
             '(∀ x, ((𝜆 y ⇒ z) {k=3}) y) : 𝔹'),
            (Forall(x@{'i': 1}, Forall(y@{'j': 2}, z, k=3)),
             '(∀ (x {i=1}), ((∀ (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Forall(x@{'i': 1}, y@{'j': 2}, k=3),
             '(∀ (x {i=1}), (y {j=2})) {k=3} : 𝔹'),
            (Forall(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(∀ (x {i=1}), (∀ (y {j=2}), z)) {k=3} : 𝔹'),
            (Forall(x, Forall(y, z, k=3)),
             '(∀ x, ((∀ y, z) {k=3})) : 𝔹'),
            (Abstraction(x, Forall(y, z, k=3)),
             '(𝜆 x ⇒ ((∀ y, z) {k=3})) : 𝔹 → 𝔹'),
            (Forall(x, Abstraction(y, z, k=3)(y)),
             '(∀ x, (((𝜆 y ⇒ z) {k=3}) y)) : 𝔹'),
            (Forall(x@{'i': 1}, Forall(y@{'j': 2}, z, k=3)),
             '(∀ (x {i=1}), ((∀ (y {j=2}), z) {k=3})) : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x, x),
             '(∀ x, x) : 𝔹'),
            (Forall(x, y, g(x, y)),
             '(∀ x, (∀ y, ((g x) y))) : 𝔹'),
            (Forall(x, Forall(y, g(x, y))),
             '(∀ x, (∀ y, ((g x) y))) : 𝔹'),
            (Forall(z, g(z, Forall(x, y, g(x, y)))),
             '(∀ z, ((g z) (∀ x, (∀ y, ((g x) y))))) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x, g(x, x)), '\
(∀ (x : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (x : 𝔹)) : 𝔹'),
            (Forall(x, y, g(x, y)), '\
(∀ (x : 𝔹) (y : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹)) : 𝔹'),
            (Forall(x, f(Forall(y, g(x, y)))), '\
(∀ (x : 𝔹), (f : 𝔹 → 𝔹) \
(∀ (y : 𝔹), (g : 𝔹 → 𝔹 → 𝔹) (x : 𝔹) (y : 𝔹))) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Forall(x, x)),
             'f (∀ x, x) : 𝔹'),
            (Forall(x, f(x)),
             '(∀ x, f x) : 𝔹'),
            (Forall(x, f(y)),
             '(∀ x, f y) : 𝔹'),
            (Forall(x, f(Forall(y, y))),
             '(∀ x, f (∀ y, y)) : 𝔹'),
            omit_types=True)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        b = Constant('b', bool)
        g = Variable('g', FunctionType(bool, bool, bool))
        self.assert_to_ulkb(
            (Abstraction(z, Forall(x, b)),
             '(𝜆 z ⇒ ∀ x, b) : 𝔹 → 𝔹'),
            (Forall(g, Abstraction(z, Forall(y, g(y, z)))(z)),
             '(∀ g, (𝜆 z ⇒ ∀ y, g y z) z) : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Forall(x, Not(x)),
             '(∀ x, ¬x) : 𝔹'),
            (Not(Forall(x, x)),
             '¬(∀ x, x) : 𝔹'),
            (Not(Forall(x, Not(x))),
             '¬(∀ x, ¬x) : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Forall(x, y), z),
             '(∀ x, y) ∧ z : 𝔹'),
            (Forall(x, And(y, z)),
             '(∀ x, y ∧ z) : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Forall(x, y), z),
             '(∀ x, y) ∨ z : 𝔹'),
            (Forall(x, Or(y, z)),
             '(∀ x, y ∨ z) : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Forall(x, y), z),
             '(∀ x, y) → z : 𝔹'),
            (Forall(x, Implies(y, z)),
             '(∀ x, y → z) : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Forall(x, y), z),
             '(∀ x, y) ↔ z : 𝔹'),
            (Forall(x, Iff(y, z)),
             '(∀ x, y ↔ z) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Exists(x, Forall(y, z)),
             '(∃ x, ∀ y, z) : 𝔹'),
            (Exists(x, y, Forall(z, h(x, y, z))),
             '(∃ x y, ∀ z, h x y z) : 𝔹'),
            (Exists(x, Forall(y, z, h(x, y, z))),
             '(∃ x, ∀ y z, h x y z) : 𝔹'),
            (Forall(x, Exists(y, z)),
             '(∀ x, ∃ y, z) : 𝔹'),
            omit_types=True)

    def test_exists1(self):
        a = TypeVariable('a')
        x, y, z, w = Variables('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        h = Constant('h', FunctionType(a, a, a, bool))
        self.assert_to_ulkb(
            (Exists1(x, Forall(y, z)),
             '(∃! x, ∀ y, z) : 𝔹'),
            (Exists1(x, y, Forall(z, h(x, y, z))),
             '(∃! x y, ∀ z, h x y z) : 𝔹'),
            (Exists1(x, Forall(y, z, h(x, y, z))),
             '(∃! x, ∀ y z, h x y z) : 𝔹'),
            (Forall(x, Exists1(y, z)),
             '(∀ x, ∃! y, z) : 𝔹'),
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
        t = Forall(x, y, Implies(g(x, y), g(y, x)))
        self.assert_to_ulkb(
            (t,
             '(∀ x y, g x y → g y x) : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (And(Forall(x, y, z, And(P, Q)), P),
             '(∀ x y z, P ∧ Q) ∧ P : 𝔹'),
            (Forall(x, And(Forall(y, P), Q)),
             '(∀ x, (∀ y, P) ∧ Q) : 𝔹'),
            (Forall(x, Abstraction(y, g(x, y))(x)),
             '(∀ x, (𝜆 y ⇒ g x y) x) : 𝔹'),
            (And(Abstraction(x, f(Forall(y, f(y))))(f(x)), P),
             '(𝜆 x ⇒ f (∀ y, f y)) (f x) ∧ P : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Forall(x, y, z, P),
             '(∀ x, (∀ y, (∀ z, P))) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Forall(x, y, g(g(x, y), z)),
             '(forall x y, g (g x y) z) : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
