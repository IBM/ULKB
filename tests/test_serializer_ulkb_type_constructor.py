# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_TypeConstructor(TestSerializerULKB):

    def test_defaults(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (a,
             'a'),
            (b,
             '𝛽'),
            (c,
             'c'))

    def test_ensure_ascii(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (a,
             'a'),
            (b,
             r'\U0001d6fd'),
            (c,
             'c'),
            (c(c(a())),
             'c (c a) : *'),
            ensure_ascii=True)

    def test_show_annotations(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (a,
             'a {i=1, j=2}'),
            (b,
             '𝛽 {i=1, j=3}'),
            (c,
             'c {i=1, j=2}'),
            (c(c(a(k=1))), '\
(c {i=1, j=2}) ((c {i=1, j=2}) ((a {i=1, j=2}) {k=1})) : *'),
            (c(c(a(k=1), l=2)), '\
(c {i=1, j=2}) ((c {i=1, j=2}) ((a {i=1, j=2}) {k=1}) {l=2}) : *'),
            show_annotations=True)

    def test_show_parentheses(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (a,
             'a'),
            (b,
             '𝛽'),
            (c,
             'c'),
            (c(c(a(k=1))),
             'c (c a) : *'),
            (c(c(a(k=1), l=2)),
             'c (c a) : *'),
            show_parentheses=True, show_types=True)


if __name__ == '__main__':
    main()
