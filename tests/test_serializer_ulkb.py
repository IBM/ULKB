# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestSerializerULKB(ULKB_TestCase):

    def assert_serialize_string(self, obj, text, format=None, **kwargs):
        self.assertEqual(obj.serialize(format=format, **kwargs), text)

    def assert_serialize(self, obj, text, format=None, **kwargs):
        import pathlib
        import tempfile
        self.assert_serialize_string(obj, text, format=format, **kwargs)
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / f'assert_serialize.{format}'
            obj.serialize(to=path, format=format, **kwargs)
            with open(path, 'r') as fp:
                self.assertEqual(fp.read(), text)
            with open(path, 'w') as fp:
                obj.serialize(to=fp, format=format, **kwargs)
            with open(path, 'r') as fp:
                self.assertEqual(fp.read(), text)

    def assert_to_ulkb(self, *args, **kwargs):
        if 'omit_types' not in kwargs and 'show_types' not in kwargs:
            kwargs['show_types'] = True
        for i, t in enumerate(args):
            assert isinstance(t, tuple) and len(t) == 2
            try:
                obj, text = t
                self.assertEqual(obj.to_ulkb(**kwargs), text)
                self.assert_serialize(obj, text, format='ulkb', **kwargs)
            except AssertionError as err:
                raise AssertionError(f'pair #{i+1}: {t}: {err}') from None


if __name__ == '__main__':
    main()
