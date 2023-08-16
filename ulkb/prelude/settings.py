# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..commands import _thy
from ..settings import Settings
from .rule_e import RuleE_Settings
from .rule_z3 import RuleZ3_Settings

__all__ = [
    'PreludeSettings'
]


class PreludeSettings(Settings):
    """Prelude settings."""

    #: :class:`RuleE` settings.
    rule_e = RuleE_Settings

    #: :class:`RuleZ3` settings.
    rule_z3 = RuleZ3_Settings


_thy().settings.prelude = PreludeSettings()
