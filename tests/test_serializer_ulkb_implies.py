# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Implies(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(x, y),
             'x → y : 𝔹'),
            (Implies(x, y, z),
             'x → y → z : 𝔹'),
            (Implies(x, y, z, w),
             'x → y → z → w : 𝔹'),
            (Implies(Implies(x, y, z), w),
             '(x → y → z) → w : 𝔹'),
            (Implies(Implies(Implies(x, y), z), w),
             '((x → y) → z) → w : 𝔹'),
            show_types=False)

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(x, y),
             'x -> y : bool'),
            (Implies(x, y, z),
             'x -> y -> z : bool'),
            (Implies(x, y, z, w),
             'x -> y -> z -> w : bool'),
            (Implies(x, Implies(y, z), w),
             'x -> (y -> z) -> w : bool'),
            ensure_ascii=True, omit_types=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(x@{'i': 1}, y@{'j': 2}, k=3),
             '(x {i=1}) → (y {j=2}) {k=3} : 𝔹'),
            (Implies(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) → (y {j=2}) → z {k=3} : 𝔹'),
            (Implies(x@{'i': 1}, Implies(y@{'j': 2}, z, k=3)),
             '(x {i=1}) → ((y {j=2}) → z {k=3}) : 𝔹'),
            show_annotations=True, omit_types=True)

        self.assert_to_ulkb(
            (Implies(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) → ((y {j=2}) → z) {k=3} : 𝔹'),
            (Implies(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(x {i=1}) → ((y {j=2}) → z) {k=3} : 𝔹'),
            show_annotations=True, show_parentheses=True, omit_types=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(x, y),
             'x → y : 𝔹'),
            (Implies(x, y, z),
             'x → (y → z) : 𝔹'),
            (Implies(x, y, z, w),
             'x → (y → (z → w)) : 𝔹'),
            show_parentheses=True, omit_types=True)

        self.assert_to_ulkb(
            (Implies(x, Implies(y, z), w),
             'x → ((y → z) → w) : 𝔹'),
            show_parentheses=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(x@bool, y, z@bool),
             '(x : 𝔹) → (y : 𝔹) → (z : 𝔹) : 𝔹'))

    def test_application(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (f(Implies(x, y)),
             'f (x → y) : 𝔹'),
            (Implies(f(x), y),
             'f x → y : 𝔹'),
            (Implies(x, f(y)),
             'x → f y : 𝔹'),
            show_types=False)

    def test_abstraction(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        v = Variable('v', type=a)
        self.assert_to_ulkb(
            (Abstraction(v, Implies(x, y)),
             '(𝜆 v ⇒ x → y) : a → 𝔹'),
            (Implies(Abstraction(v, Implies(x, y))(x), y),
             '(𝜆 v ⇒ x → y) x → y : 𝔹'),
            (Implies(x, Abstraction(v, Implies(x, y))(x)),
             'x → (𝜆 v ⇒ x → y) x : 𝔹'),
            omit_types=True)

    def test_not(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Implies(Not(x), Falsity()),
             '¬x → ⊥ : 𝔹'),
            (Not(Implies(x, Falsity())),
             '¬(x → ⊥) : 𝔹'),
            (Implies(Not(Implies(x, y, z)), w),
             '¬(x → y → z) → w : 𝔹'),
            omit_types=True)

    def test_and(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (And(Implies(x, y), z),
             '(x → y) ∧ z : 𝔹'),
            (Implies(And(x, y), z),
             'x ∧ y → z : 𝔹'),
            (Implies(x, And(y, z)),
             'x → y ∧ z : 𝔹'),
            omit_types=True)

    def test_or(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Or(Implies(x, y), z),
             '(x → y) ∨ z : 𝔹'),
            (Implies(Or(x, y), z),
             'x ∨ y → z : 𝔹'),
            (Implies(x, Or(y, z)),
             'x → y ∨ z : 𝔹'),
            omit_types=True)

    def test_iff(self):
        a = TypeVariable('a')
        x, y, z, w = Constants('x', 'y', 'z', 'w', bool)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Iff(Implies(x, y), z),
             'x → y ↔ z : 𝔹'),
            (Implies(Iff(x, y), z),
             '(x ↔ y) → z : 𝔹'),
            (Implies(x, Iff(y, z)),
             'x → (y ↔ z) : 𝔹'),
            omit_types=True)

    def test_forall(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Forall(x, Implies(x, y)),
             '(∀ x, x → y) : 𝔹'),
            (Implies(Forall(x, Implies(x, y)), y),
             '(∀ x, x → y) → y : 𝔹'),
            (Implies(x, Forall(x, Implies(x, y))),
             'x → (∀ x, x → y) : 𝔹'),
            omit_types=True)

    def test_exists(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists(x, Implies(x, y)),
             '(∃ x, x → y) : 𝔹'),
            (Implies(Exists(x, Implies(x, y)), y),
             '(∃ x, x → y) → y : 𝔹'),
            (Implies(x, Exists(x, Implies(x, y))),
             'x → (∃ x, x → y) : 𝔹'),
            omit_types=True)

    def test_exists1(self):
        x, y = Variables('x', 'y', bool)
        self.assert_to_ulkb(
            (Exists1(x, Implies(x, y)),
             '(∃! x, x → y) : 𝔹'),
            (Implies(Exists1(x, Implies(x, y)), y),
             '(∃! x, x → y) → y : 𝔹'),
            (Implies(x, Exists1(x, Implies(x, y))),
             'x → (∃! x, x → y) : 𝔹'),
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
        t = Implies(Implies(A, B), Not(A), Not(B), k1=1)
        self.assert_to_ulkb(
            (t,
             '(A → B) → ¬A → ¬B : 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (Implies(P, Q, R),
             'P → Q → R : 𝔹'),
            (Implies(P, Or(Q, Q), R),
             'P → Q ∨ Q → R : 𝔹'),
            (Implies(Implies(P, Q), R),
             '(P → Q) → R : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (Implies(P, Q, R, P),
             'P → (Q → (R → P)) : 𝔹'),
            omit_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Implies(P, Q, g(x, g(y, z))),
             'P -> Q -> g x (g y z) : bool'),
            ensure_ascii=True, show_types=False)


if __name__ == '__main__':
    main()
