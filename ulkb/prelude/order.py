# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .type_int import *
from .type_real import *

__all__ = [
    'ge',
    'gt',
    'le',
    'lt',
]


# FIXME
def ge(x, y): return ge_z(x, y) if x.type == int_ else ge_r(x, y)
def gt(x, y): return gt_z(x, y) if x.type == int_ else gt_r(x, y)
def le(x, y): return le_z(x, y) if x.type == int_ else le_r(x, y)
def lt(x, y): return lt_z(x, y) if x.type == int_ else lt_r(x, y)
