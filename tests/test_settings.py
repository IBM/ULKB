# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb.settings import Settings

from .tests import ULKB_TestCase, main


class B(Settings):
    y = 'abc'
    z = None


class A(Settings):
    x = 1
    b = B
    _c = 33

    @property
    def dx(self):
        return self.x * 2

    @dx.setter
    def dx(self, v):
        self.x = v // 2

    @dx.deleter
    def dx(self):
        del self.x


class TestSettings(ULKB_TestCase):

    def test__init__(self):
        self.assertRaisesRegex(AttributeError, 'has no attribute', A, a=1)
        self.assertRaisesRegex(AttributeError, 'has no attribute', B, a=1)

        a = A()
        self.assertEqual(a.x, 1)
        self.assertEqual(a.dx, 2)
        self.assertEqual(a.b, B(y='abc', z=None))
        self.assertEqual(len(a), 3)
        self.assertDictEqual(
            dict(a.recursive_items()),
            {'x': 1, 'dx': 2, 'b.y': 'abc', 'b.z': None})

        # overwrite class default
        a = A(x=8)
        self.assertEqual(a.x, 8)
        self.assertEqual(a.dx, 16)
        self.assertEqual(a.b, B(y='abc', z=None))
        self.assertDictEqual(
            dict(a.recursive_items()),
            {'x': 8, 'dx': 16, 'b.y': 'abc', 'b.z': None})

        a = A(x=8, b=B(z=123))
        self.assertEqual(a.x, 8)
        self.assertEqual(a.dx, 16)
        self.assertEqual(a.b, B(z=123))
        self.assertDictEqual(
            dict(a.recursive_items()),
            {'x': 8, 'dx': 16, 'b.y': 'abc', 'b.z': 123})

        # re-install nested settings
        a1, a2 = A(), A(x=33)
        self.assertEqual(a1.x, 1)
        self.assertEqual(a2.x, 33)
        self.assertEqual(a1.b, a2.b)
        self.assertIsNot(a1.b, a2.b)

    def test__getattr__(self):
        a = A()
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', getattr, a, 'a')
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', a.__getitem__, 'a')

    def test__setattr__(self):
        a = A()
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', setattr, a, 'a', 1)
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', a.__setitem__, 'a', 1)
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', setattr, a.b, 'a', 1)

        a.x = 8
        self.assertEqual(a.x, 8)
        self.assertEqual(a.dx, 16)

        a.dx = 4
        self.assertEqual(a.x, 2)
        self.assertEqual(a.dx, 4)

        # nested settings
        a.b.y = 'xyz'
        self.assertEqual(a.b.y, 'xyz')

        # bulk set
        a = A()
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', setattr, a, 'b', {'a': 1})

        a.b = {'y': 'xyz', 'z': False}
        self.assertEqual(a.x, 1)
        self.assertEqual(a.dx, 2)
        self.assertEqual(a.b.y, 'xyz')
        self.assertEqual(a.b.z, False)

    def test__delattr__(self):
        a = A()
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', delattr, a, 'a')
        self.assertRaisesRegex(
            AttributeError, 'has no attribute', a.__delitem__, 'a')

        a.x = 8
        self.assertEqual(a.x, 8)
        self.assertEqual(a.dx, 16)
        del a.x
        self.assertEqual(a.x, 1)
        self.assertEqual(a.dx, 2)

        # nested settings
        a.b = B(z=True)
        self.assertEqual(a.b.y, 'abc')
        self.assertEqual(a.b.z, True)
        del a.b
        self.assertEqual(a.b.y, 'abc')
        self.assertEqual(a.b.z, None)

    def test__call__(self):
        a = A()
        a1 = a()
        self.assertEqual(a, a1)
        self.assertIsNot(a, a1)

        a2 = a(dx=8)
        self.assertNotEqual(a, a2)
        self.assertIsNot(a, a2)
        self.assertEqual(a2.x, 4)

    def test_copy(self):
        a = A()
        a.dx = 33
        a1 = a.copy()
        self.assertEqual(a, a1)
        self.assertIs(a.b, a1.b)

    def test_deepcopy(self):
        a = A()
        a.dx = 33
        a1 = a.deepcopy()
        self.assertEqual(a, a1)
        self.assertIsNot(a.b, a1.b)


if __name__ == '__main__':
    main()
