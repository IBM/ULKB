# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import MutableMapping

from . import util

__all__ = [
    'Settings',
]


class Settings(MutableMapping):

    def __init_subclass__(cls):
        cls._attributes = sorted(
            [k for k in dir(cls)
             if not hasattr(Settings, k) and not k.startswith('_')])

    @classmethod
    def _register_attribute(cls, name, value):
        cls._attributes.append(name)
        cls._attributes.sort()
        setattr(cls, name, value)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        for k in self._attributes:
            v = getattr(self, k)
            if isinstance(v, type) and issubclass(v, Settings):
                setattr(self, k, v())

    def _check_attribute(self, k):
        if k.startswith('_') or k in self._attributes:
            return getattr(self, k)
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' has no attribute '{k}'")

    def __call__(self, **kwargs):
        obj = self.copy()
        for k, v in kwargs.items():
            obj[k] = v
        return obj

    def __iter__(self):
        return iter(self._attributes)

    def __len__(self):
        return len(self._attributes)

    def __str__(self):
        from json import dumps
        return '\n'.join(util.starmap(
            lambda k, v: f'{k} = {dumps(v)}', self.recursive_items()))

    def __setattr__(self, k, v):
        u = self._check_attribute(k)
        if (isinstance(u, Settings) and not isinstance(v, Settings)):
            v = u(**v)          # bulk set
        return super().__setattr__(k, v)

    def __delattr__(self, k):
        v = self._check_attribute(k)
        if isinstance(v, Settings):
            setattr(self, k, v.__class__())  # reset
        else:
            super().__delattr__(k)

    def __getitem__(self, k):
        return self._check_attribute(k)

    def __setitem__(self, k, v):
        setattr(self, k, v)

    def __delitem__(self, k):
        delattr(self, k)

    def copy(self):
        return util.copy(self)

    def deepcopy(self):
        return util.deepcopy(self)

    def recursive_items(self, prefix=''):
        for k, v in self.items():
            if isinstance(v, Settings):
                for t in v.recursive_items(f'{prefix + k}.'):
                    yield t
            else:
                yield (prefix + k, v)
