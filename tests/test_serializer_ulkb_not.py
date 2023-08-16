# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Not(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Not(Truth()),
             '¬(⊤ : 𝔹) : 𝔹'),
            (Not(Not(Truth())),
             '¬¬(⊤ : 𝔹) : 𝔹'),
            (Not(Falsity()),
             '¬(⊥ : 𝔹) : 𝔹'),
            (Not(Not(Falsity())),
             '¬¬(⊥ : 𝔹) : 𝔹'),
            (Not(f(x@bool)),
             '¬(f : 𝔹 → 𝔹) (x : 𝔹) : 𝔹'),
            (Not(Equal(x, x)),
             '(x : a) ≠ (x : a) : 𝔹'),
            (Not(Equal(Not(x@bool), x@bool)),
             '¬(¬(x : 𝔹) ↔ (x : 𝔹)) : 𝔹'))

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Not(f(x@bool)),
             'not f x : bool'),
            ensure_ascii=True, show_types=False)

    def test_show_annotations(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Not((y@bool)@{'i': 1}, j=2),
             '¬y : 𝔹'),
            show_annotations=False, show_types=False)

        y = y@bool
        self.assert_to_ulkb(
            (Not(y@{'i': 1}, j=2),
             '¬(y {i=1} : 𝔹) {j=2} : 𝔹'),
            (Not(Not(y@{'i': 1}, j=2), k=3),
             '¬(¬(y {i=1} : 𝔹) {j=2}) {k=3} : 𝔹'),
            (Not(Equal(x@{'i': 1}, x)),
             '(x {i=1} : a) ≠ (x : a) : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (Not(y@{'i': 1}, j=2),
             'not (y {i=1} : bool) {j=2} : bool'),
            show_annotations=True, ensure_ascii=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Not(Equal(x@{'i': 1}, x)),
             '¬(x = x) : 𝔹'),
            show_parentheses=True, show_types=False)

        y = y@bool
        self.assert_to_ulkb(
            (Not(y@{'i': 1}, j=2),
             '¬(y {i=1}) {j=2} : 𝔹'),
            (Not(Not(y@{'i': 1}, j=2), k=3),
             '¬(¬(y {i=1}) {j=2}) {k=3} : 𝔹'),
            (Not(Equal(x@{'i': 1}, x)),
             '¬((x {i=1}) = x) : 𝔹'),
            show_annotations=True, show_parentheses=True, show_types=False)

        self.assert_to_ulkb(
            (Not(y@{'i': 1}, j=2),
             'not (y {i=1}) {j=2} : bool'),
            (Not(Not(y@{'i': 1}, j=2), k=3),
             'not (not (y {i=1}) {j=2}) {k=3} : bool'),
            show_annotations=True, ensure_ascii=True, show_parentheses=True,
            show_types=False)

        self.assert_to_ulkb(
            (Not(Falsity()),
             '¬⊥ : 𝔹'),
            (Not(Equal(x@bool, x@bool)),
             '¬(x ↔ x) : 𝔹'),
            (Equal(Not(y), Not(Not(Equal(y, y)))),
             '¬y ↔ ¬¬(y ↔ y) : 𝔹'),
            show_types=False, show_parentheses=False)

        self.assert_to_ulkb(
            (Not(Falsity()),
             '¬⊥ : 𝔹'),
            (Not(Equal(x@bool, x@bool)),
             '¬(x ↔ x) : 𝔹'),
            (Equal(Not(y), Not(Not(Equal(y, y)))),
             '(¬y) ↔ (¬¬(y ↔ y)) : 𝔹'),
            show_types=False, show_parentheses=True)

        self.assert_to_ulkb(
            (Not(Equal(f(x)@{'i': x}, x)),
             '¬((f x {i=⟨x : a⟩}) = x) : 𝔹'),
            show_parentheses=True, show_annotations=True, omit_types=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Not(x@bool),
             '¬(x : 𝔹) : 𝔹'),
            (Not(Equal(x, x)),
             '(x : a) ≠ (x : a) : 𝔹'),
            (g(Not(x@bool), Not(f(x@bool))), '\
(g : 𝔹 → 𝔹 → 𝔹) (¬(x : 𝔹)) (¬(f : 𝔹 → 𝔹) (x : 𝔹)) : 𝔹'),
            show_types=True)

        self.assert_to_ulkb(
            (Not(x@bool),
             '¬x : 𝔹'),
            (Not(Equal(x, x)),
             'x ≠ x : 𝔹'),
            (g(Not(x@bool), Not(f(x@bool))), 'g (¬x) (¬f x) : 𝔹'),
            show_types=False)

        y = y@bool
        self.assert_to_ulkb(
            (f(Not(f(y))),
             '(f : 𝔹 → 𝔹) (¬(f : 𝔹 → 𝔹) (y : 𝔹)) : 𝔹'),
            show_types=True)

        self.assert_to_ulkb(
            (Not(y),
             '¬y : 𝔹'),
            (f(Not(f(y))),
             'f (¬f y) : 𝔹'),
            show_types=False)

    def test_misc(self):
        a = TypeVariable('a')
        b = TypeVariable('b')
        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        x, y, z, w = Variables('x', 'y', 'z', 'w', a)
        A = Variable('A', bool)
        t = Not(Not(Not(A)), k1=1, k2=2)
        self.assert_to_ulkb(
            (t,
             '¬¬¬(A : 𝔹) : 𝔹'),
            (Not(Or(true, false)),
             '¬((⊤ : 𝔹) ∨ (⊥ : 𝔹)) : 𝔹'))

        self.assert_to_ulkb(
            (t,
             '¬¬¬(A : 𝔹) {k1=1, k2=2} : 𝔹'),
            show_annotations=True,)

        self.assert_to_ulkb(
            (t,
             'not not not (A : bool) {k1=1, k2=2} : bool'),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '¬¬¬A {k1=1, k2=2} : 𝔹'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '¬¬¬(A : 𝔹) {k1=1, k2=2} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '¬¬¬A : 𝔹'),
            omit_types=True, omit_annotations=True)

        P, Q, R, = Constants('P', 'Q', 'R', bool)
        x, y, z = Variables('x', 'y', 'z', bool)
        self.assert_to_ulkb(
            (Not(P),
             '¬(P : 𝔹) : 𝔹'))

        self.assert_to_ulkb(
            (Not(P),
             '¬(P : 𝔹) : 𝔹'),
            omit_parentheses=False)

        self.assert_to_ulkb(
            (Not(g(x, g(y, z))), '\
not (g : bool -> bool -> bool) (x : bool) \
((g : bool -> bool -> bool) (y : bool) (z : bool)) : bool'),
            ensure_ascii=True)

        self.assert_to_ulkb(
            (Not(g(x, g(y, z))),
             '¬g x (g y z) : 𝔹'),
            show_types=False)


if __name__ == '__main__':
    main()
