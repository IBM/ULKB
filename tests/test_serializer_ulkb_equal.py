# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Equal(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Equal(x@bool, y@bool),
             '(x : 𝔹) ↔ (y : 𝔹) : 𝔹'),
            (Equal(x, y),
             '(x : a) = (y : a) : 𝔹'),
            (Equal(Equal(x, y), x@bool),
             '(x : a) = (y : a) ↔ (x : 𝔹) : 𝔹'),
            (Equal(x@bool, Equal(x, y)),
             '(x : 𝔹) ↔ (x : a) = (y : a) : 𝔹'),
            (Not(Equal(x, y)),
             '(x : a) ≠ (y : a) : 𝔹'),
            (Not(Not(Equal(x, y))),
             '¬(x : a) ≠ (y : a) : 𝔹'),
            (Not(Not(Not(Equal(x, y)))),
             '¬¬(x : a) ≠ (y : a) : 𝔹'),
            (Equal(f(x), f(y)),
             '(f : a → a) (x : a) = (f : a → a) (y : a) : 𝔹'),
            (f(Equal(x, y)),
             '(f : 𝔹 → 𝔹) ((x : a) = (y : a)) : 𝔹'),
            (Equal(Equal(x@bool, y@bool), x@bool),
             '((x : 𝔹) ↔ (y : 𝔹)) ↔ (x : 𝔹) : 𝔹'),
            (Equal(f(x), f(y)),
             '(f : a → a) (x : a) = (f : a → a) (y : a) : 𝔹'),
            (Not(Not(Equal(x, Not(Equal(x, y))))),
             '¬¬((x : 𝔹) ↔ (x : a) ≠ (y : a)) : 𝔹'))

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        b = TypeVariable('𝛽')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Equal(x@b, y@b, i='𝛼𝛽'),
             r"(x : \U0001d6fd) = (y : \U0001d6fd) "
             + r"{i='\U0001d6fc\U0001d6fd'} : bool"),
            show_annotations=True, ensure_ascii=True)

    def test_show_annotations(self):
        a = TypeVariable('a')
        b = TypeVariable('𝛽')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Equal(x, y)@{'i': {'x': y}},
             '(x : a) = (y : a) : 𝔹'),
            show_annotations=False)

        self.assert_to_ulkb(
            (Equal(x, y)@{'i': {'x': y}},
             "(x : a) = (y : a) {i={'x': ⟨y : a⟩}} : 𝔹"),
            (Equal(x, y@{'k': 1})@{'i': {x: y}},
             "(x : a) = (y {k=1} : a) {i={⟨x : a⟩: ⟨y : a⟩}} : 𝔹"),
            (Not(Not(Equal(x, y, i=1))),
             "¬¬((x : a) = (y : a) {i=1}) : 𝔹"),
            (Not(Not(Equal(x, y), i=1)),
             "¬(¬(x : a) = (y : a) {i=1}) : 𝔹"),
            (Not(Not(Equal(x, y)), i=1),
             "¬(x : a) ≠ (y : a) {i=1} : 𝔹"),
            (And(f@bool, Equal(x, y, i=1)),
             "(f : 𝔹) ∧ ((x : a) = (y : a) {i=1}) : 𝔹"),
            show_annotations=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        b = TypeVariable('𝛽')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(bool, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Equal(x, y),
             'x = y : 𝔹'),
            (f(Equal(x@a, y@a)),
             'f (x = y) : a'),
            (Equal(x@a, f(Equal(x@a, y@a))),
             'x = (f (x = y)) : 𝔹'),
            (Not(Equal(x, y)),
             '¬(x = y) : 𝔹'),
            (Not(Not(Equal(x, y))),
             '¬¬(x = y) : 𝔹'),
            (Not(Not(Not(Equal(x, y)))),
             '¬¬¬(x = y) : 𝔹'),
            (Not(Not(Equal(x, Not(Equal(x, y))))),
             '¬¬(x ↔ (¬(x = y))) : 𝔹'),
            show_parentheses=True, omit_types=True)

        self.assert_to_ulkb(
            (Equal(x, f(Equal(x, y))),
             'x = f (x = y) : 𝔹'),
            show_parentheses=False, show_types=False)

        self.assert_to_ulkb(
            (Equal(x, f(Equal(x, y))),
             '(x : a) = ((f : 𝔹 → a) ((x : a) = (y : a))) : 𝔹'),
            show_parentheses=True)

    def test_show_types(self):
        a = TypeVariable('a')
        b = TypeVariable('𝛽')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', a)
        f = Constant('f', FunctionType(bool, a))
        g = Constant('g', FunctionType(a, a, a))
        self.assert_to_ulkb(
            (Equal(x, f(y@bool)),
             'x = f y : 𝔹'),
            (Equal(x, f(y@bool)),
             'x = f y : 𝔹'),
            show_types=False)

    def test_misc(self):
        a = TypeVariable('a')
        b = TypeVariable('b')
        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        x, y, z, w = Variables('x', 'y', 'z', 'w', a)
        t = Equal(Variable('x', a, hello={}), Constant(1, b))
        self.assert_to_ulkb(
            (t,
             '(x : b) = (1 : b) : 𝔹'),
            (Equal(x, f(x)),
             '(x : a) = (f : a → a) (x : a) : 𝔹'))

        self.assert_to_ulkb(
            (t,
             '(x {hello={}} : b) = (1 : b) : 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (Equal(x, f(x)),
             '(x : a) = ((f : a → a) (x : a)) : 𝔹'),
            omit_parentheses=False,)

        self.assert_to_ulkb(
            (t,
             '(x {hello={}} : b) = (1 : b) : bool'),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '(x {hello={}} : b) = (1 : b) : 𝔹'),
            omit_parentheses=True, show_annotations=True,)

        self.assert_to_ulkb(
            (t,
             '(x {hello={}}) = 1 : 𝔹'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '(x : b) = (1 : b) : 𝔹'),
            omit_annotations=True)

        self.assert_to_ulkb(
            (t,
             'x = 1 : 𝔹'),
            omit_types=True, omit_annotations=True)


if __name__ == '__main__':
    main()
