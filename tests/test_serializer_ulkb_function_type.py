# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_FunctionType(TestSerializerULKB):

    def test_defaults(self):
        x, y = BaseTypes('x', 'y')
        self.assert_to_ulkb(
            (FunctionType(x, y),
             'x → y : *'),
            (FunctionType(x, y, x),
             'x → y → x : *'),
            (FunctionType(FunctionType(x, y), x),
             '(x → y) → x : *'),
            (FunctionType(x, FunctionType(x, y), x),
             'x → (x → y) → x : *'))

    def test_ensure_ascii(self):
        x, y = BaseTypes('x', 'y')
        self.assert_to_ulkb(
            (FunctionType(x, y),
             'x -> y : *'),
            (FunctionType(BaseType('𝛼'), y),
             '\\U0001d6fc -> y : *'),
            ensure_ascii=True)

    def test_show_annotations(self):
        x, y = BaseTypes('x', 'y')
        x = FunctionType(x, y@{'k': 8}, abc='def', i=-33)
        self.assert_to_ulkb(
            (x,
             'x → y : *'))

        self.assert_to_ulkb(
            (x,
             "x → (y {k=8}) {abc='def', i=-33} : *"),
            (x@{'i': x}, "\
x → (y {k=8}) {i=⟨x → (y {k=8}) {abc='def', i=-33} : *⟩} : *"),
            show_annotations=True)

    def test_show_parentheses(self):
        x, y = BaseTypes('x', 'y')
        self.assert_to_ulkb(
            (FunctionType(x, y),
             'x → y : *'),
            (FunctionType(x, y, x),
             'x → (y → x) : *'),
            (FunctionType(x, y, x, y),
             'x → (y → (x → y)) : *'),
            (FunctionType(x, FunctionType(x, y), x),
             'x → ((x → y) → x) : *'),
            show_parentheses=True)

    def test_show_types(self):
        x, y = BaseTypes('x', 'y')
        self.assert_to_ulkb(
            (x >> y,
             'x → y : *'),
            show_types=True)

        self.assert_to_ulkb(
            (x >> y,
             'x → y : *'),
            show_types=False)

    def test_misc(self):
        a, b = TypeVariables('a', 'b')
        self.assert_to_ulkb(
            (FunctionType(a, b),
             'a → b : *'),
            (FunctionType(a, b, a),
             'a → b → a : *'),
            (FunctionType(FunctionType(a, b), a),
             '(a → b) → a : *'))

        x, y, z = BaseTypes('x', 'y', 'z')
        self.assert_to_ulkb(
            (FunctionType(x, y, z),
             'x → y → z : *'),
            (FunctionType(x, FunctionType(y, y), z),
             'x → (y → y) → z : *'),)

        self.assert_to_ulkb(
            (FunctionType(x, y, z, x),
             'x → (y → (z → x)) : *'),
            omit_parentheses=False)

        self.assert_to_ulkb(
            (FunctionType(FunctionType(x, y), x, x),
             '(x -> y) -> x -> x : *'),
            ensure_ascii=True)


if __name__ == '__main__':
    main()
