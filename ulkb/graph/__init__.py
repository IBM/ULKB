# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .error import GraphError
from .query import Query
from .wikidata import Wikidata


def ask(form, **kwargs):
    return Query(**kwargs).ask(form)


def select(form, **kwargs):
    return Query(**kwargs).select(form)


def construct(tpl, form, **kwargs):
    return Query(**kwargs).construct(tpl, form)


def paths(source, target, **kwargs):
    return Query(**kwargs).paths(source, target)


def sparql(text, **kwargs):
    return Query(**kwargs).sparql(text)


wikidata = Wikidata
