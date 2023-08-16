# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Or(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(x, y),
             'x ∨ y : 𝔹'),
            (Or(x, y, z),
             'x ∨ y ∨ z : 𝔹'),
            (Or(x, y, z, w),
             'x ∨ y ∨ z ∨ w : 𝔹'),
            (Or(Or(x, y, z), w),
             '(x ∨ y ∨ z) ∨ w : 𝔹'),
            (Or(Or(Or(x, y), z), w),
             '((x ∨ y) ∨ z) ∨ w : 𝔹'),
            omit_types=True)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(x, y),
             'x or y : bool'),
            (Or(x, y, z),
             'x or y or z : bool'),
            (Or(x, y, z, w),
             'x or y or z or w : bool'),
            (Or(x, Or(y, z), w),
             'x or (y or z) or w : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(x@{'i': 1}, y@{'j': 2}, k=3),
             '(x {i=1}) ∨ (y {j=2}) {k=3} : 𝔹'),
            (Or(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∨ (y {j=2}) ∨ z {k=3} : 𝔹'),
            (Or(x@{'i': 1}, Or(y@{'j': 2}, z, k=3)),
             '(x {i=1}) ∨ ((y {j=2}) ∨ z {k=3}) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Or(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∨ ((y {j=2}) ∨ z) {k=3} : 𝔹'),
            (Or(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) ∨ ((y {j=2}) ∨ z) {k=3} : 𝔹'),
            show_annotations=True, show_parentheses=True, show_types=False)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(x, y),
             'x ∨ y : 𝔹'),
            (Or(x, y, z),
             'x ∨ (y ∨ z) : 𝔹'),
            (Or(x, y, z, w),
             'x ∨ (y ∨ (z ∨ w)) : 𝔹'),
            show_parentheses=True, omit_types=True)

        self.assert_to_ulkb(
            (Or(x, Or(y, z), w),
             'x ∨ ((y ∨ z) ∨ w) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(x@bool, y, z@bool),
             '(x : 𝔹) ∨ (y : 𝔹) ∨ (z : 𝔹) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Or(x, y)),
             'f (x ∨ y) : 𝔹'),
            (Or(f(x), y),
             'f x ∨ y : 𝔹'),
            (Or(x, f(y)),
             'x ∨ f y : 𝔹'),
            omit_types=True)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        v = Variable('v', type=a)
        self.assert_to_ulkb(
            (Abstraction(v, Or(x, y)),
             '(𝜆 v ⇒ x ∨ y) : a → 𝔹'),
            (Or(Abstraction(v, Or(x, y))(x), y),
             '(𝜆 v ⇒ x ∨ y) x ∨ y : 𝔹'),
            (Or(x, Abstraction(v, Or(x, y))(x)),
             'x ∨ (𝜆 v ⇒ x ∨ y) x : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Not(x), Falsity()),
             '¬x ∨ ⊥ : 𝔹'),
            (Not(Or(x, Falsity())),
             '¬(x ∨ ⊥) : 𝔹'),
            (Or(Not(Or(x, y, z)), w),
             '¬(x ∨ y ∨ z) ∨ w : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Or(x, y), z),
             '(x ∨ y) ∧ z : 𝔹'),
            (Or(And(x, y), z),
             'x ∧ y ∨ z : 𝔹'),
            (Or(x, And(y, z)),
             'x ∨ y ∧ z : 𝔹'),
            omit_types=True)

    def test_implies(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Or(x, y), z),
             'x ∨ y → z : 𝔹'),
            (Or(Implies(x, y), z),
             '(x → y) ∨ z : 𝔹'),
            (Or(x, Implies(y, z)),
             'x ∨ (y → z) : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Or(x, y), z),
             'x ∨ y ↔ z : 𝔹'),
            (Or(Iff(x, y), z),
             '(x ↔ y) ∨ z : 𝔹'),
            (Or(x, Iff(y, z)),
             'x ∨ (y ↔ z) : 𝔹'),
            omit_types=True)

    def test_forall(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Forall(x, Or(x, y)),
             '(∀ x, x ∨ y) : 𝔹'),
            (Or(Forall(x, Or(x, y)), y),
             '(∀ x, x ∨ y) ∨ y : 𝔹'),
            (Or(x, Forall(x, Or(x, y))),
             'x ∨ (∀ x, x ∨ y) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists(x, Or(x, y)),
             '(∃ x, x ∨ y) : 𝔹'),
            (Or(Exists(x, Or(x, y)), y),
             '(∃ x, x ∨ y) ∨ y : 𝔹'),
            (Or(x, Exists(x, Or(x, y))),
             'x ∨ (∃ x, x ∨ y) : 𝔹'),
            show_types=False)

    def test_exists1(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists1(x, Or(x, y)),
             '(∃! x, x ∨ y) : 𝔹'),
            (Or(Exists1(x, Or(x, y)), y),
             '(∃! x, x ∨ y) ∨ y : 𝔹'),
            (Or(x, Exists1(x, Or(x, y))),
             'x ∨ (∃! x, x ∨ y) : 𝔹'),
            show_types=False)

    def test_misc(self):
        a = TypeVariable('a')
        b = TypeVariable('b')
        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        A, B = Variables('A', 'B', bool)
        P, Q, R, = Constants('P', 'Q', 'R', bool)
        x, y, z = Variables('x', 'y', 'z', bool)
        t = Or(Or(A, B), Not(A), Not(B), k1=1)
        self.assert_to_ulkb(
            (t,
             '(A ∨ B) ∨ ¬A ∨ ¬B : 𝔹'),
            (Or(A, true),
             'A ∨ ⊤ : 𝔹'),
            (Or(false, B),
             '⊥ ∨ B : 𝔹'),
            omit_types=True, show_types=False)

        self.assert_to_ulkb(
            (Or(P, Q, R),
             'P ∨ Q ∨ R : 𝔹'),
            (Or(P, Implies(Q, Q), R),
             'P ∨ (Q → Q) ∨ R : 𝔹'),
            (Or(Or(P, Q), R),
             '(P ∨ Q) ∨ R : 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (Or(P, Q, R, P),
             'P ∨ (Q ∨ (R ∨ P)) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Or(P, Q, g(g(x, y), z)),
                'P or Q or g (g x y) z : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
