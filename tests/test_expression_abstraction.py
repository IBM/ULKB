# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestExpressionAbstraction(ULKB_TestCase):

    def test_equal(self):
        a, b, c = TypeVariables('a', 'b', 'c')
        x, x1 = Variables('x', 'x1', a)
        y, y1 = Variables('y', 'y1', b)
        z = Variable('z', c)
        self.assertEqual(
            Abstraction(x, x), Abstraction(x1, x1))
        self.assertNotEqual(
            Abstraction(x, x1), Abstraction(x1, x))
        self.assertEqual(
            Abstraction(x, y), Abstraction(x1, y))
        self.assertNotEqual(
            Abstraction(x, z), Abstraction(y, z))


if __name__ == '__main__':
    main()
