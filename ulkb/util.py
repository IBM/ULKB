# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

"""
Utility functions.

(Not intended for external use.)
"""
import logging
from collections import deque
from copy import copy, deepcopy
from functools import cmp_to_key, lru_cache, reduce, total_ordering, wraps
from hashlib import sha256
from itertools import chain, combinations, count, dropwhile, repeat, starmap
from pathlib import Path
from re import compile

from more_itertools import (always_reversible, first, flatten, islice_extended,
                            last, peekable, sliding_window, unique_everseen)

islice = islice_extended


# -- Combinators -----------------------------------------------------------

def identity(x):
    """The identity function, i.e., (𝜆 x ⇒ x)."""
    return x


def all_map(f, xs):
    """Tests whether `f` holds for all `x` in `xs`."""
    return all(map(f, xs))


def any_map(f, xs):
    """Tests whether `f` holds for some `x` in `xs`."""
    return any(map(f, xs))


def flip(f):
    """Returns the function (𝜆 x, y ⇒ f(y, x))."""
    @wraps(f)
    def g(x, y):
        return f(y, x)
    return g


def foldl(f, x, xs):
    """Left-folds `xs` with using `f` and starting value `x`."""
    return reduce(f, xs, x)


def foldl_args(f, x, *args):
    """Same as :func:`foldl` but applies to varargs."""
    return foldl(f, x, args)


def foldl1(f, xs):
    """Left-folds `xs` using `f` and no starting value."""
    return reduce(f, xs)


def foldl1_args(f, *args):
    """Same as :func:`foldl1` but applies to varargs."""
    return foldl1(f, args)


def foldl_infix(f, g, arg1, arg2, *args, **kwargs):
    """Left-fold variant used to apply infix operators.

    For example:

    .. code-block:: python

       foldl_infix(f, g, [1,2,3,4,5], **kwargs)

    is equivalent to:

    .. code-block:: python

       f(g(g(g(1, 2), 3), 4), 5, **kwargs)
    """
    if not args:
        return f(arg1, arg2, **kwargs)
    else:
        it = chain([arg1, arg2], islice(args, len(args) - 1))
        return f(foldl1(g, it), args[-1], **kwargs)


def unfoldl(f, x):
    """Left-unfolds `x` using unpacking function `f`.

    Equivalent to:

    .. code-block:: python

       def g(x):
          if f(x) is None:      # no more unpacking
             return [x]
          else:
             return g(x[0]) + [x[1]]

    Used to recover values which were left-folded.  For example:

    .. code-block:: python

       >>> f = (lambda t: t if isinstance(t, tuple) else None)
       >>> it = unfold(f, (((1, 2), 3), 4))
       >>> list(it)
       [1, 2, 3, 4]
    """
    return always_reversible(_unfoldl(f, x))


def _unfoldl(f, x):
    while True:
        t = f(x)
        if t is None:
            yield x
            break
        x, r = t
        yield r


def foldr(f, x, xs):
    """Right-folds `xs` using `f` and starting value `x`."""
    #
    # This seems to be the fastest version.
    # See <tests/profile_util.py>.
    #
    for y in reversed(xs):
        x = f(y, x)
    return x


def foldr_args(f, x, *args):
    """Same as :func:`foldr` but applies to varargs."""
    return foldr(f, x, args)


def foldr1(f, xs):
    """Right-folds `xs` using `f` and no starting value."""
    #
    # The efficiency remarks regarding foldr() also apply here.
    # See <tests/profile_util.py>.
    #
    it = reversed(xs)
    x = next(it)
    for y in it:
        x = f(y, x)
    return x


def foldr1_args(f, *args):
    """Same as :func:`foldr1` but applies to varargs."""
    return foldr1(f, args)


def foldr_infix(f, g, arg1, arg2, *args, **kwargs):
    """Right-fold variant used to apply infix operators.

    For example:

    .. code-block:: python

       foldr_infix(f, g, [1,2,3,4,5], **kwargs)

    is equivalent to:

    .. code-block:: python

       f(1, g(2, g(3, g(4, 5))), **kwargs)
    """
    if not args:
        return f(arg1, arg2, **kwargs)
    else:
        return f(arg1, foldr1_args(g, arg2, *args), **kwargs)


def unfoldr(f, x):
    """Right-unfolds `x` using unpacking function `f`.

    Equivalent to:

    .. code-block:: python

       def h(t):
          if f(t) is None:      # no more unpacking
             return [t]
          else:
             return [t[0]] + h(t[1])

    Used to recover values which were right-folded.  For example:

    .. code-block:: python

       >>> f = (lambda t: t if isinstance(t, tuple) else None)
       >>> it = unfold(f, (1, (2, (3, 4))))
       >>> list(it)
       [1, 2, 3, 4]
    """
    while True:
        t = f(x)
        if t is None:
            yield x
            break
        l, x = t
        yield l


def map_args(f, *args):
    """Same as :func:`map` but applies to varargs."""
    return map(f, args)


def match_first(f, xs, x=None):
    """Returns the first element of `xs` satisfying `f`; or `x`"""
    return foldr(lambda x, y: x if f(x) else y, x, xs)


def match_last(f, xs, x=None):  # last element satisfying f; or x
    """Returns the last element of `xs` satisfying `f`; or `x`."""
    return foldl(lambda x, y: y if f(y) else x, x, xs)


def sliding_pairs(it):
    """Returns a sliding window of width 2 over `it`."""
    return sliding_window(it, 2)


def sliding_pairs_args(x1, x2, *xs):
    """Same as :func:`sliding_pairs` but applies to varargs."""
    return sliding_pairs(chain([x1, x2], xs))


# -- Proxy -----------------------------------------------------------------

class Proxy:
    """Proxy object.

    Forwards any access to the object obtained using `get_proxy`.
    """

    def __init__(self, get_proxy):
        get_proxy = get_proxy if callable(get_proxy) else lambda: get_proxy
        super().__setattr__('_get_proxy', get_proxy)

    def __call__(self, *args, **kwargs):
        return self._get_proxy()(*args, **kwargs)

    def __getattr__(self, k):
        return getattr(self._get_proxy(), k)

    def __setattr__(self, k, v):
        setattr(self._get_proxy(), k, v)

    def __delattr__(self, k):
        delattr(self._get_proxy(), k)

    def __str__(self):
        return str(self._get_proxy())


# -- Imports ---------------------------------------------------------------

def get_package_data_dir(modname):
    """Returns package-data directory of `modname`."""
    import importlib
    return Path(importlib.util.find_spec(modname).origin).parent


# -- Misc ------------------------------------------------------------------

class Nil:
    """Class representing the absence of value."""
    pass


def camel2snake(
        name,
        re1=compile(r'(.)([A-Z][a-z]+)'),
        re2=compile(r'([a-z0-9])([A-Z])')):
    """Converts `name` from camel-case to snake-case."""
    return re2.sub(r'\1_\2', re1.sub(r'\1_\2', name)).lower()


def get_variant(name, re=compile(r'(.*?)(\d*)$')):
    """Returns the next numerical-suffixed variant of `name`."""
    pre, suf = re.match(name).groups()
    if suf:
        return pre + str(int(suf) + 1)
    else:
        return pre + '0'


def get_variant_not_in(name, avoid):
    """Same as :func:`get_variant` but skip variants in `avoid`."""
    var = name
    while var in avoid:
        var = get_variant(name)
    return var
