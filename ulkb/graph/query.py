# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import error, util
from ..converter.sparql import ConverterSPARQL
from ..expression import Constant, TypeVariable, Variable
from ..theory import Theory
from .sparql import SPARQL

__all__ = [
    'Query',
]


class Query:

    _cached_sparql = None

    def __init__(
            self, uri=None, named_tuples=None, cutoff=None, length=1,
            **kwargs):
        # settings
        self.settings = Theory._thy().settings.graph(**kwargs)
        self.limit = self.settings.limit
        self.uri = uri or self.settings.uri
        # internal attributes
        if (self._cached_sparql is None  # reuse _sparql if possible
                or self._cached_sparql.uri != self.uri):
            self._cached_sparql = SPARQL(self.uri)
        self._sparql = self._cached_sparql
        self._sparql.timeout = self.settings.timeout
        self.nsm = self.settings._get_namespace_manager()
        self.namespaces = self.nsm._namespace_dict
        self.named_tuples = named_tuples
        self.cutoff = cutoff
        self.length = length

    def ask(self, form):
        form = Theory.Formula.check(form, 'ask', 'form', 1)
        query = form.to_sparql(query='ask')
        util.logging.debug(query)
        return self._sparql.eval(query)['boolean']

    def select(self, form):
        form = Theory.Formula.check(form, 'select', 'form', 1)
        self.vars = sorted(list(form.free_variables))
        with_optional = []
        if self.settings.with_description:
            with_optional.append([
                self.settings.with_description_suffix,
                self.settings.with_description_predicate,
                self.settings.with_description_language,
                self.settings.with_description_extra])
        if self.settings.with_label:
            with_optional.append([
                self.settings.with_label_suffix,
                self.settings.with_label_predicate,
                self.settings.with_label_language,
                self.settings.with_label_extra])
        query = form.to_sparql(
            limit=self.limit, with_optional=with_optional)
        util.logging.debug(query)
        bindings = self._sparql.eval(query)['results']['bindings']
        return map(self._select_row, bindings)

    def _select_row(self, row):
        if self.named_tuples:
            return {x: self._select_var(row, x) for x in self.vars}
        else:
            it = map(lambda x: self._select_var(row, x), self.vars)
            if len(self.vars) > 1:
                return tuple(it)
            else:
                return next(it)

    def _select_var(self, row, x):
        from rdflib import Literal  # FIXME: move this to somewhere else

        from .wikidata import Wikidata
        entry = row[x.id]
        if entry['type'] == 'uri':
            uri = self.nsm.normalizeUri(entry['value'])
            if uri[0] == '<' and uri[-1] == '>':
                uri = uri[1:-1]
            id, type, kwargs = uri, x.type, {'uri': uri}
            if self.settings.with_description:
                desc = x.id + self.settings.with_description_suffix
                if desc in row:
                    kwargs['description'] = row[desc]['value']
                else:
                    desc = Wikidata.get_property_description(entry['value'])
                    if desc:
                        kwargs['description'] = desc
            if self.settings.with_label:
                label = x.id + self.settings.with_label_suffix
                if label in row:
                    kwargs['label'] = row[label]['value']
                else:
                    label = Wikidata.get_property_label(entry['value'])
                    if label:
                        kwargs['label'] = label
            try:
                return Theory.top.lookup_constant(
                    id).with_annotations(**kwargs)
            except LookupError:
                return Constant(id, x.type, **kwargs)
        elif entry['type'] == 'literal':
            lit = Literal(
                entry['value'], datatype=entry.get('datatype', None))
            return Constant(lit.n3(self.nsm), x.type)
        else:
            raise NotImplementedError

    def construct(self, tpl, form):
        tpl = Theory.Formula.check(tpl, 'construct', 'tpl', 1)
        form = Theory.Formula.check(form, 'construct', 'form', 2)
        self.named_tuples = True
        return map(lambda theta: tpl.substitute(theta), self.select(form))

    def paths(self, source, target):
        source = Theory.Term.check(source, 'paths', 'source', 1)
        target = Theory.Term.check(target, 'paths', 'target', 2)
        cutoff = self.cutoff
        length = self.length
        if cutoff:
            def _get(i):
                util.logging.debug(f'searching for paths of length {i}')
                return self._paths_of_length(source, target, i)
            cutoff = max(1, error.check_arg_class(cutoff, int, 'paths'))
            return util.flatten(map(_get, range(1, cutoff + 1)))
        else:
            length = max(1, error.check_arg_class(length, int, 'paths'))
            return self._paths_of_length(source, target, length)

    def _paths_of_length(self, source, target, n):
        tvar_ids = set(map(
            lambda x: x.id, source.type_variables | target.type_variables))
        a_id = util.get_variant_not_in('a', tvar_ids)
        b_id = util.get_variant_not_in('b', tvar_ids)
        c_id = util.get_variant_not_in('c', tvar_ids)
        var_ids = set(map(
            lambda x: x.id, source.variables | target.variables))
        x_id = util.get_variant_not_in('x', var_ids)
        p_id = util.get_variant_not_in('p', var_ids)
        xs = map(
            lambda i: Variable(
                f'{x_id}_{i}', TypeVariable(f'{a_id}_{i}')),
            util.count(0))
        ps = map(
            lambda i: Variable(
                f'{p_id}_{i}', Theory.FunctionType(
                    TypeVariable(f'{b_id}_{i}'),
                    TypeVariable(f'{c_id}_{i}'), bool)),
            util.count(0))
        nodes = util.peekable(util.chain(
            [source], util.islice(xs, n - 1), [target]))
        edges = util.islice(ps, n)
        if n == 1:
            (query,) = map(
                lambda p: p(util.first(nodes), nodes.peek()), edges)
        else:
            query = Theory.And(*map(
                lambda p: p(util.first(nodes), nodes.peek()), edges))
        return self.construct(query, query)

    def sparql(self, text):
        prefixes = ConverterSPARQL._get_prefixes(self.nsm)
        return self._sparql.eval(prefixes + '\n' + text)
