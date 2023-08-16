# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb.object import Object

from .tests import ULKB_TestCase, main


class A(Object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class B(A):
    pass


class C(Object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestObject(ULKB_TestCase):

    def test__init__(self):
        self.assertRaisesRegex(TypeError, 'bad argument', A, None)

        a = A()
        self.assert_object(a, (), {})

        a = A(1, 2, 3, a=1, b=2, c=3)
        self.assert_object(a, (1, 2, 3), {'a': 1, 'b': 2, 'c': 3})

    def test_compare(self):
        a1, a2 = A('a1'), A('a2')
        self.assertEqual(a1.compare(a2), -1)
        self.assertTrue(a1 < a2)
        self.assertFalse(a1 > a2)
        self.assertFalse(a1 == a2)
        self.assertEqual(a2.compare(a1), 1)
        self.assertTrue(a2 > a1)
        self.assertFalse(a2 < a1)
        self.assertFalse(a2 == a1)
        self.assertEqual(a1.compare(a1), 0)
        self.assertFalse(a1 < a1)
        self.assertFalse(a2 < a2)
        self.assertTrue(a1 == a1)
        b = B('b', a1)
        self.assertTrue(a1 < b)
        self.assertTrue(a2 < b)

    def test_equal(self):
        self.assertTrue(A(1, 2, 3).equal(A(1, 2, 3)))
        self.assertFalse(A(1, 2, 3).equal(A(1, 2)))
        self.assertFalse(A(1, 2, 3).equal(B(1, 2, 3)))
        self.assertFalse(A(1, 2, 3).equal(C(1, 2, 3)))

        a1 = A(1, 2, 3, x='x')
        a2 = A(1, 2, 3, x='y')
        self.assertTrue(a1.equal(a2))
        self.assertFalse(a1.equal(a2, deep=True))

        # nested objects
        a1 = A(1, 2, B(1, 2, x='x'))
        a2 = A(1, 2, B(1, 2, x='y'))
        self.assertTrue(a1.equal(a2))
        self.assertFalse(a1.equal(a2, deep=True))
        self.assertTrue(a1.equal(A(1, 2, B(1, 2, x='x')), deep=True))

    def test_deepequal(self):
        a1 = A(1, 2, B(1, 2, x='x'))
        a2 = A(1, 2, B(1, 2, x='y'))
        self.assertFalse(a1.deepequal(a2))
        self.assertTrue(a1.deepequal(A(1, 2, B(1, 2, x='x'))))

    def test_copy(self):
        a1 = A(1, 2, B(), x='x', y='y')
        a2 = a1.copy()
        self.assertTrue(a1, a2)
        self.assertIsNot(a1, a2)
        self.assertIs(a1.args, a2.args)
        self.assertIs(a1.annotations, a2.annotations)

        a3 = a1.copy(1, 2, B())
        self.assertEqual(a1, a3)
        self.assertIsNot(a1, a3)
        self.assertIsNot(a1.args, a3.args)
        self.assertIsNot(a1.annotations, a3.annotations)

    def test_with_args(self):
        a = A(1, 2, B(), x='x', y='y')
        self.assert_deep_equal(a.with_args(1), A(1, x='x', y='y'))

    def test_with_annotations(self):
        a = A(1, 2, B(), x='x', y='y')
        self.assert_deep_equal(
            a.with_annotations(z='z'), A(1, 2, B(), z='z'))

    def test_deepcopy(self):
        t = {}
        a = A(1, 2, B(t))
        a1 = a.copy(1, 2, B(t))
        a2 = a.deepcopy()
        self.assert_deep_equal(a, a1)
        self.assert_deep_equal(a, a2)
        self.assertIsNot(a[2], a1[2])
        self.assertIsNot(a[2], a2[2])
        self.assertIs(a[2][0], a1[2][0])
        self.assertIsNot(a[2][0], a2[2][0])

    def test_hexdigest(self):
        a = A(1, 2, B(), x='x')
        b = A(1, 2, B(), y='y')
        self.assertEqual(a.hexdigest, b.hexdigest)

    def test_dump(self):
        a = A(1, 2, B(), x='x', y='y')
        self.assertEqual(a.dump(), '(A 1 2 B)')

    def test_convert_from(self):
        a = {
            'class': 'A',
            'args': (1, 2, {'class': 'B', 'args': ()}),
            'x': 'x',
            'y': 'y',
        }
        self.assert_deep_equal(
            A.convert_from(a, format='ast'), A(1, 2, B(), x='x', y='y'))

    def test_convert_to(self):
        a = A(1, 2, B(), x='x', y='y')
        self.assertDictEqual(
            a.convert_to(format='ast'),
            {'class': 'A',
             'args': (1, 2, {'class': 'B', 'args': ()}),
             'x': 'x',
             'y': 'y'})

    def test_parse(self):
        import json
        a = {
            'class': 'A',
            'args': (1, 2, {'class': 'B', 'args': ()}),
            'x': 'x',
            'y': 'y',
        }
        self.assert_deep_equal(
            A.parse(json.dumps(a), format='json'),
            A(1, 2, B(), x='x', y='y'))

    def test_serialize(self):
        import json
        a = A(1, 2, B(), x='x', y='y')
        self.assertEqual(
            a.serialize(format='json', indent=None, separators=None),
            json.dumps({
                'class': 'A',
                'args': (1, 2, {'class': 'B', 'args': ()}),
                'x': 'x',
                'y': 'y',
            }))

    def test_test(self):
        a = A(1, 2, 3, a=1, b=2, c=3)
        self.assertTrue(Object.test(a))
        self.assertTrue(a.test_object())
        self.assertTrue(A.test(a))
        self.assertTrue(a.test_a())
        self.assertFalse(B.test(a))
        self.assertFalse(a.test_b())
        self.assertFalse(C.test(a))
        self.assertFalse(a.test_c())

        b = B('b')
        self.assertTrue(Object.test(b))
        self.assertTrue(b.is_object())
        self.assertTrue(A.test(b))
        self.assertTrue(b.is_a())
        self.assertTrue(B.test(b))
        self.assertTrue(b.is_b())
        self.assertFalse(C.test(b))
        self.assertFalse(b.is_c())

    def test_test_object(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertTrue(a.test_object())
        self.assertFalse(a.test_b())
        self.assertTrue(b.test_object())
        self.assertTrue(b.test_a())

    def test_check(self):
        a = A(1, 2, 3, a=1, b=2, c=3)
        self.assertEqual(Object.check(a), a)
        self.assertEqual(A.check(a), a)
        self.assertEqual(a.check(a), a)
        self.assertRaisesRegex(TypeError, 'bad argument', B.check, a)
        self.assertRaisesRegex(TypeError, 'bad argument', C.check, a)

        b = B('b')
        self.assertEqual(Object.check(a), a)
        self.assertEqual(A.check(b), b)
        self.assertEqual(a.check(b), b)
        self.assertEqual(B.check(b), b)
        self.assertEqual(b.check(b), b)
        self.assertRaisesRegex(TypeError, 'bad argument', C.check, b)

    def test_check_object(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertEqual(a.check_object(), a)
        self.assertRaisesRegex(TypeError, 'bad argument', a.check_b)
        self.assertEqual(b.check_object(), b)
        self.assertEqual(b.check_a(), b)

    def test_unfold(self):
        a, b, c = A(1, 2, 3), B(), C('x', 'y', 'z')
        self.assertEqual(A.unfold(a), (1, 2, 3))
        self.assertEqual(a.unfold(a), (1, 2, 3))
        self.assertRaisesRegex(TypeError, 'bad argument', B.unfold, a)
        self.assertEqual(a.unfold(b), ())
        self.assertEqual(C.unfold(c), ('x', 'y', 'z'))

    def test_unfold_object(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertEqual(a.unfold_object(), (1, 2, 3))
        self.assertEqual(a.unfold_a(), (1, 2, 3))
        self.assertRaisesRegex(TypeError, 'bad argument', a.unfold_b)
        self.assertEqual(b.unfold_object(), ('b',))
        self.assertEqual(b.unfold_a(), ('b',))
        self.assertEqual(b.unfold_b(), ('b',))

    def test_unfold_unsafe(self):
        a, b, c = A(1, 2, 3), B(), C('x', 'y', 'z')
        self.assertEqual(A.unfold_unsafe(a), (1, 2, 3))
        self.assertEqual(a.unfold_unsafe(a), (1, 2, 3))
        self.assertIsNone(B.unfold_unsafe(a))
        self.assertEqual(a.unfold_unsafe(b), ())
        self.assertEqual(C.unfold_unsafe(c), ('x', 'y', 'z'))

    def test_unfold_object_unsafe(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertEqual(a.unfold_object_unsafe(), (1, 2, 3))
        self.assertEqual(a.unfold_a_unsafe(), (1, 2, 3))
        self.assertIsNone(a.unfold_b_unsafe())
        self.assertEqual(b.unfold_object_unsafe(), ('b',))
        self.assertEqual(b.unfold_a_unsafe(), ('b',))

    def test_unpack(self):
        a, b, c = A(1, 2, 3), B(), C('x', 'y', 'z')
        self.assertEqual(A.unpack(a), (1, 2, 3))
        self.assertEqual(a.unpack(a), (1, 2, 3))
        self.assertRaisesRegex(TypeError, 'bad argument', B.unpack, a)
        self.assertEqual(a.unpack(b), ())
        self.assertEqual(C.unpack(c), ('x', 'y', 'z'))

    def test_unpack_object(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertEqual(a.unpack_object(), (1, 2, 3))
        self.assertEqual(a.unpack_a(), (1, 2, 3))
        self.assertRaisesRegex(TypeError, 'bad argument', a.unpack_b)
        self.assertEqual(b.unpack_object(), ('b',))
        self.assertEqual(b.unpack_a(), ('b',))
        self.assertEqual(b.unpack_b(), ('b',))

    def test_unpack_unsafe(self):
        a, b, c = A(1, 2, 3), B(), C('x', 'y', 'z')
        self.assertEqual(A.unpack_unsafe(a), (1, 2, 3))
        self.assertEqual(a.unpack_unsafe(a), (1, 2, 3))
        self.assertIsNone(B.unpack_unsafe(a))
        self.assertEqual(a.unpack_unsafe(b), ())
        self.assertEqual(C.unpack_unsafe(c), ('x', 'y', 'z'))

    def test_unpack_object_unsafe(self):
        a, b = A(1, 2, 3, a=1, b=2, c=3), B('b')
        self.assertEqual(a.unpack_object_unsafe(), (1, 2, 3))
        self.assertEqual(a.unpack_a_unsafe(), (1, 2, 3))
        self.assertIsNone(a.unpack_b_unsafe())
        self.assertEqual(b.unpack_object_unsafe(), ('b',))
        self.assertEqual(b.unpack_a_unsafe(), ('b',))


if __name__ == '__main__':
    main()
