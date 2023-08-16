# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Truth(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Truth(),
             '⊤ : 𝔹'),
            (g(Truth(), Truth()),
             '(g : 𝔹 → 𝔹 → 𝔹) (⊤ : 𝔹) (⊤ : 𝔹) : 𝔹'),
            (Equal(Truth(), Truth()),
             '(⊤ : 𝔹) ↔ (⊤ : 𝔹) : 𝔹'),
            (Abstraction(x, Truth()),
             '(𝜆 (x : a) ⇒ (⊤ : 𝔹)) : a → 𝔹'),
            (f(Abstraction(x, Truth())),
             '(f : (a → 𝔹) → a → 𝔹) (𝜆 (x : a) ⇒ (⊤ : 𝔹)) : a → 𝔹'))

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Truth(),
             'true : bool'),
            (Truth(i=1, j=(-1, Truth())),
             'true : bool'),
            ensure_ascii=True)

    def test_show_annotations(self):
        top = Truth(i=1, j=(-1, Truth()))
        self.assert_to_ulkb(
            (top,
             '⊤ : 𝔹'),
            show_annotations=False)

        self.assert_to_ulkb(
            (top,
             '⊤ {i=1, j=(-1, ⟨⊤ : 𝔹⟩)} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (top,
             '⊤ {i=1, j=(-1, ⟨⊤ : 𝔹⟩)} : 𝔹'),
            show_annotations=True, show_parentheses=True)

        self.assert_to_ulkb(
            (top,
             'true {i=1, j=(-1, <true : bool>)} : bool'),
            show_annotations=True, ensure_ascii=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Truth(),
             '⊤ : 𝔹'),
            (g(Truth(), Truth()),
             '(g ⊤) ⊤ : 𝔹'),
            show_parentheses=True, show_types=False)

    def test_show_types(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Truth(),
             '⊤ : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (g(Truth(), Truth()),
             '(g : 𝔹 → 𝔹 → 𝔹) (⊤ : 𝔹) (⊤ : 𝔹) : 𝔹'),
            (g(Truth(), Truth()),
             '(g : 𝔹 → 𝔹 → 𝔹) (⊤ : 𝔹) (⊤ : 𝔹) : 𝔹'),
            show_types=True)

        self.assert_to_ulkb(
            (g(f(Truth()), Truth()),
             'g (f ⊤) ⊤ : 𝔹'),
            (g(Truth(), Truth()),
             'g ⊤ ⊤ : 𝔹'),
            show_types=False)

    def test_misc(self):
        t = Truth(k1=2, k2=1)
        self.assert_to_ulkb(
            (t,
             '⊤ : 𝔹'))

        self.assert_to_ulkb(
            (t,
             '⊤ {k1=2, k2=1} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t,
             'true {k1=2, k2=1} : bool'),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊤ {k1=2, k2=1} : 𝔹'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊤ {k1=2, k2=1} : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '⊤ : 𝔹'),
            omit_annotations=True)


if __name__ == '__main__':
    main()
