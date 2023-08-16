# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestConverterAST(ULKB_TestCase):

    def test_sanity(self):
        self.assertRaises(ValueError, BoolType().convert_to, format='x')
        self.assertRaises(ValueError, Constant.convert_from, {}, format='x')
        self.assertRaisesRegex(
            ConverterError, 'missing required field', Object.from_ast, {})
        self.assertRaisesRegex(
            ConverterError, 'invalid class', Object.from_ast,
            {'class': 'k'})
        self.assertRaisesRegex(
            ConverterError, 'missing required field', Object.from_ast,
            {'class': 'TypeConstructor'})
        self.assertRaisesRegex(
            ConverterError, 'TypeConstructor:', Object.from_ast,
            {'class': 'TypeApplication', 'args': (
                {'class': 'TypeConstructor',
                 'args': ('x',)},
            )})

    def test_type_constructor(self):
        t = TypeConstructor('t', 0, 'left', i=1, j=2)
        ast = t.to_ast()
        self.assertEqual(ast, {
            'class': 'TypeConstructor',
            'args': ('t', 0, 'left'),
            'i': 1,
            'j': 2
        })
        self.assert_deep_equal(t, t.from_ast(ast))

        s = TypeConstructor('s', 1, None, t=t)
        ast = s.to_ast()
        self.assertEqual(ast, {
            'class': 'TypeConstructor',
            'args': ('s', 1, None),
            't': t.to_ast()
        })
        self.assert_deep_equal(s, Object.from_ast(ast))

    def test_theory(self):
        ast = Theory.top.to_ast()
        self.assert_deep_equal(Theory.top, Theory.from_ast(ast))


if __name__ == '__main__':
    main()
