# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_NewTypeConstructor(TestSerializerULKB):

    def test_defaults(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        d = TypeConstructor('d', 2, 'left', i=1, j=2)
        e = TypeConstructor('e', 2, 'right', i=1, j=2)
        f = TypeConstructor('f', 2, i=1, j=2)
        self.assert_to_ulkb(
            (NewTypeConstructor(a),
             'type_constructor a 0'),
            (NewTypeConstructor(b),
             'type_constructor 𝛽 8'),
            (NewTypeConstructor(c),
             'type_constructor c 1'),
            (NewTypeConstructor(d),
             'type_constructor d 2 left'),
            (NewTypeConstructor(e),
             'type_constructor e 2 right'),
            (NewTypeConstructor(f),
             'type_constructor f 2'))

    def test_ensure_ascii(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (NewTypeConstructor(a),
             'type_constructor a 0'),
            (NewTypeConstructor(b),
             r'type_constructor \U0001d6fd 8'),
            (NewTypeConstructor(c),
             'type_constructor c 1'),
            ensure_ascii=True)

    def test_show_annotations(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        d = TypeConstructor('d', 2, 'left', i=1, j=2)
        self.assert_to_ulkb(
            (NewTypeConstructor(a, k=1, l=2),
             'type_constructor (a {i=1, j=2}) 0 {k=1, l=2}'),
            (NewTypeConstructor(b, k=1, l=2),
             'type_constructor (𝛽 {i=1, j=3}) 8 {k=1, l=2}'),
            (NewTypeConstructor(c, k=1, l=2),
             'type_constructor (c {i=1, j=2}) 1 {k=1, l=2}'),
            (NewTypeConstructor(d, k=1, l=2),
             'type_constructor (d {i=1, j=2}) 2 left {k=1, l=2}'),
            show_annotations=True)

    def test_show_parentheses(self):
        a = TypeConstructor('a', 0, i=1, j=2)
        b = TypeConstructor('𝛽', 8, i=1, j=3)
        c = TypeConstructor('c', 1, i=1, j=2)
        self.assert_to_ulkb(
            (NewTypeConstructor(a),
             'type_constructor a 0'),
            (NewTypeConstructor(b),
             'type_constructor 𝛽 8'),
            (NewTypeConstructor(c),
             'type_constructor c 1'),
            show_parentheses=True, show_types=True)


if __name__ == '__main__':
    main()
