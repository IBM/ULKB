# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestParserJSON(ULKB_TestCase):

    def test_theory(self):
        top = Theory.top
        with Theory() as th1:
            self.assertEqual(th1, top)
            th2 = Theory.from_json(th1.to_json())
            self.assertEqual(th2, th1)


if __name__ == '__main__':
    main()
