# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..rule import *
from ..settings import Settings
from .formula import *

__all__ = [
    'RuleE',
]


class RuleE_Settings(Settings):
    """RuleE settings"""

    #: Temporary directory to use (`None` means use the default).
    tempdir = None

    #: Whether to delete the generated temporary file.
    delete = True


class RuleE(PrimitiveRule):

    @classmethod
    def _new(                   # (form,)
            cls, arg1, **kwargs):
        import os
        import subprocess
        from tempfile import NamedTemporaryFile
        settings = cls._thy().settings.prelude.rule_e(**kwargs)
        conj = Formula.check(arg1, cls.__name__, None, 1)
        conj_tptp = conj.to_tptp()
        hyps = cls._thy().to_tptp()
        with NamedTemporaryFile(
                prefix='ulkb_eprover_', suffix='.tptp', mode='w',
                delete=settings.delete, dir=settings.tempdir) as temp:
            if hyps:
                temp.write(hyps)
            temp.write(f'fof(main,conjecture,{conj_tptp}).\n')
            temp.flush()
            util.logging.debug(f'wrote {temp.name}')
            cmd = ['eprover', '--output-level=0', temp.name]
            ret = subprocess.run(cmd, text=True, capture_output=True)
            status = ret.returncode
            if status == 0 or status == 1:
                if status == 0:
                    return {}, conj
                else:
                    raise cls.error(f"failed to prove '{conj}'")
            else:
                raise RuntimeError(ret.stderr)
