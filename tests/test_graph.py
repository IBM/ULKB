# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import os

from ulkb import *

from .tests import ULKB_TestCase, main, skip_if_not_set

# skip_if_not_set('TEST_GRAPH')


class TestGraph(ULKB_TestCase):

    def test_sanity(self):
        a = TypeVariable('a')
        x = Variable('x', a)
        self.assertRaisesRegex(TypeError, 'bad argument', graph.ask, x)
        self.assertRaisesRegex(TypeError, 'bad argument', graph.select, x)
        self.assertRaisesRegex(
            TypeError, 'bad argument', graph.construct, x, x)
        self.assertRaisesRegex(
            TypeError, 'bad argument', graph.construct, Truth(), x)
        self.assertRaisesRegex(
            TypeError, 'bad argument',
            graph.paths, Truth(), Truth(), length='abc')
        self.assertRaisesRegex(
            TypeError, 'bad argument',
            graph.paths, Truth(), Truth(), cutoff='abc')

    def test_ask(self):
        a = TypeVariable('a')
        x = Variable('x', a)
        instanceOf = Constant(
            'instanceOf', FunctionType(a, a, bool), uri='wdt:P31')
        Human = Constant('Person', a, uri='wd:Q5')
        Cat = Constant('Cat', a, uri='wd:Q146')
        Madonna = Constant('Madonna', a, uri='wd:Q1744')
        self.assertTrue(graph.ask(Exists(x, instanceOf(x, Human))))
        self.assertTrue(graph.ask(instanceOf(Madonna, Human), timeout=10))
        self.assertFalse(graph.ask(instanceOf(Madonna, Cat)))

    def test_select(self):
        from time import sleep

        def ask(*args, **kwargs):
            sleep(1)
            return graph.ask(*args, **kwargs)

        def select(*args, **kwargs):
            sleep(1)
            return graph.select(*args, **kwargs)

        a = TypeVariable('a')
        x, y = Variables('x', 'y', a)
        instanceOf = Constant(
            'instanceOf', FunctionType(a, a, bool), uri='wdt:P31')
        ownedBy = Constant(
            'ownedBy', FunctionType(a, a, bool), uri='wdt:P127')
        hasCountry = Constant(
            'hasCountry', FunctionType(a, a, bool), uri='wdt:P17')
        Human = Constant('Person', a, uri='wd:Q5')
        Cat = Constant('Cat', a, uri='wd:Q146')
        Madonna = Constant('Madonna', a, uri='wd:Q1744')
        Hospital = Constant('Hospital', a, uri='wd:Q16917')
        Germany = Constant('Germany', a, uri='wd:Q183')

        for p in select(instanceOf(x, Human), limit=5):
            self.assertIsInstance(p, Constant)
            self.assertEqual(p.type, a)

        self.assertTrue(ask(instanceOf(
            *select(instanceOf(x, Human), limit=1), Human)))

        self.assertFalse(ask(instanceOf(
            *select(instanceOf(x, Human), limit=1), Cat)))

        it = select(
            instanceOf(x, Human)
            & instanceOf(y, Cat)
            & ownedBy(y, x),
            limit=1)
        for x, y in it:
            self.assertTrue(ask(instanceOf(x, Human)))
            self.assertTrue(ask(instanceOf(y, Cat)))
            self.assertTrue(ask(ownedBy(y, x)))

        x, y = Variables('x', 'y', a)
        it = select(
            instanceOf(y, Cat) & Not(Exists(x, ownedBy(y, x))),
            limit=2, named_tuples=True)
        for t in it:
            self.assertFalse(ask(Exists(x, ownedBy(t[y], x))))

        it = select(
            instanceOf(x, Hospital)
            & hasCountry(x, Germany),
            limit=5)
        self.assertEqual(len(list(it)), 5)

        height = Constant(
            'hasHeight', FunctionType(a, a, bool), uri='wdt:P2048')
        h = next(select(height(Madonna, x), limit=1))
        self.assert_constant(h, ('"164"^^xsd:decimal', a))

    def test_construct(self):
        a = TypeVariable('a')
        x = Variable('x', a)
        instanceOf = Constant(
            'instanceOf', FunctionType(a, a, bool), uri='wdt:P31')
        Human = Constant('Human', a, uri='wd:Q5')
        Cat = Constant('Cat', a, uri='wd:Q146')
        it = graph.construct(
            instanceOf(x, Cat),
            instanceOf(x, Human),
            limit=3)
        for stmt in it:
            op, arg1, arg2 = stmt.unfold_application()
            self.assertEqual(op, instanceOf)
            self.assertIsInstance(arg1, Constant)
            self.assertEqual(arg2, Cat)

    def test_paths(self):
        a = TypeVariable('a')
        Human = Constant('Human', a, uri='wd:Q5')
        Madonna = Constant('Madonna', a, uri='wd:Q1744')
        it = graph.paths(Madonna, Human, length=1, limit=1)
        for stmt in it:
            op, *args = stmt.unfold_application()
            self.assertEqual(op.annotations['uri'], 'wdt:P31')
            self.assertEqual(args[0], Madonna)
            self.assertEqual(args[1], Human)
        it = graph.paths(Madonna, Human, cutoff=2, limit=3)
        for stmt in it:
            if stmt.is_and():
                l, r = stmt.unpack_and()
                _, start, _ = l.unfold_application()
                _, _, end = r.unfold_application()
                self.assertEqual(start, Madonna)
                self.assertEqual(end, Human)
            else:
                op, *args = stmt.unfold_application()
                self.assertEqual(op.annotations['uri'], 'wdt:P31')
                self.assertEqual(args[0], Madonna)
                self.assertEqual(args[1], Human)
        # 1-hop from Madonna
        x = Variable('x', a)
        res = list(graph.paths(Madonna, x, length=1, limit=3))
        self.assertEqual(len(res), 3)
        for stmt in res:
            self.assertEqual(stmt.left.right, Madonna)
        # 1-hop to Madonna
        y = Variable('y', a)
        res = list(graph.paths(x, Madonna, length=1, limit=3))
        self.assertEqual(len(res), 3)
        for stmt in res:
            self.assertEqual(stmt.right, Madonna)

    def test_sparql(self):
        self.assertTrue(graph.sparql('ASK {?x wdt:P31 wd:Q5}')['boolean'])


if __name__ == '__main__':
    main()
