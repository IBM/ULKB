# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestExtension(ULKB_TestCase):

    def test_new_type_constructor(self):
        self.assertRaises(TypeError, NewTypeConstructor, None)
        self.assertRaises(TypeError, NewTypeConstructor, BoolType())

        ext = NewTypeConstructor(TypeConstructor('t', 0), i=1, j=2)
        self.assert_new_type_constructor(
            ext, (TypeConstructor('t', 0),), {'i': 1, 'j': 2})

        ext = NewTypeConstructor(TypeConstructor('k', 8, i=1), j=2)
        self.assert_new_type_constructor(
            ext, (TypeConstructor('k', 8, i=1),), {'j': 2})

    def test_new_constant(self):
        self.assertRaises(TypeError, NewConstant, None)
        self.assertRaises(TypeError, NewConstant, BoolType())

        ext = NewConstant(Constant('c', bool), i=1, j=2)
        self.assert_new_constant(
            ext, (Constant('c', bool),), {'i': 1, 'j': 2})

        ext = NewConstant(Constant('k', FunctionType(bool, bool), i=1), j=2)
        self.assert_new_constant(
            ext, (Constant('k', FunctionType(bool, bool), i=1),), {'j': 2})

    def test_new_axiom(self):
        self.assertRaises(TypeError, NewAxiom, None)
        self.assertRaises(TypeError, NewAxiom, BoolType())
        self.assertRaises(TypeError, NewAxiom, Constant('x', bool))

        a, b, c = TypeVariables('a', 'b', 'c')
        f = Constant('f', FunctionType(bool, bool))
        k = Constant('k', bool)
        x = Constant('x', bool)

        self.assertRaises(TypeError, NewAxiom, f(k))

        ext = NewAxiom(x, f(k), i=1, j=2)
        self.assert_new_axiom(
            ext, (x, ext[1]), {'i': 1, 'j': 2})

    def test_new_definition(self):
        self.assertRaises(TypeError, NewDefinition, None)
        self.assertRaises(TypeError, NewDefinition, BoolType())
        self.assertRaises(TypeError, NewDefinition, Constant('x', bool))

        a, b, c = TypeVariables('a', 'b', 'c')
        f = Constant('f', FunctionType(bool, bool))
        k = Constant('k', bool)
        x = Variable('x', bool)

        self.assertRaises(TypeError, NewDefinition, f(k))
        self.assertRaisesRegex(
            ValueError, '(not a definitional equation)',
            NewDefinition, Equal(f, k@FunctionType(bool, bool)))
        self.assertRaisesRegex(
            ValueError, '(definiens is not closed)',
            NewDefinition, Equal(x, x))
        self.assertRaisesRegex(
            ValueError, '(extra type variable in definiens)',
            NewDefinition, Equal(x@a, (f@FunctionType(a, b))(k@a)))

        ext = NewDefinition(Equal(x, f(k)), i=1, j=2)
        self.assert_new_definition(
            ext, (Equal(x, f(k)),), {'i': 1, 'j': 2})

    def test_new_python_type_alias(self):
        self.assertRaises(TypeError, NewPythonTypeAlias, None)
        self.assertRaises(TypeError, NewPythonTypeAlias, BoolType())
        self.assertRaises(
            TypeError, NewPythonTypeAlias, int, Constant('x', bool))
        self.assertRaises(
            TypeError, NewPythonTypeAlias, Constant('x', bool), BoolType())

        ext = NewPythonTypeAlias(int, BoolType(), i=1, j=2)
        self.assert_new_python_type_alias(
            ext, (int, BoolType(), None), {'i': 1, 'j': 2})


if __name__ == '__main__':
    main()
