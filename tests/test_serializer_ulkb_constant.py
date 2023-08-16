# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Constant(TestSerializerULKB):

    def test_defaults(self):
        x = Constant('x', bool)
        self.assert_to_ulkb(
            (x,
             'x : 𝔹'),
            (x@bool,
             'x : 𝔹'),
            (x@BaseType('int'),
             'x : ℤ'),
            (x@TypeVariable('t'),
             'x : t'),
            (Constant('x', TypeVariable('t')),
             'x : t'),
            (Constant(True, type=bool),
             'True : 𝔹'),
            (Constant(1, BaseType('int')),
             '1 : ℤ'))

    def test_ensure_ascii(self):
        x = Constant('x', bool)
        self.assert_to_ulkb(
            (Constant('𝜉', bool),
             '\\U0001d709 : bool'),
            ensure_ascii=True)

    def test_show_annotations(self):
        x = Constant('x', bool, i=1, j=(-1, 1))
        self.assert_to_ulkb(
            (x,
             'x : 𝔹'),
            (x@{'obj': x},
             'x : 𝔹'),
            show_annotations=False)

        self.assert_to_ulkb(
            (x,
             'x {i=1, j=(-1, 1)} : 𝔹'),
            (x@{'obj': x},
             'x {obj=⟨x {i=1, j=(-1, 1)} : 𝔹⟩} : 𝔹'),
            (x@{'i': x@{'i': x}},
             'x {i=⟨x {i=⟨x {i=1, j=(-1, 1)} : 𝔹⟩} : 𝔹⟩} : 𝔹'),
            show_annotations=True)

    def test_show_parentheses(self):
        x = Constant('x', bool)
        self.assert_to_ulkb(
            (x,
             'x : 𝔹'),
            (x@TypeVariable('int'),
             'x : int'),
            show_parentheses=True)

    def test_show_types(self):
        x = Constant('x', TypeVariable('a'))
        self.assert_to_ulkb(
            (x@bool,
             'x : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (x@bool,
             'x : 𝔹'),
            show_types=True)

    def test_misc(self):
        n = Constant(1, type=BaseType('nat'), k1=1, k2=2)
        self.assert_to_ulkb(
            (n,
             '1 : nat'))

        self.assert_to_ulkb(
            (n,
             '1 {k1=1, k2=2} : nat'),
            show_annotations=True)

        self.assert_to_ulkb(
            (n,
             '1 {k1=1, k2=2} : nat'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (n,
             '1 : nat'),
            omit_annotations=True)

        self.assert_to_ulkb(
            (n,
             '1 : nat'),
            omit_types=True, omit_annotations=True)

        self.assert_to_ulkb(
            (Constant(1, TypeVariable('𝛼')),
             '1 : 𝛼'),
            (Constant(1, BaseType('int')),
             '1 : ℤ'))


if __name__ == '__main__':
    main()
