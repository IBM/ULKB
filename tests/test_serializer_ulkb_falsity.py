# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Falsity(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Falsity(),
             '⊥ : 𝔹'),
            (g(Falsity(), Falsity()),
             '(g : 𝔹 → 𝔹 → 𝔹) (⊥ : 𝔹) (⊥ : 𝔹) : 𝔹'),
            (Equal(Falsity(), Truth()),
             '(⊥ : 𝔹) ↔ (⊤ : 𝔹) : 𝔹'),
            (Abstraction(x, Falsity()),
             '(𝜆 (x : a) ⇒ (⊥ : 𝔹)) : a → 𝔹'),
            (f(Abstraction(x, Falsity())),
             '(f : (a → 𝔹) → a → 𝔹) (𝜆 (x : a) ⇒ (⊥ : 𝔹)) : a → 𝔹'))

    def test_ensure_ascii(self):
        self.assert_to_ulkb(
            (Falsity(),
             'false : bool'),
            ensure_ascii=True)

    def test_show_annotations(self):
        bot = Falsity(i=1, j=(-1, Falsity()))
        self.assert_to_ulkb(
            (bot,
             '⊥ : 𝔹'),
            show_annotations=False, show_types=False)

        self.assert_to_ulkb(
            (bot,
             '⊥ {i=1, j=(-1, ⟨⊥ : 𝔹⟩)} : 𝔹'),
            show_annotations=True, show_types=False)

        self.assert_to_ulkb(
            (bot,
             'false {i=1, j=(-1, <false : bool>)} : bool'),
            show_annotations=True, ensure_ascii=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Falsity(),
             '⊥ : 𝔹'),
            (g(Falsity(), Falsity()),
             '(g ⊥) ⊥ : 𝔹'),
            show_parentheses=True, show_types=False)

        self.assert_to_ulkb(
            (g(Falsity(), Falsity()),
             '((g : 𝔹 → (𝔹 → 𝔹)) (⊥ : 𝔹)) (⊥ : 𝔹) : 𝔹'),
            show_parentheses=True)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Falsity(),
             '⊥ : 𝔹'),
            (g(Falsity(), f(Falsity())), '\
(g : 𝔹 → 𝔹 → 𝔹) (⊥ : 𝔹) ((f : 𝔹 → 𝔹) (⊥ : 𝔹)) : 𝔹'),
            show_types=True)

    def test_misc(self):
        t = Falsity(k1=2, k2=1)
        self.assert_to_ulkb(
            (t,
             '⊥ : 𝔹'))

        self.assert_to_ulkb(
            (t,
             '⊥ {k1=2, k2=1} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t,
             'false {k1=2, k2=1} : bool'),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊥ {k1=2, k2=1} : 𝔹'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊥ {k1=2, k2=1} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊥ : 𝔹'),
            omit_annotations=True)


if __name__ == '__main__':
    main()
