# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestTypeConstructor(ULKB_TestCase):

    def test_type_constructor(self):
        self.assertRaises(TypeError, TypeConstructor, None)
        self.assertRaises(TypeError, TypeConstructor, 'x')
        self.assertRaises(TypeError, TypeConstructor, 'x', 'x')
        self.assertRaises(ValueError, TypeConstructor, 'x', 0, 'x')

        c0 = TypeConstructor('c0', 0, 'left', i=1, j=2)
        self.assert_type_constructor(
            c0, ('c0', 0, 'left'), {'i': 1, 'j': 2})
        self.assertNotEqual(c0, TypeConstructor('c0', 1))
        self.assert_deep_equal(
            TypeApplication(c0, i=1, j=2), c0(i=1, j=2))
        self.assert_equal_but_not_deep_equal(
            TypeApplication(c0, i=1, j=2), c0())

        c1 = TypeConstructor('c1', 1, None, i=1, j=2)
        self.assert_type_constructor(
            c1, ('c1', 1, None), {'i': 1, 'j': 2})
        self.assertNotEqual(c1, TypeConstructor('c1', 0))
        self.assertNotEqual(c1, TypeConstructor('c0', 1))
        self.assert_deep_equal(
            TypeApplication(c1, c0(), i=1, j=2), c1(c0(), i=1, j=2))
        self.assert_equal_but_not_deep_equal(
            TypeApplication(c1, c0(), i=1, j=2), c1(c0(), ))

        a, b, c = BaseTypes('a', 'b', 'c', i=1, j=2)
        self.assert_type_application(
            a,
            (TypeConstructor('a', 0),),
            (TypeConstructor('a', 0),),
            {'i': 1, 'j': 2})
        self.assert_type_application(
            b,
            (TypeConstructor('b', 0),),
            (TypeConstructor('b', 0),),
            {'i': 1, 'j': 2})
        self.assert_type_application(
            c,
            (TypeConstructor('c', 0),),
            (TypeConstructor('c', 0),),
            {'i': 1, 'j': 2})
        c2 = TypeConstructor('c2', 2, 'left', i=1, j=2)
        self.assert_type_constructor(
            c2, ('c2', 2, 'left'), {'i': 1, 'j': 2})
        self.assert_deep_equal(
            TypeApplication(
                c2, TypeApplication(c2, a, b), c, i=1, j=2),
            c2(a, b, c, i=1, j=2))

        c3 = TypeConstructor('c3', 2, 'right', i=1, j=2)
        self.assert_type_constructor(
            c3, ('c3', 2, 'right'), {'i': 1, 'j': 2})

        self.assert_deep_equal(
            TypeApplication(
                c3, a, TypeApplication(c3, b, c), i=1, j=2),
            c3(a, b, c, i=1, j=2))

        c4 = TypeConstructor('c4', 2, i=1, j=2)
        self.assert_type_constructor(
            c4, ('c4', 2, None), {'i': 1, 'j': 2})
        self.assertRaises(ValueError, c4, a, b, c)
        self.assert_type_application(
            c4(a, b, i=1, j=2),
            (c4, a, b),
            (c4, a, b),
            {'i': 1, 'j': 2})

        c5 = TypeConstructor('c5', 8, i=1, j=2)
        self.assert_type_constructor(
            c5, ('c5', 8, None), {'i': 1, 'j': 2})
        self.assertRaises(ValueError, c5, a, b, c)
        self.assert_type_application(
            c5(a, b, c, a, b, c, a, b, i=1, j=2),
            (c5, a, b, c, a, b, c, a, b),
            (c5, a, b, c, a, b, c, a, b),
            {'i': 1, 'j': 2})

        c6 = TypeConstructor('c6', 2, 'left', i=1, j=2)
        self.assert_type_constructor(
            c6, ('c6', 2, 'left'), {'i': 1, 'j': 2})
        self.assertRaises(ValueError, c6, a)
        self.assert_type_application(
            c6(a, b, c, b, i=1, j=2),
            (c6, c6(c6(a, b), c), b),
            (c6, a, b, c, b),
            {'i': 1, 'j': 2})

        c7 = TypeConstructor('c7', 2, 'right', i=1, j=2)
        self.assert_type_constructor(
            c7, ('c7', 2, 'right'), {'i': 1, 'j': 2})
        self.assertRaises(ValueError, c7, a)
        self.assert_type_application(
            c7(a, b, c, b, i=1, j=2),
            (c7, a, c7(b, c7(c, b))),
            (c7, a, b, c, b),
            {'i': 1, 'j': 2})


if __name__ == '__main__':
    main()
