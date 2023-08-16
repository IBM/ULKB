# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestConverterSPARQL(ULKB_TestCase):

    maxDiff = 1024

    def assert_to_sparql(self, form, text, namespaces=dict(), **kwargs):
        from ulkb.converter.sparql import ConverterSPARQL
        nsm = settings.graph()._get_namespace_manager(namespaces)
        prefixes = ConverterSPARQL._get_prefixes(nsm)
        self.assertEqual(
            form.to_sparql(namespaces=namespaces, **kwargs),
            prefixes + '\n' + text)

    def test_sanity(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c = Constant('c', a)
        f = Constant('f', FunctionType(a, a))
        g = Constant('g', FunctionType(a, a, a))
        p = Constant('p', FunctionType(a, a, bool))
        q = Constant('q', FunctionType(a, a, a, bool))
        self.assertRaisesRegex(
            ConverterError, 'bad query type', x.to_sparql, query='x')
        self.assertRaisesRegex(
            TypeError, 'bad argument', a.to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', Truth().to_sparql, query='ask')
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', x.to_sparql, query='ask')
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', x.to_sparql, query='select')
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', x.to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'no variables to select', c.to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', f(x).to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', g(x, c).to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'bad limit', p(x, c).to_sparql, limit='x')
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', Not(x@bool).to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', q(x, x, x).to_sparql)
        self.assertRaisesRegex(
            ConverterError, 'cannot convert', Forall(x, p(x, y)).to_sparql)

    def test_convert_predicate(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c = Constant('c', a)
        f = Constant('f', FunctionType(a, a, bool))

        self.assert_to_sparql(
            f(x, y), '''\
ASK {
  ?x <f> ?y .
}\n''',
            query='ask')

        self.assert_to_sparql(
            f(x, y), '''\
SELECT DISTINCT ?x ?y
WHERE {
  ?x <f> ?y .
}\n''')

        query = f(x, y).to_sparql(rdflib_query=True)
        self.assertEqual(query._original_args[0], '''\
SELECT DISTINCT ?x ?y
WHERE {
  ?x <f> ?y .
}\n''')

        self.assert_to_sparql(
            f(x, c), '''\
SELECT DISTINCT ?x
WHERE {
  ?x <f> <c> .
}\n''')

        self.assert_to_sparql(
            f(x, y), '''\
SELECT DISTINCT ?y
WHERE {
  ?x <f> ?y .
}\n''',
            select=y)

        self.assert_to_sparql(
            f.with_annotations(uri='rdf:type')(x, c@{'uri': 'ex:c'}), '''\
SELECT DISTINCT ?x
WHERE {
  ?x rdf:type ex:c .
}\n''',
            namespaces={'ex': 'http://ex.org/'})

        self.assert_to_sparql(
            f.with_annotations(uri='rdf:type')(x, c@{'uri': 'ex:c'}), '''\
ASK {
  ?x rdf:type ex:c .
}\n''',
            query='ask', namespaces={'ex': 'http://ex.org/'})

        # -- with_optional --

        self.assert_to_sparql(
            f(x, y), '''\
ASK {
  ?x <f> ?y .
}\n''',
            query='ask',
            with_optional=[('_label', 'rdfs:label', None, None)])

        self.assert_to_sparql(
            f(y, x), '''\
SELECT DISTINCT ?y ?y_label ?x ?x_label
WHERE {
  ?y <f> ?x .
  OPTIONAL {
    ?y rdfs:label ?y_label .
  }
  OPTIONAL {
    ?x rdfs:label ?x_label .
  }
}\n''',
            select=[y, x],
            with_optional=[('_label', 'rdfs:label', None, None)])

        # -- limit --

        self.assert_to_sparql(
            f(x, y), '''\
ASK {
  ?x <f> ?y .
}\n''',
            query='ask', limit=12)

        self.assert_to_sparql(
            f(x, y), '''\
SELECT DISTINCT ?x ?y
WHERE {
  ?x <f> ?y .
}
LIMIT 12\n''',
            limit=12)

    def test_convert_equal(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))
        h = Variable('h', FunctionType(a, a, bool))

        query = f(c, y) & Equal(x, y) & g(x, c)
        self.assert_to_sparql(
            query, '''\
ASK {
  <c> <f> ?y .
  FILTER (?x = ?y)
  ?x <g> <c> .
}\n''',
            query='ask')

        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  <c> <f> ?y .
  FILTER (?x = ?y)
  ?x <g> <c> .
}\n''')

        query = eq(x, y, c, d)
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  FILTER (?x = ?y)
  FILTER (?y = <c>)
  FILTER (<c> = <d>)
}\n''')

    def test_convert_distinct(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))
        h = Variable('h', FunctionType(a, a, bool))

        query = f(c, y) & ne(x, y) & g(x, c)
        self.assert_to_sparql(
            query, '''\
ASK {
  <c> <f> ?y .
  FILTER (?x != ?y)
  ?x <g> <c> .
}\n''',
            query='ask')

    def test_convert_not(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))
        h = Variable('h', FunctionType(a, a, bool))

        query = f(c, y) & ~f(x, d) & g(x, c)
        self.assert_to_sparql(
            query, '''\
ASK {
  <c> <f> ?y .
  FILTER NOT EXISTS {
    ?x <f> <d> .
  }
  ?x <g> <c> .
}\n''',
            query='ask')

        query = (
            h(c, y) & ~f(x, d) & ~g.with_annotations(uri='rdf:type')(x, c))
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?h ?x ?y
WHERE {
  <c> ?h ?y .
  FILTER NOT EXISTS {
    ?x <f> <d> .
  }
  FILTER NOT EXISTS {
    ?x rdf:type <c> .
  }
}\n''')

    def test_convert_and(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))

        query = f(c, y) & f(x, d) & g(x, c)
        self.assert_to_sparql(
            query, '''\
ASK {
  <c> <f> ?y .
  ?x <f> <d> .
  ?x <g> <c> .
}\n''',
            query='ask')

        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  <c> <f> ?y .
  ?x <f> <d> .
  ?x <g> <c> .
}\n''')

        query = f(c, y) & ~f(x, d) & g(x, c) & ne(x, y)
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  <c> <f> ?y .
  FILTER NOT EXISTS {
    ?x <f> <d> .
  }
  ?x <g> <c> .
  FILTER (?x != ?y)
}\n''')

    def test_convert_or(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))

        query = f(c, y) | f(x, d)
        self.assert_to_sparql(
            query, '''\
ASK {
  {
    <c> <f> ?y .
  } UNION {
    ?x <f> <d> .
  }
}\n''',
            query='ask')

        query = f(c, y) | f(x, d) | g(y, x)
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  {
    {
      <c> <f> ?y .
    } UNION {
      ?x <f> <d> .
    }
  } UNION {
    ?y <g> ?x .
  }
}\n''',
            query='select')

        query = Or(f(c, y), f(x, d), g(y, x))
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  {
    <c> <f> ?y .
  } UNION {
    ?x <f> <d> .
  } UNION {
    ?y <g> ?x .
  }
}\n''',
            query='select')

        query = Or(f(c, y) & f(x, d), g(y, x))
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  {
    <c> <f> ?y .
    ?x <f> <d> .
  } UNION {
    ?y <g> ?x .
  }
}\n''',
            query='select')

        query = Or(f(c, y) & ~f(x, d), g(y, x))
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  {
    <c> <f> ?y .
    FILTER NOT EXISTS {
      ?x <f> <d> .
    }
  } UNION {
    ?y <g> ?x .
  }
}\n''')

        query = Or(f(c, y) & ~f(x, d), g(y, x) & Equal(x, c))
        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x ?y
WHERE {
  {
    <c> <f> ?y .
    FILTER NOT EXISTS {
      ?x <f> <d> .
    }
  } UNION {
    ?y <g> ?x .
    FILTER (?x = <c>)
  }
}\n''')

    def test_convert_exists(self):
        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        c, d = Constants('c', 'd', a)
        f, g = Constants('f', 'g', FunctionType(a, a, bool))

        query = Exists(y, f(c, y) & f(x, d) & g(x, c))
        self.assert_to_sparql(
            query, '''\
ASK {
  <c> <f> ?y .
  ?x <f> <d> .
  ?x <g> <c> .
}\n''',
            query='ask')

        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?x
WHERE {
  <c> <f> ?y .
  ?x <f> <d> .
  ?x <g> <c> .
}\n''')

        self.assert_to_sparql(
            query, '''\
SELECT DISTINCT ?y
WHERE {
  <c> <f> ?y .
  ?x <f> <d> .
  ?x <g> <c> .
}\n''',
            select=[y])


if __name__ == '__main__':
    main()
