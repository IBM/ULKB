# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import timeit as timeit_

__all__ = [
    'Profiler',
]


class Profiler:

    def __init__(self, globals):
        self._globals = globals

    def timeit(self, *args, globals=None, number=timeit_.default_number):
        globals = globals or self._globals
        for code in args:
            print('>>>', code)
            dt = timeit_.timeit(code, globals=globals, number=number)
            print(f'{dt:.1f}s')

    def profile(self, f):
        import cProfile
        import os
        import shutil
        import subprocess
        import tempfile
        prof = cProfile.Profile()
        prof.runcall(f)
        tmpdir = tempfile.mkdtemp()
        proffile = os.path.join(tmpdir, 'profile')
        prof.dump_stats(proffile)
        cgraphfile = os.path.join(tmpdir, 'callgraph')
        subprocess.run(['pyprof2calltree', '-k', '-i', proffile,
                        '-o', cgraphfile], check=True)
