# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main

aty = TypeVariable('a')
xyz = list(Variables(*'xyz', aty))
ABCDE = list(Constants(*'ABCDE', FunctionType(aty, bool)))
abcde = list(Constants(*'abcde', aty))
pqrst = list(Constants(*'pqrst', FunctionType(aty, aty, bool)))

Ity = BaseType('I')             # object domain
ixyz = list(Variables(*'xyz', Ity))
iABCDE = list(Constants(*'ABCDE', FunctionType(Ity, bool)))
iabcde = list(Constants(*'abcde', Ity))
ipqrst = list(Constants(*'pqrst', FunctionType(Ity, Ity, bool)))

Dty = BaseType('D')             # data domain
dxyz = list(Variables(*'xyz', Dty))
dABCDE = list(Constants(*'ABCDE', FunctionType(Dty, bool)))
dpqrst = list(Constants(*'pqrst', FunctionType(Ity, Dty, bool)))


class TestParserONF(ULKB_TestCase):

    def assert_owl_time(self, thy, ity=aty, dty=aty):
        ix, iy, iz = Variables(*'xyz', ity)
        dx, dy, dz = Variables('dx', 'dy', 'dz', dty)
        # constants
        before = thy.lookup_constant('before')
        after = thy.lookup_constant('after')
        DateTimeDescription = thy.lookup_constant('DateTimeDescription')
        day = thy.lookup_constant('day')
        gDay = thy.lookup_constant('xsd:gDay')
        # axioms
        axioms = set(map(lambda ax: ax[1], thy.axioms_dict.values()))
        # InverseObjectProperties(:after :before)
        self.assertIn(
            Forall(ix, iy, Implies(after(ix, iy), before(iy, ix))),
            axioms)
        # SubClassOf(:DateTimeDescription DataAllValuesFrom(:day xsd:gDay))
        self.assertIn(
            Forall(ix, Implies(
                DateTimeDescription(ix),
                Forall(dy, Implies(
                    day(ix, dy),
                    gDay(dy))))),
            axioms)

    def test_parse_file(self):
        self.assert_owl_time(Theory.from_ofn(path='tests/data/time.ofn'))

    def test_parse_string(self):
        with open('tests/data/time.ofn') as fp:
            with Theory() as thy:
                ity = thy.new_base_type('I')
                dty = thy.new_base_type('D')
                Theory.from_ofn(
                    fp.read(), theory=thy, domain=ity, data_domain=dty)
                self.assert_owl_time(thy, ity, dty)

    def test_parse_stream(self):
        with open('tests/data/time.ofn', 'rb') as fp:
            self.assert_owl_time(Theory.from_ofn(fp))

    # -- Ontology(...) -----------------------------------------------------

    def test_parse_ontology_document(self):
        # failure: empty string
        self.assertRaises(ParserError, Theory.from_ofn, '')

        # failure: no ontology
        self.assertRaises(ParserError, Theory.from_ofn, '''\
Prefix(skos:=<http://www.w3.org/2004/02/skos/core#>)
''')

        # empty ontology
        thy = Theory.from_ofn('Ontology()')
        self.assertIsInstance(thy, Theory)

        # prefix declarations
        thy = Theory.from_ofn('''\
Prefix(:=<http://www.w3.org/2006/time#>)
Prefix(skos:=<http://www.w3.org/2004/02/skos/core#>)
Ontology()
''')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(
            thy.annotations['prefixes'][''],
            'http://www.w3.org/2006/time#')
        self.assertEqual(
            thy.annotations['prefixes']['skos'],
            'http://www.w3.org/2004/02/skos/core#')

        # ontology_iri
        thy = Theory.from_ofn('Ontology(<http://ex.org>)')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(
            thy.annotations['ontology_iri'],
            'http://ex.org')

        # version_iri
        thy = Theory.from_ofn('''\
Ontology(<http://ex.org> <http://ex.org/2023>)
''')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(
            thy.annotations['ontology_iri'],
            'http://ex.org')
        self.assertEqual(
            thy.annotations['version_iri'],
            'http://ex.org/2023')

        # imports
        thy = Theory.from_ofn(
            'Ontology(Import(<http://www.w3.org/2006/time>))')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(
            thy.annotations['imports'],
            ['http://www.w3.org/2006/time'])

        # annotations
        thy = Theory.from_ofn('''\
Ontology(
Annotation(rdfs:label "Test"@en)
Annotation(rdfs:label "Teste"@es)
Annotation(dct:created "2023-03-26"^^xsd:date)
Annotation(dct:license <https://creativecommons.org/licenses/by/4.0/>)
)''')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(
            thy.annotations['dct:created'], '"2023-03-26"^^xsd:date')
        self.assertEqual(
            thy.annotations['dct:license'],
            '<https://creativecommons.org/licenses/by/4.0/>')
        self.assertEqual(
            thy.annotations['rdfs:label'],
            'Test')

        # annotations: language option
        thy = Theory.from_ofn('''\
Ontology(
Annotation(rdfs:label "Test"@en)
Annotation(rdfs:label "Teste"@es)
)''', language='es')
        self.assertIsInstance(thy, Theory)
        self.assertEqual(thy.annotations['rdfs:label'], 'Teste')

        # axioms
        thy = Theory.from_ofn('''\
Ontology(
Declaration(Class(:Pizza))
)''')
        self.assertIsInstance(thy, Theory)
        self.assert_constant(
            thy.lookup_constant('Pizza'),
            ('Pizza', FunctionType(aty, bool)))

        # axioms: prefix option
        thy = Theory.from_ofn('''\
Ontology(
Declaration(Class(:Pizza))
)''', prefix='onto')
        self.assertIsInstance(thy, Theory)
        self.assert_constant(
            thy.lookup_constant('onto:Pizza'),
            ('onto:Pizza', FunctionType(aty, bool)))

        thy = Theory.from_ofn(
            'Ontology(SameIndividual(:a :b))', prefix='onto')
        self.assertEqual(
            thy.lookup_axiom('ax_onto_same_1')[1],
            Equal(Constant('onto:a', aty), Constant('onto:b', aty)))

        # axioms: axiom_prefix option
        thy = Theory.from_ofn(
            'Ontology(SameIndividual(:a :b))', axiom_prefix='onto')
        self.assertEqual(
            thy.lookup_axiom('ax_onto_same_1')[1],
            Equal(Constant('a', aty), Constant('b', aty)))

        # axioms: theory option
        with Theory() as thy:
            Theory.from_ofn('''
Ontology(
Annotation(rdfs:label "Test"@en)
Declaration(Class(:Pizza))
)''', theory=thy)
            self.assertEqual(thy.annotations['rdfs:label'], 'Test')
            self.assert_constant(
                thy.lookup_constant('Pizza'),
                ('Pizza', FunctionType(aty, bool)))

    # -- Axiom -------------------------------------------------------------

    def test_parse_axiom(self):
        # option start
        ext = Object.from_ofn('Declaration(Class(:Pizza))', start='axiom')
        self.assert_new_constant(
            ext, (Constant('Pizza', FunctionType(aty, bool)),))

    # -- Declaration(Class(...)) -------------------------------------------

    def test_parse_declaration_class(self):
        # success
        ext = Extension.from_ofn('Declaration(Class(:Pizza))')
        self.assert_new_constant(
            ext, (Constant('Pizza', FunctionType(aty, bool)),))

        # annotations
        ext = Extension.from_ofn('''
Declaration(
  Annotation(rdfs:label "Pizza")
  Annotation(dct:created "2023-03-26"^^xsd:date)
  Class(:Pizza)
)''')
        self.assert_new_constant(
            ext, (Constant('Pizza', FunctionType(aty, bool)),),
            {'dct:created': '"2023-03-26"^^xsd:date',
             'rdfs:label': 'Pizza'})

        # option domain
        ity = BaseType('I')
        ext = Extension.from_ofn('Declaration(Class(:Pizza))', domain=ity)
        self.assert_new_constant(
            ext, (Constant('Pizza', FunctionType(ity, bool)),))

    # -- Declaration(Datatype(...)) ----------------------------------------

    def test_parse_declaration_datatype(self):
        # success
        ext = Extension.from_ofn('Declaration(Datatype(:size))')
        self.assert_new_constant(
            ext, (Constant('size', FunctionType(aty, bool)),))

        # option data domain
        ext = Extension.from_ofn(
            'Declaration(Datatype(:size))', data_domain=Dty)
        self.assert_new_constant(
            ext, (Constant('size', FunctionType(Dty, bool)),))

    # -- Declaration(ObjectProperty(...)) ----------------------------------

    def test_parse_declaration_object_property(self):
        # success
        ext = Extension.from_ofn('Declaration(ObjectProperty(:likes))')
        self.assert_new_constant(
            ext, (Constant('likes', FunctionType(aty, aty, bool)),))

        # option domain
        ity = BaseType('I')
        ext = Extension.from_ofn(
            'Declaration(ObjectProperty(:size))', domain=ity)
        self.assert_new_constant(
            ext, (Constant('size', FunctionType(ity, ity, bool)),))

    # -- Declaration(DataProperty(...)) ------------------------------------

    def test_parse_declaration_data_property(self):
        # success
        ext = Extension.from_ofn('Declaration(DataProperty(:age))')
        self.assert_new_constant(
            ext, (Constant('age', FunctionType(aty, aty, bool)),))

        # option data domain
        dty = BaseType('D')
        ext = Extension.from_ofn(
            'Declaration(DataProperty(:age))', domain=dty)
        self.assert_new_constant(
            ext, (Constant('age', FunctionType(dty, dty, bool)),))

    # -- Declaration(AnnotationProperty(...)) ------------------------------

    def test_parse_declaration_annotation_property(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct',
            NewAxiom.from_ofn, 'Declaration(AnnotationProperty(:p))')

    # -- Declaration(NamedIndividual(...)) ---------------------------------

    def test_parse_declaration_named_individual(self):
        # success
        ext = Extension.from_ofn('Declaration(NamedIndividual(:bob))')
        self.assert_new_constant(
            ext, (Constant('bob', aty),))

        # option domain
        ity = BaseType('I')
        ext = Extension.from_ofn(
            'Declaration(NamedIndividual(:bob))', domain=ity)
        self.assert_new_constant(
            ext, (Constant('bob', ity),))

    # -- SubClassOf(...) ---------------------------------------------------

    def test_parse_axiom_sub_class_of(self):
        x, y, z = xyz
        y1, y2, y3 = Variables('y1', 'y2', 'y3', y.type)
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        ix, iy, iz = ixyz
        iy1, iy2, iy3 = Variables('y1', 'y2', 'y3', iy.type)
        iA, iB, iC, iD, iE = iABCDE
        ip, iq, ir, is_, it = ipqrst

        dx, dy, dz = dxyz
        dy1, dy2, dy3 = Variables('y1', 'y2', 'y3', dy.type)
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # failure: class_cons
        self.assertRaises(
            ParserError, NewAxiom.from_ofn, 'SubClassOf(:A)')

        # class_cons
        ax = NewAxiom.from_ofn('SubClassOf(:A :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(A(x), B(x))),))

        # class_cons: annotations
        ax = NewAxiom.from_ofn(
            'SubClassOf(Annotation(rdfs:comment "hello") :A :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(A(x), B(x)))),
            {'rdfs:comment': 'hello'})

        # failure: object_intersection_of
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectIntersectionOf(:A) :C)')

        # object_intersection_of
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectIntersectionOf(:A :B) :C)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(A(x) & B(x), C(x)))))

        ax = NewAxiom.from_ofn(
            'SubClassOf(:A ObjectIntersectionOf(:B :C :D :E))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x), And(B(x), C(x), D(x), E(x))))))

        # failure: object_union_of
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectUnionOf(:A) :C)')

        # object_union_of
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectUnionOf(:A :B) :C)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(A(x) | B(x), C(x)))))

        ax = NewAxiom.from_ofn(
            'SubClassOf(:A ObjectUnionOf(:B :C :D :E))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x), Or(B(x), C(x), D(x), E(x))))))

        # failure: object_complement_of
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectComplementOf() :C)')

        # object_complement_of
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectComplementOf(:A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(~A(x), B(x)))))

        ax = NewAxiom.from_ofn(
            'SubClassOf(:B ObjectComplementOf(ObjectUnionOf(:A :B)))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(B(x), ~(A(x) | B(x))))))

        # failure: object_one_of
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(:A ObjectOneOf())')

        # object_one_of
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectOneOf(:a :b :c) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Or(Equal(x, a), Equal(x, b), Equal(x, c)),
                     B(x)))))

        # failure: object_some_values_from
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectSomeValuesFrom(:p) :B)')

        # object_some_values_from
        ax = NewAxiom.from_ofn(
            'SubClassOf(:A ObjectSomeValuesFrom(:p :B))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Exists(y, p(x, y) & B(y))))))

        ax = NewAxiom.from_ofn('''\
SubClassOf(:A ObjectSomeValuesFrom(ObjectInverseOf(:p) ObjectOneOf(:a)))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Exists(y, p(y, x) & Equal(y, a))))))

        # failure: object_all_values_from
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(:A ObjectAllValuesFrom(:p :A :B))')

        # object_all_values_from
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectAllValuesFrom(:p :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Forall(y, Implies(p(x, y), A(y))),
                     B(x)))))

        # failure: object_has_value
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(:A ObjectHasValue(:p :a :b))')

        # object_has_value
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectHasValue(:p :a) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     p(x, a),
                     B(x)))))

        # failure: object_has_self
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectHasSelf(:p :a) :B)')

        # object_has_self
        ax = NewAxiom.from_ofn(
            'SubClassOf(:A ObjectHasSelf(:p))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     p(x, x)))))

        # failure: object_min_cardinality
        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectMinCardinality(:p :B) :B)')

        self.assertRaises(
            ParserError, NewAxiom.from_ofn,
            'SubClassOf(ObjectMinCardinality(:p :p :B) :B)')

        # object_min_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(:A ObjectMinCardinality(1 :p))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Exists(y, p(x, y))))))

        # object_max_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectMaxCardinality(1 :p :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y) & A(y)),
                     B(x)))))

        # object_exact_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(ObjectExactCardinality(1 :p :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y) & A(y)),
                     B(x)))))

        # data_some_values_from
        ax = NewAxiom.from_ofn(
            'SubClassOf(DataSomeValuesFrom(:p :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y) & A(y)),
                     B(x)))))

        ax = NewAxiom.from_ofn(  # domain
            'SubClassOf(DataSomeValuesFrom(:p :A) :B)', domain=Ity)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     Exists(iy, ip(ix, iy) & iA(iy)),
                     iB(ix)))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(DataSomeValuesFrom(:p :A) :B)',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     Exists(dy, dp(ix, dy) & dA(dy)),
                     iB(ix)))))

        ax = NewAxiom.from_ofn(
            'SubClassOf(DataSomeValuesFrom(:p :q :r :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y1, y2, y3, And(
                         p(x, y1),
                         q(x, y2),
                         r(x, y3),
                         A(y1),
                         A(y2),
                         A(y3))),
                     B(x)))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(DataSomeValuesFrom(:p :q :r :A) :B)',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     Exists(dy1, dy2, dy3, And(
                         dp(ix, dy1),
                         dq(ix, dy2),
                         dr(ix, dy3),
                         dA(dy1),
                         dA(dy2),
                         dA(dy3))),
                     iB(ix)))))

        # data_all_values_from
        ax = NewAxiom.from_ofn(
            'SubClassOf(:A DataAllValuesFrom(:p :B))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Forall(y, Implies(p(x, y), B(y)))))))

        ax = NewAxiom.from_ofn(  # domain
            'SubClassOf(:A DataAllValuesFrom(:p :B))', domain=Ity)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     A(ix),
                     Forall(iy, Implies(ip(ix, iy), iB(iy)))))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(:A DataAllValuesFrom(:p :B))',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     iA(ix),
                     Forall(dy, Implies(dp(ix, dy), dB(dy)))))))

        ax = NewAxiom.from_ofn(
            'SubClassOf(:A DataAllValuesFrom(:p :q :r :B))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Forall(y1, y2, y3, Implies(
                         p(x, y1),
                         q(x, y2),
                         r(x, y3),
                         And(B(y1), B(y2), B(y3))))))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(:A DataAllValuesFrom(:p :q :r :B))',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     iA(ix),
                     Forall(dy1, dy2, dy3, Implies(
                         dp(ix, dy1),
                         dq(ix, dy2),
                         dr(ix, dy3),
                         And(dB(dy1), dB(dy2), dB(dy3))))))))

        # data_has_value
        ax = NewAxiom.from_ofn(
            'SubClassOf(DataHasValue(:p "0"^^xsd:nonNegativeInteger) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     p(x, Constant('"0"^^xsd:nonNegativeInteger', aty)),
                     B(x)))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(DataHasValue(:p "0"^^xsd:nonNegativeInteger) :B)',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     dp(ix, Constant('"0"^^xsd:nonNegativeInteger', Dty)),
                     iB(ix)))))

        # data_min_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(DataMinCardinality(8 :p) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y)),
                     B(x)))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(DataMinCardinality(8 :p) :B)',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     Exists(dy, dp(ix, dy)),
                     iB(ix)))))

        # data_max_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(:A DataMaxCardinality(1 :p :B))')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     A(x),
                     Exists(y, p(x, y) & B(y))))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(:A DataMaxCardinality(1 :p :B))',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     iA(ix),
                     Exists(dy, dp(ix, dy) & dB(dy))))))

        # data_exact_cardinality
        ax = NewAxiom.from_ofn(
            'SubClassOf(DataExactCardinality(1 :p :A) :B)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y) & A(y)),
                     B(x)))))

        ax = NewAxiom.from_ofn(  # domain, data_domain
            'SubClassOf(DataExactCardinality(1 :p :A) :B)',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(ix, Implies(
                     Exists(dy, dp(ix, dy) & dA(dy)),
                     iB(ix)))))

    # -- EquivalentClasses(...) --------------------------------------------

    def test_parse_axiom_equivalent_classes(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, *_ = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('EquivalentClasses(:A :B :C :D)')
        self.assert_new_axiom(
            ax, (Constant('ax_equiv_1', bool),
                 Forall(x, And(
                     Iff(A(x), B(x)),
                     Iff(B(x), C(x)),
                     Iff(C(x), D(x))))))

        # annotations
        ax = NewAxiom.from_ofn('''\
EquivalentClasses(Annotation(abc:def "15"^^xsd:string)
:A ObjectIntersectionOf(:B ObjectUnionOf(:C :D)))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_equiv_1', bool),
                 Forall(x, Iff(A(x), B(x) & (C(x) | D(x))))),
            {'abc:def': '"15"^^xsd:string'})

    # -- DisjointClasses(...) ----------------------------------------------

    def test_parse_axiom_disjoint_classes(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('DisjointClasses(:A :B :C :D)')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_1', bool),
                 Forall(x, And(
                     Implies(A(x), ~B(x)),
                     Implies(A(x), ~C(x)),
                     Implies(A(x), ~D(x)),
                     Implies(B(x), ~C(x)),
                     Implies(B(x), ~D(x)),
                     Implies(C(x), ~D(x))))))

        # annotations
        ax = NewAxiom.from_ofn('''\
DisjointClasses(
Annotation(abc:def "33"^^xsd:nonNegativeInteger)
Annotation(<http://ex.org> <http://ex.org>)
ObjectSomeValuesFrom(:p :A) ObjectIntersectionOf(:B ObjectOneOf(:c :d)))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_1', bool),
                 Forall(x, Implies(
                     Exists(y, p(x, y) & A(y)),
                     ~(B(x) & (Equal(x, c) | Equal(x, d)))))),
            {'abc:def': '"33"^^xsd:nonNegativeInteger',
             '<http://ex.org>': '<http://ex.org>'})

    # -- DisjointUnion(...) ------------------------------------------------

    def test_parse_axiom_disjoint_union(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('DisjointUnion(:A :B :C :D)')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_union_1', bool),
                 Forall(x, And(
                     Iff(A(x), Or(B(x), C(x), D(x))),
                     Implies(B(x), ~C(x)),
                     Implies(B(x), ~D(x)),
                     Implies(C(x), ~D(x))))))

        ax = NewAxiom.from_ofn('''\
DisjointUnion(
Annotation(_:b "33"^^xsd:nonNegativeInteger)
Annotation(<http://ex.org> rdfs:label)
  :C
  ObjectIntersectionOf(ObjectHasValue(:p :a) ObjectHasSelf(:p))
  ObjectComplementOf(:B))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_union_1', bool),
                 Forall(x, And(
                     Iff(C(x), Or(p(x, a) & p(x, x), ~B(x))),
                     Implies(p(x, a) & p(x, x), ~~B(x))))),
            {'<http://ex.org>': 'rdfs:label',
             '_:b': '"33"^^xsd:nonNegativeInteger'})

    # -- SubObjectPropertyOf(...) ------------------------------------------

    def test_parse_axiom_sub_object_property_of(self):
        x, y, z = xyz
        y0, y1, y2, y3, y4 = Variables('y0', 'y1', 'y2', 'y3', 'y4', aty)
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn('SubObjectPropertyOf(:p :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     q(x, y)))))

        # object_property_chain
        ax = NewAxiom.from_ofn('''\
SubObjectPropertyOf(ObjectPropertyChain(:p :q ObjectInverseOf(:r) :s) :t)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, y1, y2, y3, y, Implies(
                     And(p(x, y1),
                         q(y1, y2),
                         r(y3, y2),
                         s(y3, y)),
                     t(x, y)))))

        # annotation
        ax = NewAxiom.from_ofn('''\
SubObjectPropertyOf(
  Annotation(abc:def abc:def)
  ObjectInverseOf(:p) :q)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_sub_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     q(x, y)))),
            {'abc:def': 'abc:def'})

    # -- EquivalentObjectProperties(...) -----------------------------------

    def test_parse_axiom_equivalent_object_properties(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn('EquivalentObjectProperties(:p :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_equiv_1', bool),
                 Forall(x, y, Iff(
                     p(x, y),
                     q(x, y)))))

        # annotations
        ax = NewAxiom.from_ofn('''
EquivalentObjectProperties(
  Annotation(<http://x.org/a> "hello")
  :p :q :r ObjectInverseOf(:s))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_equiv_1', bool),
                 Forall(x, y, And(
                     Iff(p(x, y), q(x, y)),
                     Iff(q(x, y), r(x, y)),
                     Iff(r(x, y), s(y, x))))),
            {'<http://x.org/a>': 'hello'})

    # -- DisjointObjectProperties(...) -------------------------------------

    def test_parse_axiom_disjoint_object_properties(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'DisjointObjectProperties(ObjectInverseOf(:p) :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     ~q(x, y)))))

        # annotations
        ax = NewAxiom.from_ofn('''
DisjointObjectProperties(
  Annotation(skos:historyNote "0"^^xsd:decimal)
  :p :q :r ObjectInverseOf(:s))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_disj_1', bool),
                 Forall(x, y, And(
                     Implies(p(x, y), ~q(x, y)),
                     Implies(p(x, y), ~r(x, y)),
                     Implies(p(x, y), ~s(y, x)),
                     Implies(q(x, y), ~r(x, y)),
                     Implies(q(x, y), ~s(y, x)),
                     Implies(r(x, y), ~s(y, x))))),
            {'skos:historyNote': '"0"^^xsd:decimal'})

    # -- InverseObjectProperties(...) --------------------------------------

    def test_parse_axiom_inverse_object_properties(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'InverseObjectProperties(:p :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_inv_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     q(y, x)))))

        # annotations
        ax = NewAxiom.from_ofn('''
InverseObjectProperties(
  Annotation(abc:def "0"^^<http://ex.org>)
  Annotation(<http://ex.org> "hola"@es)
  ObjectInverseOf(:p) ObjectInverseOf(:q))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_inv_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     q(x, y)))),
            {'abc:def': '"0"^^<http://ex.org>'})

    # -- ObjectPropertyDomain(...) -----------------------------------------

    def test_parse_axiom_object_property_domain(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'ObjectPropertyDomain(:p :A)')
        self.assert_new_axiom(
            ax, (Constant('ax_dom_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     A(x)))))

        # annotations
        ax = NewAxiom.from_ofn('''
ObjectPropertyDomain(
  Annotation(rdfs:label <x:y>)
  ObjectInverseOf(:p)
  ObjectComplementOf(ObjectComplementOf(:A)))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_dom_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     ~~A(x)))),
            {'rdfs:label': '<x:y>'})

    # -- ObjectPropertyRange(...) ------------------------------------------

    def test_parse_axiom_object_property_range(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'ObjectPropertyRange(:p :A)')
        self.assert_new_axiom(
            ax, (Constant('ax_ran_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     A(y)))))

        # annotations
        ax = NewAxiom.from_ofn('''
ObjectPropertyRange(
  Annotation(rdfs:label "1"^^xsd:decimal)
  ObjectInverseOf(:p)
  ObjectHasSelf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_ran_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     p(y, y)))),
            {'rdfs:label': '"1"^^xsd:decimal'})

    # -- FunctionalObjectProperty(...) -------------------------------------

    def test_parse_axiom_functional_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'FunctionalObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_fun_1', bool),
                 Forall(x, y, z, Implies(
                     p(x, y),
                     p(x, z),
                     Equal(y, z)))))

        # annotations
        ax = NewAxiom.from_ofn('''
FunctionalObjectProperty(
  Annotation(_:b _:b)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_fun_1', bool),
                 Forall(x, y, z, Implies(
                     p(y, x),
                     p(z, x),
                     Equal(y, z)))),
            {'_:b': '_:b'})

    # -- InverseFunctionalObjectProperty(...) ------------------------------

    def test_parse_axiom_inverse_functional_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'InverseFunctionalObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_inv_fun_1', bool),
                 Forall(x, y, z, Implies(
                     p(y, x),
                     p(z, x),
                     Equal(y, z)))))

        # annotations
        ax = NewAxiom.from_ofn('''
InverseFunctionalObjectProperty(
  Annotation(_:b :b)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_inv_fun_1', bool),
                 Forall(x, y, z, Implies(
                     p(x, y),
                     p(x, z),
                     Equal(y, z)))),
            {'_:b': 'b'})

    # -- ReflexiveObjectProperty(...) --------------------------------------

    def test_parse_axiom_reflexive_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'ReflexiveObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_refl_1', bool),
                 Forall(x, p(x, x))))

        # annotations
        ax = NewAxiom.from_ofn('''
ReflexiveObjectProperty(
  Annotation(<http://ex.org/> _:b)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_refl_1', bool),
                 Forall(x, p(x, x))),
            {'<http://ex.org/>': '_:b'})

    # -- IrreflexiveObjectProperty(...) ------------------------------------

    def test_parse_axiom_irreflexive_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'IrreflexiveObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_irrefl_1', bool),
                 Forall(x, ~p(x, x))))

        # annotations
        ax = NewAxiom.from_ofn('''
IrreflexiveObjectProperty(
  Annotation(_:b <http://ex.org/>)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_irrefl_1', bool),
                 Forall(x, Not(p(x, x)))),
            {'_:b': '<http://ex.org/>'})

    # -- SymmetricObjectProperty(...) --------------------------------------

    def test_parse_axiom_symmetric_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'SymmetricObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_symm_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     p(y, x)))))

        # annotations
        ax = NewAxiom.from_ofn('''
SymmetricObjectProperty(
  Annotation(:hello "5")
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_symm_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     p(x, y)))),
            {'hello': '5'})

    # -- AsymmetricObjectProperty(...) -------------------------------------

    def test_parse_axiom_asymmetric_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'AsymmetricObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_asymm_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     ~p(y, x)))))

        # annotations
        ax = NewAxiom.from_ofn('''
AsymmetricObjectProperty(
  Annotation(:hello :hello)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_asymm_1', bool),
                 Forall(x, y, Implies(
                     p(y, x),
                     ~p(x, y)))),
            {'hello': 'hello'})

    # -- TransitiveObjectProperty(...) -------------------------------------

    def test_parse_axiom_transitive_object_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, s, t = pqrst

        # success
        ax = NewAxiom.from_ofn(
            'TransitiveObjectProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_trans_1', bool),
                 Forall(x, y, z, Implies(
                     p(x, y),
                     p(y, z),
                     p(x, z)))))

        # annotations
        ax = NewAxiom.from_ofn('''
TransitiveObjectProperty(
  Annotation(a:b <a>)
  ObjectInverseOf(:p))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_trans_1', bool),
                 Forall(x, y, z, Implies(
                     p(y, x),
                     p(z, y),
                     p(z, x)))),
            {'a:b': '<a>'})

    # -- SubDataPropertyOf(...) --------------------------------------------

    def test_parse_axiom_sub_data_property_of(self):
        x, y, z = xyz
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn('SubDataPropertyOf(:p :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_data_sub_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     q(x, y)))))

        # annotations
        ax = NewAxiom.from_ofn('''\
SubDataPropertyOf(
  Annotation(:hello <http://x.org/>)
  :p :q)
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_sub_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     dq(ix, dy)))),
            {'hello': '<http://x.org/>'})

    # -- EquivalentDataProperties(...) -------------------------------------

    def test_parse_axiom_equivalent_data_properties(self):
        x, y, z = xyz
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn('EquivalentDataProperties(:p :q)')
        self.assert_new_axiom(
            ax, (Constant('ax_data_equiv_1', bool),
                 Forall(x, y, Iff(
                     p(x, y),
                     q(x, y)))))

        # annotations
        ax = NewAxiom.from_ofn('''
EquivalentDataProperties(
  Annotation(<http://x.org/a> "hello")
  :p :q :r :s)
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_equiv_1', bool),
                 Forall(ix, dy, And(
                     Iff(dp(ix, dy), dq(ix, dy)),
                     Iff(dq(ix, dy), dr(ix, dy)),
                     Iff(dr(ix, dy), ds(ix, dy))))),
            {'<http://x.org/a>': 'hello'})

    # -- DisjointDataProperties(...) ---------------------------------------

    def test_parse_axiom_disjoint_data_properties(self):
        x, y, z = xyz
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn(
            'DisjointDataProperties(:p :q)', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_disj_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     ~dq(ix, dy)))))

        # annotations
        ax = NewAxiom.from_ofn('''
DisjointDataProperties(
  Annotation(skos:historyNote "0"^^xsd:decimal)
  :p :q :r :s)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_data_disj_1', bool),
                 Forall(x, y, And(
                     Implies(p(x, y), ~q(x, y)),
                     Implies(p(x, y), ~r(x, y)),
                     Implies(p(x, y), ~s(x, y)),
                     Implies(q(x, y), ~r(x, y)),
                     Implies(q(x, y), ~s(x, y)),
                     Implies(r(x, y), ~s(x, y))))),
            {'skos:historyNote': '"0"^^xsd:decimal'})

    # -- DataPropertyDomain(...) -------------------------------------------

    def test_parse_axiom_data_property_domain(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn(
            'DataPropertyDomain(:p :A)')
        self.assert_new_axiom(
            ax, (Constant('ax_data_dom_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     A(x)))))

        # annotations
        ax = NewAxiom.from_ofn('''
DataPropertyDomain(
  Annotation(rdfs:label <x:y>)
  :p :A)
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_dom_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     iA(ix)))),
            {'rdfs:label': '<x:y>'})

    # -- DataPropertyRange(...) --------------------------------------------

    def test_parse_axiom_data_property_range(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # datatype_cons
        ax = NewAxiom.from_ofn(
            'DataPropertyRange(:p :A)')
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(x, y, Implies(
                     p(x, y),
                     A(y)))))

        # datatype_cons: annotations
        ax = NewAxiom.from_ofn('''
DataPropertyRange(
  Annotation(rdfs:label "1"^^xsd:decimal)
  :p :A)
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     dA(dy)))),
            {'rdfs:label': '"1"^^xsd:decimal'})

        # data_intersection_of
        ax = NewAxiom.from_ofn(
            'DataPropertyRange(:p DataIntersectionOf(:A :B :C))',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     And(dA(dy), dB(dy), dC(dy))))))

        # data_union_of
        ax = NewAxiom.from_ofn('''\
DataPropertyRange(:p DataIntersectionOf(:A DataUnionOf(:B :C :D)))
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     And(dA(dy), Or(dB(dy), dC(dy), dD(dy)))))))

        # data_complement_of
        ax = NewAxiom.from_ofn('''\
DataPropertyRange(:p
   DataIntersectionOf(:A
     DataComplementOf(DataComplementOf(DataUnionOf(:B :C :D)))))
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     And(dA(dy), ~~Or(dB(dy), dC(dy), dD(dy)))))))

        # data_one_of
        ax = NewAxiom.from_ofn(
            'DataPropertyRange(:p DataOneOf("a" "0"^^xsd:decimal "c"))',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     Or(Equal(dy, Constant('"a"', Dty)),
                        Equal(dy, Constant('"0"^^xsd:decimal', Dty)),
                        Equal(dy, Constant('"c"', Dty)))))))

        # datatype_restriction
        ax = NewAxiom.from_ofn('''\
DataPropertyRange(:p DatatypeRestriction(:A b:c "c" d:e "0"^^xsd:decimal))
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_ran_1', bool),
                 Forall(ix, dy, Implies(
                     dp(ix, dy),
                     dA(dy)))))

    # -- FunctionalDataProperty(...) ---------------------------------------

    def test_parse_axiom_functional_data_property(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn(
            'FunctionalDataProperty(:p)')
        self.assert_new_axiom(
            ax, (Constant('ax_data_fun_1', bool),
                 Forall(x, y, z, Implies(
                     p(x, y),
                     p(x, z),
                     Equal(y, z)))))

        # annotations
        ax = NewAxiom.from_ofn('''\
FunctionalDataProperty(Annotation(_:b _:b) :p)
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_fun_1', bool),
                 Forall(ix, dy, dz, Implies(
                     dp(ix, dy),
                     dp(ix, dz),
                     Equal(dy, dz)))),
            {'_:b': '_:b'})

    # -- DatatypeDefinition(...) -------------------------------------------

    def test_parse_axiom_datatype_definition(self):
        x, *_ = xyz
        A, B, *_ = ABCDE

        dx, *_ = dxyz
        dA, dB, dC, dD, dE = dABCDE

        ax = NewAxiom.from_ofn(
            'DatatypeDefinition(:A DataComplementOf(:B))')
        self.assert_new_axiom(
            ax, (Constant('ax_data_def_1', bool),
                 Forall(x, Iff(A(x), ~B(x)))))

        ax = NewAxiom.from_ofn('''\
DatatypeDefinition(:A DataUnionOf(DataComplementOf(:B) :C :D :E))
''', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_def_1', bool),
                 Forall(dx, Iff(
                     dA(dx),
                     Or(~dB(dx), dC(dx), dD(dx), dE(dx))))))

    # -- HasKey(...) -------------------------------------------------------

    def test_parse_axiom_has_key(self):
        x, y, z = xyz
        z1, z2, z3 = Variables('z1', 'z2', 'z3', aty)
        w1, w2, w3 = Variables('w1', 'w2', 'w3', aty)
        A, B, C, D, E = ABCDE
        p, q, r, s, t = pqrst
        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ip, iq, ir, is_, it = ipqrst
        dx, dy, dz = dxyz
        dw1, dw2, dw3 = Variables('w1', 'w2', 'w3', Dty)
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # failure: empty pexps and dpexps
        self.assertRaisesRegex(
            ParserError, 'ignored construct',
            NewAxiom.from_ofn, 'HasKey(:A () ())')

        # empty dpexps
        ax = NewAxiom.from_ofn('HasKey(:A (:p) ())')
        self.assert_new_axiom(
            ax, (Constant('ax_has_key_1', bool),
                 Forall(x, y, z1, Implies(
                     And(A(x),
                         A(y),
                         p(x, z1),
                         p(y, z1)),
                     Equal(x, y)))))

        # empty pexps
        ax = NewAxiom.from_ofn('HasKey(:A () (:p :q))')
        self.assert_new_axiom(
            ax, (Constant('ax_has_key_1', bool),
                 Forall(x, y, w1, w2, Implies(
                     And(A(x),
                         A(y),
                         p(x, w1),
                         p(y, w1),
                         q(x, w2),
                         q(y, w2)),
                     Equal(x, y)))))

        ax = NewAxiom.from_ofn(
            'HasKey(:A () (:p :q))', domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_has_key_1', bool),
                 Forall(ix, iy, dw1, dw2, Implies(
                     And(iA(ix),
                         iA(iy),
                         dp(ix, dw1),
                         dp(iy, dw1),
                         dq(ix, dw2),
                         dq(iy, dw2)),
                     Equal(ix, iy)))))

        # annotations
        ax = NewAxiom.from_ofn('''\
HasKey(
  Annotation(rdfs:label "hello")
  ObjectComplementOf(:A) (:p :q) (:r :s))
''')
        self.assert_new_axiom(
            ax, (Constant('ax_has_key_1', bool),
                 Forall(x, y, z1, z2, w1, w2, Implies(
                     And(~A(x),
                         ~A(y),
                         p(x, z1),
                         p(y, z1),
                         q(x, z2),
                         q(y, z2),
                         r(x, w1),
                         r(y, w1),
                         s(x, w2),
                         s(y, w2)),
                     Equal(x, y)))),
            {'rdfs:label': 'hello'})

    # -- SameIndividual(...) -----------------------------------------------

    def test_parse_axiom_same_individual(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('SameIndividual(:a :b)')
        self.assert_new_axiom(
            ax, (Constant('ax_same_1', bool),
                 Equal(a, b)))

        # annotations
        ax = NewAxiom.from_ofn('''\
SameIndividual(
  Annotation(abc:def "15"^^xsd:string)
  :a :b :c :d)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_same_1', bool),
                 Equal.eq(a, b, c, d)),
            {'abc:def': '"15"^^xsd:string'})

    # -- DifferentIndividuals(...) -----------------------------------------

    def test_parse_axiom_different_individuals(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('DifferentIndividuals(:a :b)')
        self.assert_new_axiom(
            ax, (Constant('ax_diff_1', bool),
                 Not(Equal(a, b))))

        # annotations
        ax = NewAxiom.from_ofn('''\
DifferentIndividuals(
  Annotation(<http://ex.org/> "15"^^xsd:integer)
  :a :b :c :d)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_diff_1', bool),
                 Equal.ne(a, b, c, d)),
            {'<http://ex.org/>': '"15"^^xsd:integer'})

    # -- ClassAssertion(...) -----------------------------------------------

    def test_parse_axiom_class_assertion(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('ClassAssertion(:A :a)')
        self.assert_new_axiom(
            ax, (Constant('ax_class_1', bool),
                 A(a)))

        # annotations
        _b = Constant('_:b', aty)
        ax = NewAxiom.from_ofn('''\
ClassAssertion(
  Annotation(abc:def "99"^^xsd:nonNegativeInteger)
  ObjectIntersectionOf(ObjectHasValue(:p :a) ObjectHasSelf(:p))
  _:b)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_class_1', bool),
                 p(_b, a) & p(_b, _b)),
            {'abc:def': '"99"^^xsd:nonNegativeInteger'})

    # -- ObjectPropertyAssertion(...) --------------------------------------

    def test_parse_axiom_object_property_assertion(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('ObjectPropertyAssertion(:p :a :b)')
        self.assert_new_axiom(
            ax, (Constant('ax_prop_1', bool),
                 p(a, b)))

        # annotations
        _b = Constant('_:b', aty)
        ax = NewAxiom.from_ofn('''\
ObjectPropertyAssertion(
  Annotation(<http://ex.org> abc:def)
  ObjectInverseOf(:p) :a _:b)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_prop_1', bool),
                 p(_b, a)),
            {'<http://ex.org>': 'abc:def'})

    # -- NegativeObjectPropertyAssertion(...) ------------------------------

    def test_parse_axiom_negative_object_property_assertion(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        # success
        ax = NewAxiom.from_ofn('NegativeObjectPropertyAssertion(:p :a :b)')
        self.assert_new_axiom(
            ax, (Constant('ax_neg_prop_1', bool),
                 ~p(a, b)))

        # annotations
        a = Constant('<http://ex.org/a>', aty)
        _b = Constant('_:b', aty)
        ax = NewAxiom.from_ofn('''\
NegativeObjectPropertyAssertion(
  Annotation(<http://ex.org> abc:def)
  ObjectInverseOf(:p) _:b <http://ex.org/a>)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_neg_prop_1', bool),
                 ~p(a, _b)),
            {'<http://ex.org>': 'abc:def'})

    # -- DataPropertyAssertion(...) ----------------------------------------

    def test_parse_axiom_data_property_assertion(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ia, ib, ic, id, ie = iabcde
        ip, iq, ir, is_, it = ipqrst

        dx, dy, dz = dxyz
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn('DataPropertyAssertion(:p :a "abc")')
        self.assert_new_axiom(
            ax, (Constant('ax_data_prop_1', bool),
                 p(a, Constant('"abc"', aty))))

        ax = NewAxiom.from_ofn(
            'DataPropertyAssertion(:p :a "abc")',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_data_prop_1', bool),
                 dp(ia, Constant('"abc"', Dty))))

        # annotations
        _b = Constant('_:b', aty)
        ax = NewAxiom.from_ofn('''\
DataPropertyAssertion(
  Annotation(<http://ex.org> abc:def)
  :p :a "15"^^xsd:nonNegativeInteger)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_data_prop_1', bool),
                 p(a, Constant('"15"^^xsd:nonNegativeInteger', aty))),
            {'<http://ex.org>': 'abc:def'})

    # -- NegativeDataPropertyAssertion(...) --------------------------------

    def test_parse_axiom_negative_data_property_assertion(self):
        x, y, z = xyz
        A, B, C, D, E = ABCDE
        a, b, c, d, e = abcde
        p, q, r, *_ = pqrst

        ix, iy, iz = ixyz
        iA, iB, iC, iD, iE = iABCDE
        ia, ib, ic, id, ie = iabcde
        ip, iq, ir, is_, it = ipqrst

        dx, dy, dz = dxyz
        dA, dB, dC, dD, dE = dABCDE
        dp, dq, dr, ds, dt = dpqrst

        # success
        ax = NewAxiom.from_ofn('NegativeDataPropertyAssertion(:p :a "abc")')
        self.assert_new_axiom(
            ax, (Constant('ax_neg_data_prop_1', bool),
                 ~p(a, Constant('"abc"', aty))))

        ax = NewAxiom.from_ofn(
            'NegativeDataPropertyAssertion(:p :a "abc")',
            domain=Ity, data_domain=Dty)
        self.assert_new_axiom(
            ax, (Constant('ax_neg_data_prop_1', bool),
                 ~dp(ia, Constant('"abc"', Dty))))

        # annotations
        _b = Constant('_:b', aty)
        ax = NewAxiom.from_ofn('''\
NegativeDataPropertyAssertion(
  Annotation(<http://ex.org> abc:def)
  :p :a "15"^^xsd:nonNegativeInteger)
''')
        self.assert_new_axiom(
            ax, (Constant('ax_neg_data_prop_1', bool),
                 ~p(a, Constant('"15"^^xsd:nonNegativeInteger', aty))),
            {'<http://ex.org>': 'abc:def'})

    # -- AnnotationAssertion(...) ------------------------------------------

    def test_parse_axiom_annotation_assertion(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct', NewAxiom.from_ofn,
            'AnnotationAssertion(:p :a :b)')

    # -- AnnotationAssertion(...) ------------------------------------------

    def test_parse_axiom_annotation_assertion(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct', NewAxiom.from_ofn,
            'AnnotationAssertion(:p :a :b)')

    # -- SubAnnotationPropertyOf(...) --------------------------------------

    def test_parse_axiom_sub_annotation_property_of(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct', NewAxiom.from_ofn,
            'SubAnnotationPropertyOf(:p :q)')

    # -- AnnotationPropertyDomain(...) -------------------------------------

    def test_parse_axiom_annotation_property_domain(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct', NewAxiom.from_ofn,
            'AnnotationPropertyDomain(:p <http://ex.org/>)')

    # -- AnnotationPropertyRange(...) --------------------------------------

    def test_parse_axiom_annotation_property_range(self):
        self.assertRaisesRegex(
            ParserError, 'ignored construct', NewAxiom.from_ofn,
            'AnnotationPropertyRange(:p <http://ex.org/>)')


if __name__ == '__main__':
    main()
