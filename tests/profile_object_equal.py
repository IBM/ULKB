# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import random

from ulkb import *

from .profiler import Profiler

random.seed(0)


class A(Object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def rand_obj(width, height):
    w = random.randint(0, max(width, 0))
    h = random.randint(0, max(height, 0))
    if h == 0:
        return A()
    args = []
    for i in range(0, w + 1):
        if bool(random.randint(0, 1)):
            args.append(rand_obj(w, h-1))
        else:
            args.append(random.randint(0, 1000))
    return A(*args)


def main():
    global a
    a = rand_obj(50, 60)
    pf = Profiler(globals())
    pf.timeit('a == a')
    pf.timeit('a.equal(a)')
    pf.timeit('hash(a)')
    #pf.profile(lambda: hash(a))


if __name__ == '__main__':
    main()
