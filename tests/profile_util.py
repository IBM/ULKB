# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import functools

from ulkb import util

from .profiler import Profiler


def sum_v1(it):
    total = 0
    for n in it:
        total += n
    return total


def sum_v2(it, f=lambda x, y: x + y):
    total = 0
    for n in it:
        total = f(total, n)
    return total


def reduce(f, x, xs):
    return functools.reduce(f, xs, x)


def foldl(f, x, xs):
    for y in iter(xs):
        x = f(x, y)
    return x


def foldr_v1(f, x, xs):
    return reduce(util.flip(f), x, reversed(xs))


def foldr_v2(f, x, xs):
    for y in reversed(xs):
        x = f(y, x)
    return x


def foldr1_v1(f, xs):
    return functools.reduce(util.flip(f), reversed(xs))


def foldr1_v2(f, xs):
    it = reversed(xs)
    x = next(it)
    for y in it:
        x = f(y, x)
    return x


total = sum(range(0, 100))
input = 'range(0, 100)'

pf = Profiler(globals())
pf.timeit(
    f'assert sum_v1({input}) == {total}',
    f'assert sum_v2({input}) == {total}',
    f'assert reduce(lambda x, y: x + y, 0, {input}) == {total}',
    f'assert foldl(lambda x, y: x + y, 0, {input}) == {total}',
    f'assert foldr_v1(lambda x, y: x + y, 0, {input}) == {total}',
    f'assert foldr_v2(lambda x, y: x + y, 0, {input}) == {total}',
    f'assert foldr1_v1(lambda x, y: x + y, {input}) == {total}',
    f'assert foldr1_v2(lambda x, y: x + y, {input}) == {total}')


# pf.profile(lambda: util.foldr(lambda x, y: x + y, 0, range(0, 1000)))
