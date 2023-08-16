# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import json

from ..expression import Constant, TypeVariable, Variable
from ..theory import Theory
from .query import Query

__all__ = [
    'Wikidata',
]


class Wikidata:

    _uri = Theory._thy().settings.graph.uri
    _all_properties = None

    @classmethod
    def get_all_properties(cls):
        if cls._all_properties is None:
            cls._all_properties = cls._load_all_properties()
        return cls._all_properties

    @classmethod
    def get_property_description(cls, uri):
        props = cls.get_all_properties()
        if uri not in props:
            return None
        return props[uri].get('description', None)

    @classmethod
    def get_property_label(cls, uri):
        props = cls.get_all_properties()
        if uri not in props:
            return None
        return props[uri].get('label', None)

    @classmethod
    def _load_all_properties(cls):
        from importlib import util as importlib_util
        from pathlib import Path
        dir = Path(importlib_util.find_spec(__name__).origin).parent
        with open(dir / 'wikidata_properties.json') as fp:
            return json.load(fp)

    @classmethod
    def _get_all_properties(cls, uri=None):
        res = Query(uri=uri or cls._uri).sparql('''
SELECT DISTINCT ?x ?xLabel ?xDescription WHERE {
  ?x wikibase:propertyType ?y.
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
  }
}''')
        rows = res['results']['bindings']
        nsm = settings.graph()._get_namespace_manager()

        def collect(t):
            k = t['x']['value']
            v = {'wd': k}
            if 'xLabel' in t:
                v['label'] = t['xLabel']['value']
            if 'xDescription' in t:
                v['description'] = t['xDescription']['value']
            k = f'wdt:{nsm.normalizeUri(k)[3:]}'
            return nsm.expand_curie(k), v
        return dict(map(collect, rows))

    @classmethod
    def _dump_all_properties(cls, uri=None):
        with open('wikidata_properties.json', 'w') as fp:
            json.dump(cls._get_all_properties(uri), fp, indent=2)

    # @classmethod
    # def Q(cls, id=None, label=None, limit=None):
    #     a = TypeVariable('a')
    #     x = Variable('x', a)
    #     y = Variable('y', a)
    #     instanceOf = Constant('wdt:P31', Theory.FunctionType(a, a, bool))
    #     query = Query(uri=cls._uri, limit=limit)
    #     if id is not None:
    #         if isinstance(id, int):
    #             id = str(id)
    #         if not id.startswith('wd:Q'):
    #             id = f'wd:Q{id}'
    #         c = Constant(id, a)
    #         it = query.select(
    #             Theory.Exists(y, instanceOf(x, y) & Theory.Equal(x, c)))
    #         return next(it)
    #     elif label is not None:
    #         raise NotImplementedError

    @classmethod
    def Q(cls, id, uri=None):
        if isinstance(id, int):
            id = str(id)
        if not id.startswith('wd:Q'):
            id = f'wd:Q{id}'
        res = Query(uri=uri or cls._uri).sparql('''
SELECT DISTINCT ?x ?xLabel ?xDescription WHERE {
  BIND(%s as ?x)
  ?x wdt:P31 ?y.
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
  }
} LIMIT 1
''' % id)
        nsm = settings.graph()._get_namespace_manager()
        rows = res['results']['bindings']
        if not rows:
            return None
        t = rows[0]
        id = nsm.normalizeUri(t['x']['value'])
        label = t['xLabel']['value']
        descr = t['xDescription']['value']
        return Constant(
            id, TypeVariable('a'), label=label, description=descr)


if __name__ == '__main__':
    uri = None
    # uri = 'https://query.wikidata.org/sparql'
    Wikidata._dump_all_properties(uri)
