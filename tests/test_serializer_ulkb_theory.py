# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Theory(TestSerializerULKB):

    def test_defaults(self):
        pass
        #self.assert_to_ulkb((Theory(), Theory.top.to_ulkb()))


if __name__ == '__main__':
    main()
