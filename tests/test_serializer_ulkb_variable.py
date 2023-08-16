# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Variable(TestSerializerULKB):

    def test_defaults(self):
        x = Variable('x', bool)
        self.assert_to_ulkb(
            (false,
             '⊥ : 𝔹'),
            (x@bool,
             'x : 𝔹'),
            (x@BaseType('int'),
             'x : ℤ'),
            (x@TypeVariable('t'),
             'x : t'),
            (Variable('x', type=TypeVariable('t')),
             'x : t'))

    def test_ensure_ascii(self):
        x = Variable('x', bool)
        self.assert_to_ulkb(
            (Variable('𝜄', FunctionType(bool, bool))(true),
             '(\\U0001d704 : bool -> bool) (true : bool) : bool'),
            ensure_ascii=True)

    def test_show_annotations(self):
        x = Variable('x', bool, i=[1, (2, ('3', {4}))])
        self.assert_to_ulkb(
            (x,
             'x : 𝔹'),
            (x@{'i': {'a': 1.}},
             'x : 𝔹'))
        self.assert_to_ulkb(

            (x,
             "x {i=[1, (2, ('3', {4}))]} : 𝔹"),
            (x@{'i': {'a': 1.}},
             "x {i={'a': 1.0}} : 𝔹"),
            show_annotations=True)

    def test_show_parentheses(self):
        x = Variable('x', bool)
        self.assert_to_ulkb(
            (x,
             'x : 𝔹'),
            (x@BaseType('int'),
             'x : ℤ'),
            show_parentheses=True)

    def test_show_types(self):
        x = Variable('x', bool)
        self.assert_to_ulkb(
            (x@bool,
             'x : 𝔹'),
            show_types=False)

        self.assert_to_ulkb(
            (x@bool,
             'x : 𝔹'),
            show_types=True)

    def test_misc(self):
        nat = BaseType('nat')
        x = Variable('x', type=nat >> nat, k8=8)
        self.assert_to_ulkb(
            (x,
             'x : nat → nat'))

        self.assert_to_ulkb(
            (x,
             'x {k8=8} : nat → nat'),
            show_annotations=True)

        self.assert_to_ulkb(
            (x,
             'x {k8=8} : nat -> nat'),
            show_annotations=True, ensure_ascii=True)

        self.assert_to_ulkb(
            (x,
             'x {k8=8} : nat → nat'),
            omit_annotations=False, omit_parentheses=False)

        self.assert_to_ulkb(
            (x,
             'x {k8=8} : nat → nat'),
            omit_types=True, show_annotations=True)

        self.assert_to_ulkb(
            (x,
             'x : nat → nat'),
            omit_annotations=True)

        self.assert_to_ulkb(
            (x,
             'x : nat → nat'),
            omit_types=True, omit_annotations=True)


if __name__ == '__main__':
    main()
