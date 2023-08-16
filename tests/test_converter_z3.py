# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import z3

from ulkb import *

from .tests import ULKB_TestCase, main


class TestConverterZ3(ULKB_TestCase):

    def assert_z3_is_const(self, obj):
        self.assertTrue(z3.is_const(obj))

    def assert_z3_is_true(self, obj):
        self.assertTrue(z3.is_true(obj))

    def assert_z3_is_false(self, obj):
        self.assertTrue(z3.is_false(obj))

    def test_sanity(self):
        pass

    def test_convert_constant(self):
        b = Constant('b', bool)
        self.assert_z3_is_const(b.to_z3())
        self.assert_constant(Formula.from_z3(b.to_z3()), ('b', BoolType()))

        a = BaseType('a')
        k = Constant('k', a)
        self.assert_z3_is_const(k.to_z3())
        self.assert_constant(Constant.from_z3(k.to_z3()), ('k', a))

        x = Variable('x', bool)
        self.assert_z3_is_const(x.to_z3())
        self.assert_constant(Constant.from_z3(x.to_z3()), ('x', BoolType()))

    def test_convert_truth(self):
        self.assert_z3_is_true(Truth().to_z3())
        self.assert_truth(Constant.from_z3(z3.BoolVal(True)))

    def test_convert_falsity(self):
        self.assert_z3_is_false(Falsity().to_z3())
        self.assert_falsity(Constant.from_z3(z3.BoolVal(False)))


if __name__ == '__main__':
    main()
