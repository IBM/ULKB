# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Iff(TestSerializerULKB):

    def test_defaultsa(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(x, y),
             'x ↔ y : 𝔹'),
            (Iff(x, y, z),
             'x ↔ y ↔ z : 𝔹'),
            (Iff(x, y, z, w),
             'x ↔ y ↔ z ↔ w : 𝔹'),
            (Iff(Iff(x, y, z), w),
             '(x ↔ y ↔ z) ↔ w : 𝔹'),
            (Iff(Iff(Iff(x, y), z), w),
             '((x ↔ y) ↔ z) ↔ w : 𝔹'),
            omit_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(x, y),
             'x <-> y : bool'),
            (Iff(x, y, z),
             'x <-> y <-> z : bool'),
            (Iff(x, y, z, w),
             'x <-> y <-> z <-> w : bool'),
            (Iff(x, Iff(y, z), w),
             'x <-> (y <-> z) <-> w : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(x@{'i': 1}, y@{'j': 2}, k=3),
             '(x {i=1}) ↔ (y {j=2}) {k=3} : 𝔹'),
            (Iff(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ↔ (y {j=2}) ↔ z {k=3} : 𝔹'),
            (Iff(x@{'i': 1}, Iff(y@{'j': 2}, z, k=3)),
             '(x {i=1}) ↔ ((y {j=2}) ↔ z {k=3}) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Iff(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ↔ ((y {j=2}) ↔ z) {k=3} : 𝔹'),
            (Iff(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ↔ ((y {j=2}) ↔ z) {k=3} : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(x, y),
             'x ↔ y : 𝔹'),
            (Iff(x, y, z),
             'x ↔ (y ↔ z) : 𝔹'),
            (Iff(x, y, z, w),
             'x ↔ (y ↔ (z ↔ w)) : 𝔹'),
            show_parentheses=True, omit_types=True)

        self.assert_to_ulkb(
            (Iff(x, Iff(y, z), w),
             'x ↔ ((y ↔ z) ↔ w) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(x@bool, y, z@bool),
             '(x : 𝔹) ↔ (y : 𝔹) ↔ (z : 𝔹) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Iff(x, y)),
             'f (x ↔ y) : 𝔹'),
            (Iff(f(x), y),
             'f x ↔ y : 𝔹'),
            (Iff(x, f(y)),
             'x ↔ f y : 𝔹'),
            omit_types=True)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        v = Variable('v', type=a)
        self.assert_to_ulkb(
            (Abstraction(v, Iff(x, y)),
             '(𝜆 v ⇒ x ↔ y) : a → 𝔹'),
            (Iff(Abstraction(v, Iff(x, y))(x), y),
             '(𝜆 v ⇒ x ↔ y) x ↔ y : 𝔹'),
            (Iff(x, Abstraction(v, Iff(x, y))(v)),
             'x ↔ (𝜆 v ⇒ x ↔ y) v : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Not(x), Falsity()),
             '¬x ↔ ⊥ : 𝔹'),
            (Not(Iff(x, Falsity())),
             '¬(x ↔ ⊥) : 𝔹'),
            (Iff(Not(Iff(x, y, z)), w),
             '¬(x ↔ y ↔ z) ↔ w : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Iff(x, y), z),
             '(x ↔ y) ∧ z : 𝔹'),
            (Iff(And(x, y), z),
             'x ∧ y ↔ z : 𝔹'),
            (Iff(x, And(y, z)),
             'x ↔ y ∧ z : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Iff(x, y), z),
             '(x ↔ y) ∨ z : 𝔹'),
            (Iff(Or(x, y), z),
             'x ∨ y ↔ z : 𝔹'),
            (Iff(x, Or(y, z)),
             'x ↔ y ∨ z : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Iff(x, y), z),
             '(x ↔ y) → z : 𝔹'),
            (Iff(Implies(x, y), z),
             'x → y ↔ z : 𝔹'),
            (Iff(x, Implies(y, z)),
             'x ↔ y → z : 𝔹'),
            omit_types=True)

    def test_forall(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Forall(x, Iff(x, y)),
             '(∀ x, x ↔ y) : 𝔹'),
            (Iff(Forall(x, Iff(x, y)), y),
             '(∀ x, x ↔ y) ↔ y : 𝔹'),
            (Iff(x, Forall(x, Iff(x, y))),
             'x ↔ (∀ x, x ↔ y) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists(x, Iff(x, y)),
             '(∃ x, x ↔ y) : 𝔹'),
            (Iff(Exists(x, Iff(x, y)), y),
             '(∃ x, x ↔ y) ↔ y : 𝔹'),
            (Iff(x, Exists(x, Iff(x, y))),
             'x ↔ (∃ x, x ↔ y) : 𝔹'),
            omit_types=True)

    def test_exists1(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists1(x, Iff(x, y)),
             '(∃! x, x ↔ y) : 𝔹'),
            (Iff(Exists1(x, Iff(x, y)), y),
             '(∃! x, x ↔ y) ↔ y : 𝔹'),
            (Iff(x, Exists1(x, Iff(x, y))),
             'x ↔ (∃! x, x ↔ y) : 𝔹'),
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
        t = Iff(Iff(A, B), Not(A), Not(B), k1=1)
        self.assert_to_ulkb(
            (t,
             '(A ↔ B) ↔ ¬A ↔ ¬B : 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (Iff(P, Q, R),
             'P ↔ Q ↔ R : 𝔹'),
            (Iff(P, And(Q, Q), R),
             'P ↔ Q ∧ Q ↔ R : 𝔹'),
            (Iff(Iff(P, Q), R),
             '(P ↔ Q) ↔ R : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Iff(P, Q, R, P),
             'P ↔ (Q ↔ (R ↔ P)) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Iff(P, Q, g(g(x, y), z)),
             'P <-> Q <-> g (g x y) z : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
