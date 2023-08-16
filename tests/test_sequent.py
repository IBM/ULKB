# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *
from ulkb.sequent import _Sequent

from .tests import ULKB_TestCase, main


class TestSequent(ULKB_TestCase):

    def mk_sequent(self, *args, **kwargs):
        return _Sequent(*args, **kwargs)

    def test_sequent(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', bool)

        self.assertRaisesRegex(TypeError, 'abstract class', Sequent, x, x)
        self.assertRaises(TypeError, self.mk_sequent, {}, y@a)
        self.assertRaises(TypeError, self.mk_sequent, {x, y@a}, x)

        seq = self.mk_sequent({}, x, i=1, j=2)
        self.assert_sequent(seq, (frozenset(), x), {'i': 1, 'j': 2})

        seq = self.mk_sequent({x, x, y, x}, y, i=1, j=2)
        self.assert_sequent(seq, (frozenset({x, y}), y), {'i': 1, 'j': 2})


if __name__ == '__main__':
    main()
