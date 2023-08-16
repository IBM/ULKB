# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import re
import textwrap

from rdflib import Graph, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.plugins.sparql import prepareQuery

from .. import error, util
from ..settings import Settings
from .converter import Converter


class ConverterSPARQL_Settings(Settings):
    indent = 2
    limit = None
    query = 'select'
    rdflib_query = False
    with_optional = []


class ConverterSPARQL(
        Converter, format='sparql', format_long='SPARQL',
        settings=ConverterSPARQL_Settings):

    @classmethod
    def _get_prefixes(cls, nsm, _prefix=lambda k, v: f'PREFIX {k}: <{v}>'):
        return '\n'.join(util.starmap(_prefix, nsm.namespaces()))

    def __init__(self, cls, arg, namespaces={}, select=None, **kwargs):
        super().__init__(cls, arg, **kwargs)
        # settings
        self.settings = cls._thy().settings.converter.sparql(**kwargs)
        self.indent = self.settings.indent
        self.limit = self.settings.limit
        self.rdflib_query = self.settings.rdflib_query
        self.with_optional = self.settings.with_optional
        # internal attributes
        self.nsm = cls._thy().settings.graph()._get_namespace_manager(
            namespaces)
        self.namespaces = self.nsm._namespace_dict
        self.select = select

    def error_bad_query(self, query, line, column, details):
        return self.error(f'''\
bad query:
{query}
At line {line}, column {column}:
{details}''')

    def error_cannot_convert(self, obj):
        return self.error(f"cannot convert '{obj}'")

    def do_convert_from(self):
        # See <https://www.sciencedirect.com/science/article/pii/S1570826822000543>
        raise NotImplementedError

    def do_convert_to(self):
        from pyparsing.exceptions import ParseException
        form = self.cls.Term.check(self.arg)
        type = self.settings.query
        if type == 'ask':
            text = self._do_convert_to_ask(form)
        elif self.select is not None or type == 'select':
            self.settings.query = 'select'
            type = self.settings.query
            vars = self.select or ()
            if not isinstance(vars, (tuple, list)):
                vars = (vars,)
            text = self._do_convert_to_select(vars, form)
        else:
            raise self.error(f"bad query type '{type}'")
        try:
            query = prepareQuery(text, initNs=self.namespaces)
            if self.rdflib_query:
                return query
            else:
                prefixes = self._get_prefixes(self.nsm)
                return prefixes + '\n' + query._original_args[0]
        except ParseException as err:
            raise self.error_bad_query(
                err.args[0], err.lineno, err.column,
                err.explain()) from None
        except Exception as err:
            raise self.error(str(err)) from None

    def _do_convert_to_ask(self, form):
        return self._ask(self._formula_to_pattern(form))

    def _do_convert_to_select(self, vars, form):
        if not vars:
            vars = sorted(list(form.free_variables))
        else:
            vars = list(util.unique_everseen(
                filter(lambda x: x in form.variables, vars)))
        if not vars:
            raise self.error('no variables to select')
        where = self._formula_to_pattern(form)
        suffixes = []
        for t in self.with_optional:
            suffix, pred, lang, extra = t
            suffixes.append(suffix)
            text = '\n'.join(map(
                lambda x: self._with_optional_pattern(
                    x, suffix, pred, lang), vars))
            if extra:
                text += '\n' + extra
            where += '\n' + text
        if suffixes:
            vars = list(util.flatten(map(
                lambda x: (x, *map(
                    lambda y: self._with_suffix(x, y), suffixes)), vars)))
        vars = ' '.join(map(self._variable_to_pattern, vars))
        return self._select(vars, where, self.limit)

    def _formula_to_pattern(self, form):
        if form.is_not():
            (form,) = form.unpack_not()
            if form.is_equal():
                return self._filter_ne(*self._equal_to_pattern(form))
            else:
                return self._filter_not_exists(
                    self._formula_to_pattern(form))
        elif form.is_and():
            res = map(self._formula_to_pattern, form.unfold_and())
            return '\n'.join(res)
        elif form.is_or():
            return self._union(
                *map(self._formula_to_pattern, form.unfold_or()))
        elif form.is_exists():
            return self._formula_to_pattern(form.unpack_exists()[-1])
        elif form.is_application() and form.is_formula():
            if form.is_equal():
                return self._filter_eq(*self._equal_to_pattern(form))
            else:
                return self._atomic_formula_to_pattern(form)
        else:
            raise self.error_cannot_convert(form)

    def _equal_to_pattern(self, form):
        l, r = form.unpack_equal()
        return (
            self._atomic_term_to_pattern(l), self._atomic_term_to_pattern(r))

    def _atomic_formula_to_pattern(self, form):
        args = list(map(
            self._atomic_term_to_pattern, form.unfold_application()))
        if len(args) != 3 or None in args:
            raise self.error_cannot_convert(form)
        p, s, o = args
        return f'{s} {p} {o} .'

    def _atomic_term_to_pattern(self, term):
        if term.is_variable():
            return self._variable_to_pattern(term)
        elif term.is_constant():
            return self._constant_to_pattern(term)
        else:
            raise self.error_cannot_convert(term)

    def _variable_to_pattern(self, x):
        return '?' + x.id

    def _with_optional_pattern(self, x, suffix, pred, lang=None):
        a = x.TypeVariable('a')
        pred = x.Constant(pred, x.FunctionType(x.type, a, bool))
        var = self._with_suffix(x, suffix)
        pats = [self._formula_to_pattern(pred(x, var))]
        if lang is not None:
            pats.append(self._filter_lang(
                self._atomic_term_to_pattern(var), f'"{lang}"'))
        return self._optional(*pats)

    def _with_suffix(self, x, suffix):
        return x.with_args(f'{x.id}{suffix}', x.type)

    def _constant_to_pattern(self, c):
        uri = c.annotations.get('uri', c.id)
        try:
            uri = self.nsm.expand_curie(uri)
        except ValueError:
            pass
        return self.nsm.normalizeUri(uri)

    def _ask(self, text):
        return f'ASK {self._group(text)}\n'

    def _select(self, vars, text, limit=None):
        text = f'SELECT DISTINCT {vars}\nWHERE {self._group(text)}\n'
        if limit:
            try:
                text += f'LIMIT {max(0, int(limit))}\n'
            except ValueError:
                raise self.error(f"bad limit '{limit}'")
        return text

    def _filter_eq(self, left, right):
        return f'FILTER ({left} = {right})'

    def _filter_ne(self, left, right):
        return f'FILTER ({left} != {right})'

    def _filter_lang(self, left, right):
        return f'FILTER (LANG({left}) = "" || LANGMATCHES(LANG({left}), {right}))'

    def _filter_not_exists(self, *args):
        return 'FILTER NOT EXISTS ' + self._group(*args)

    def _optional(self, *args):
        return 'OPTIONAL ' + self._group('\n'.join(args))

    def _union(self, *args):
        return ' UNION '.join(map(self._group, args))

    def _group(self, *args):
        return '{\n' + self._indent('\n'.join(args)) + '\n}'

    def _indent(self, text, _re_blank=re.compile(r'^\s*\S')):
        return textwrap.indent(text, self.indent * ' ', _re_blank.match)
