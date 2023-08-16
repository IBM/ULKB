# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_And(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(x, y),
             'x ∧ y : 𝔹'),
            (And(x, y, z),
             'x ∧ y ∧ z : 𝔹'),
            (And(x, y, z, w),
             'x ∧ y ∧ z ∧ w : 𝔹'),
            (And(And(x, y, z), w),
             '(x ∧ y ∧ z) ∧ w : 𝔹'),
            (And(And(And(x, y), z), w),
             '((x ∧ y) ∧ z) ∧ w : 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (And(x, y),
             '(x : 𝔹) ∧ (y : 𝔹) : 𝔹'),
            (And(x, y, z),
             '(x : 𝔹) ∧ (y : 𝔹) ∧ (z : 𝔹) : 𝔹'),
            (And(x, y, z, w),
             '(x : 𝔹) ∧ (y : 𝔹) ∧ (z : 𝔹) ∧ (w : 𝔹) : 𝔹'),
            (And(And(x, y, z), w),
             '((x : 𝔹) ∧ (y : 𝔹) ∧ (z : 𝔹)) ∧ (w : 𝔹) : 𝔹'),
            (And(And(And(x, y), z), w),
             '(((x : 𝔹) ∧ (y : 𝔹)) ∧ (z : 𝔹)) ∧ (w : 𝔹) : 𝔹'),
            show_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(x, y),
             'x and y : bool'),
            (And(x, y, z),
             'x and y and z : bool'),
            (And(x, y, z, w),
             'x and y and z and w : bool'),
            (And(x, And(y, z), w),
             'x and (y and z) and w : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(x@{'i': 1}, y@{'j': 2}, k=3),
             '(x {i=1}) ∧ (y {j=2}) {k=3} : 𝔹'),
            (And(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∧ (y {j=2}) ∧ z {k=3} : 𝔹'),
            (And(x@{'i': 1}, And(y@{'j': 2}, z, k=3)),
             '(x {i=1}) ∧ ((y {j=2}) ∧ z {k=3}) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (And(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∧ ((y {j=2}) ∧ z) {k=3} : 𝔹'),
            (And(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∧ ((y {j=2}) ∧ z) {k=3} : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(x, y),
             'x ∧ y : 𝔹'),
            (And(x, y, z),
             'x ∧ (y ∧ z) : 𝔹'),
            (And(x, y, z, w),
             'x ∧ (y ∧ (z ∧ w)) : 𝔹'),
            (And(x, And(y, z), w),
             'x ∧ ((y ∧ z) ∧ w) : 𝔹'),
            show_parentheses=True, show_types=False)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(x@bool, y, z@bool),
             '(x : 𝔹) ∧ (y : 𝔹) ∧ (z : 𝔹) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(And(x, y)),
             'f (x ∧ y) : 𝔹'),
            (And(f(x), y),
             'f x ∧ y : 𝔹'),
            (And(x, f(y)),
             'x ∧ f y : 𝔹'),
            show_types=False)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        v = Variable('v', type=a)
        self.assert_to_ulkb(
            (Abstraction(v, And(x, y)),
             '(𝜆 v ⇒ x ∧ y) : a → 𝔹'),
            (And(Abstraction(v, And(x, y))(x), y),
             '(𝜆 v ⇒ x ∧ y) x ∧ y : 𝔹'),
            (And(x, Abstraction(v, And(x, y))(f(x))),
             'x ∧ (𝜆 v ⇒ x ∧ y) (f x) : 𝔹'),
            show_types=False)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Not(x), Falsity()),
             '¬x ∧ ⊥ : 𝔹'),
            (Not(And(x, Falsity())),
             '¬(x ∧ ⊥) : 𝔹'),
            (And(Not(And(x, y, z)), w),
             '¬(x ∧ y ∧ z) ∧ w : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(And(x, y), z),
             'x ∧ y ∨ z : 𝔹'),
            (And(Or(x, y), z),
             '(x ∨ y) ∧ z : 𝔹'),
            (And(x, Or(y, z)),
             'x ∧ (y ∨ z) : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(And(x, y), z),
             'x ∧ y → z : 𝔹'),
            (And(Implies(x, y), z),
             '(x → y) ∧ z : 𝔹'),
            (And(x, Implies(y, z)),
             'x ∧ (y → z) : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(And(x, y), z),
             'x ∧ y ↔ z : 𝔹'),
            (And(Iff(x, y), z),
             '(x ↔ y) ∧ z : 𝔹'),
            (And(x, Iff(y, z)),
             'x ∧ (y ↔ z) : 𝔹'),
            omit_types=True)

    def test_forall(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Forall(x, And(x, y)),
             '(∀ x, x ∧ y) : 𝔹'),
            (And(Forall(x, And(x, y)), y),
             '(∀ x, x ∧ y) ∧ y : 𝔹'),
            (And(x, Forall(x, And(x, y))),
             'x ∧ (∀ x, x ∧ y) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists(x, And(x, y)),
             '(∃ x, x ∧ y) : 𝔹'),
            (And(Exists(x, And(x, y)), y),
             '(∃ x, x ∧ y) ∧ y : 𝔹'),
            (And(x, Exists(x, And(x, y))),
             'x ∧ (∃ x, x ∧ y) : 𝔹'),
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
        t = And(And(A, B), Not(A), Not(B), k1=1)
        self.assert_to_ulkb(
            (t,
             '(A ∧ B) ∧ ¬A ∧ ¬B : 𝔹'),
            (And(A, true),
             'A ∧ ⊤ : 𝔹'),
            (And(false, B),
             '⊥ ∧ B : 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (And(P, Q, R),
             'P ∧ Q ∧ R : 𝔹'),
            (And(P, Or(Q, Q), R),
             'P ∧ (Q ∨ Q) ∧ R : 𝔹'),
            (And(And(P, Q), R),
             '(P ∧ Q) ∧ R : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (And(P, Q, R, P),
             'P ∧ (Q ∧ (R ∧ P)) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (And(P, Q, g(g(x, y), z)),
             'P and Q and g (g x y) z : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
