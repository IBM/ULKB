# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Sequent(TestSerializerULKB):

    def test_defaults(self):
        x = Variable('x', bool)
        self.assert_to_ulkb(
            (RuleRefl(x),
             '⊢ x ↔ x'),
            omit_types=True)


if __name__ == '__main__':
    main()
