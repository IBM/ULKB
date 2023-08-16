# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_BaseType(TestSerializerULKB):

    def test_defaults(self):
        a, b, c = BaseTypes('a', 'b', 'c')
        self.assert_to_ulkb(
            (a,
             'a : *'),
            (b,
             'b : *'),
            (c,
             'c : *'))

    def test_ensure_ascii(self):
        a, b, c = BaseTypes('a', 'b', 'c')
        self.assert_to_ulkb(
            (BaseType('𝛽𝜖𝜏𝛼'),
             '\\U0001d6fd\\U0001d716\\U0001d70f\\U0001d6fc : *'),
            ensure_ascii=True)

    def test_show_annotations(self):
        x = BaseType('x', abc='def', i=-33)
        y = BaseType('y')
        self.assert_to_ulkb(
            (x,
             'x : *'))
        self.assert_to_ulkb(
            (x,
             "x {abc='def', i=-33} : *"),
            (x@{'i': x},
             "x {i=⟨x {abc='def', i=-33} : *⟩} : *"),
            (y@{'i': y@{'j': y@{'k': y}}},
             'y {i=⟨y {j=⟨y {k=⟨y : *⟩} : *⟩} : *⟩} : *'),
            show_annotations=True)

        self.assert_to_ulkb(
            (x,
             "x {abc='def', i=-33} : *"),
            (x@{'i': x},
             "x {i=<x {abc='def', i=-33} : *>} : *"),
            (y@{'i': y@{'j': y@{'k': y}}},
             'y {i=<y {j=<y {k=<y : *>} : *>} : *>} : *'),
            show_annotations=True, ensure_ascii=True)

    def test_show_parentheses(self):
        x = BaseType('x')
        self.assert_to_ulkb(
            (x,
             'x : *'),
            show_parentheses=True)

    def test_show_types(self):
        x = BaseType('x')
        self.assert_to_ulkb(
            (x,
             'x : *'),
            show_types=True)

        self.assert_to_ulkb(
            (x,
             'x : *'),
            show_types=False)


if __name__ == '__main__':
    main()
