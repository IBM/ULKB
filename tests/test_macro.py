# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestMacro(ULKB_TestCase):

    def test_type_variables(self):
        self.assertEqual(tuple(TypeVariables('x')), (TypeVariable('x'),))
        x, y, z = TypeVariables('x', 'y', 'z', i=1, j=2)
        self.assert_type_variable(x, ('x',), {'i': 1, 'j': 2})
        self.assert_type_variable(y, ('y',), {'i': 1, 'j': 2})
        self.assert_type_variable(z, ('z',), {'i': 1, 'j': 2})

    def test_variables(self):
        self.assertRaises(TypeError, Variables, 'x')
        self.assertEqual(
            tuple(Variables('x', bool)), (Variable('x', bool),))
        x, y, z = Variables('x', 'y', 'z', bool, i=1, j=2)
        self.assert_variable(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_variable(y, ('y', BoolType()), {'i': 1, 'j': 2})
        self.assert_variable(z, ('z', BoolType()), {'i': 1, 'j': 2})

    def test_constants(self):
        self.assertRaises(TypeError, Constants, 'x')
        self.assertEqual(
            tuple(Constants('x', bool)), (Constant('x', bool),))
        x, y, z = Constants('x', 'y', 'z', bool, i=1, j=2)
        self.assert_constant(x, ('x', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(y, ('y', BoolType()), {'i': 1, 'j': 2})
        self.assert_constant(z, ('z', BoolType()), {'i': 1, 'j': 2})

    def test_base_types(self):
        self.assertEqual(tuple(BaseTypes('x')), (BaseType('x'),))
        x, y, z = BaseTypes('x', 'y', 'z', i=1, j=2)
        self.assert_base_type(x, (x[0],), {'i': 1, 'j': 2})
        self.assert_base_type(y, (y[0],), {'i': 1, 'j': 2})
        self.assert_base_type(z, (z[0],), {'i': 1, 'j': 2})

    def test_eq(self):
        a = TypeVariable('a')
        x, y, z = Variables('x', 'y', 'z', a)
        self.assert_deep_equal(eq(x, y, i=1, j=2), Equal(x, y, i=1, j=2))
        self.assert_deep_equal(
            eq(x, y, z, i=1, j=2),
            And(Equal(x, y), Equal(y, z), i=1, j=2))
        self.assertEqual(
            eq(x, y, z, x, y, z),
            And(
                Equal(x, y), Equal(y, z),
                Equal(z, x), Equal(x, y), Equal(y, z)))

    def test_ne(self):
        a = TypeVariable('a')
        x, y, z = Variables('x', 'y', 'z', a)
        self.assert_deep_equal(
            ne(x, y, i=1, j=2), Not(Equal(x, y), i=1, j=2))
        self.assert_deep_equal(
            ne(x, y, z, i=1, j=2),
            And(Not(Equal(x, y)), Not(Equal(y, z)), i=1, j=2))
        self.assertEqual(
            ne(x, y, z, x, y, z),
            And(
                Not(Equal(x, y)), Not(Equal(y, z)),
                Not(Equal(z, x)), Not(Equal(x, y)), Not(Equal(y, z))))


if __name__ == '__main__':
    main()
