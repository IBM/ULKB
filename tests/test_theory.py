# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *
from ulkb.converter import ConverterSettings
from ulkb.parser import ParserSettings
from ulkb.serializer import SerializerSettings

from .tests import ULKB_TestCase, main


class TestTheory(ULKB_TestCase):

    def test_prelude(self):
        with EmptyTheory() as thy:
            self.assertIsNone(thy.prelude)
        with Theory() as thy:
            self.assertEqual(type(thy.prelude).__name__, 'module')

    def test_prelude_offset(self):
        with EmptyTheory() as thy:
            self.assertEqual(thy.prelude_offset, 0)
        with Theory() as thy:
            self.assertEqual(thy.prelude_offset, len(thy))

    def test_args_no_prelude(self):
        with EmptyTheory() as thy:
            self.assertFalse(bool(thy.args_no_prelude))
        with Theory() as thy:
            self.assertFalse(bool(thy.args_no_prelude))
            thy.new_axiom(Truth())
            self.assertTrue(bool(thy.args_no_prelude))

    def test_settings(self):
        self.assertEqual(settings.converter, ConverterSettings())
        self.assertEqual(settings.parser, ParserSettings())
        self.assertEqual(settings.serializer, SerializerSettings())


if __name__ == '__main__':
    main()
