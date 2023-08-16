# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from lark import Lark, v_args
from lark.exceptions import UnexpectedInput, VisitError
from lark.visitors import Discard, Transformer_InPlaceRecursive
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import NamespaceManager, split_uri

from .. import error, util
from ..settings import Settings
from .parser import Parser


class ParserOFN_Settings(Settings):
    domain = None              # object domain type (𝛥I)
    data_domain = None         # data domain type (𝛥D)
    language = 'en'            # language tag to consider
    prefix = None              # ontology prefix
    axiom_prefix = None        # axiom prefix (ontology prefix if not given)
    start = None               # start symbol (guess from cls if not given)
    theory = None              # target theory (new one if not given)


class ParserOFN(
        Parser, format='ofn', format_long='OWL Functional Syntax',
        settings=ParserOFN_Settings):

    _parser = None

    def __init__(self, cls, encoding=None, **kwargs):
        super().__init__(cls, encoding=encoding, **kwargs)
        # settings
        self.settings = cls._thy().settings.parser.ofn(**kwargs)
        self.domain = self.settings.domain
        self.data_domain = self.settings.data_domain
        self.language = self.settings.language
        self.prefix = self.settings.prefix
        self.axiom_prefix = self.settings.axiom_prefix or self.prefix
        self.start = self.settings.start
        self.theory = self.settings.theory
        # internal attributes
        self.ity = self.domain  # type of individuals
        if self.ity is None:
            self.ity = self.cls.TypeVariable('a')
        self.dty = self.data_domain  # type of data
        if self.dty is None:
            self.dty = self.ity
        # results
        self.ontology_iri = None
        self.version_iri = None
        self.nsm = NamespaceManager(Graph())
        if self.prefix:
            self.nsm.bind(self.prefix, f'{self.prefix}:')
        self.prefixes = dict(self.nsm.namespaces())  # declared prefixes
        self.consts = dict()       # constants by (id,type)
        self.const_counts = dict()  # constant counts by id
        # parser
        with open(util.get_package_data_dir(__name__) / 'ofn.lark') as fp:
            self.parser = Lark(
                fp, start=['ontology_document', 'axiom'], parser='lalr',
                transformer=TreeToObject(self), maybe_placeholders=True,
                cache=True)

    def guess_start(self):
        if self.start:
            return self.start
        if issubclass(self.cls, self.cls.Extension):
            return 'axiom'
        else:
            return 'ontology_document'

    def do_parse_from_string(self, text):
        try:
            ret = self.parser.parse(text, start=self.guess_start())
            if ret == Discard:
                raise self.error(f'cannot convert ignored construct')
            else:
                return ret
        except VisitError as err:
            raise self.error(err)
        except UnexpectedInput as err:
            raise self.syntax_error(
                err.line, err.column, err.get_context(text)) from None


class TreeToObject(Transformer_InPlaceRecursive):

    inline_args = v_args(inline=True)

    def __init__(self, parser):
        super().__init__()
        self.parser = parser
        self.cls = parser.cls
        self.ity = parser.ity
        self.dty = parser.dty
        self.Cty = self.cls.FunctionType(self.ity, bool)
        self.OPty = self.cls.FunctionType(self.ity, self.ity, bool)
        self.Dty = self.cls.FunctionType(self.dty, bool)
        self.DPty = self.cls.FunctionType(self.ity, self.dty, bool)
        self.x = self.cls.Variable('x', self.ity)
        self.y = self.cls.Variable('y', self.ity)
        self.z = self.cls.Variable('z', self.ity)
        self.xyz = (self.x, self.y, self.z)
        self.dx = self.cls.Variable('dx', self.dty)
        self.dy = self.cls.Variable('dy', self.dty)
        self.dz = self.cls.Variable('dz', self.dty)
        self.dxyz = (self.dx, self.dy, self.dz)
        self.axn = 0

    def _fresh_axiom_id(self, label=None):
        self.axn += 1
        if self.parser.axiom_prefix:
            label = f'{self.parser.axiom_prefix}_{label}'
        return self.cls.Constant(
            f'ax_{label}_{self.axn}' if label else f'ax_{self.axn}', bool)

    def _iri2str(self, iri):
        if iri[0] == ':':
            return iri[1:]
        elif iri[0:2] == '_:':
            return str(iri)
        else:
            return self.parser.nsm.normalizeUri(iri)

    def _lit2str(self, lit):
        return lit.n3(self.parser.nsm)

    def _cons(self, v, ty, id_cb):
        id = id_cb(v)
        if (id, ty) in self.parser.consts:
            return self.parser.consts[(id, ty)]
        else:
            cons = self.cls.Constant(id, ty)
            self.parser.consts[(id, ty)] = cons
            if id not in self.parser.const_counts:
                self.parser.const_counts[id] = 0
            self.parser.const_counts[id] += 1
            return cons

    def _filter_discards_out(self, args, f=lambda x: x != Discard):
        return filter(f, args)

    def discard(self, *args, **kwargs):
        return Discard

    @inline_args
    def non_negative_integer(self, n):
        return int(n)

    @inline_args
    def quoted_string(self, s):
        return s.value[1:-1]

    @inline_args
    def full_iri(self, s):
        return URIRef(s[1:-1])

    @inline_args
    def prefix_name(self, name, colon):
        return name.value if name else ''

    @inline_args
    def abbreviated_iri(self, pfx, name):
        if pfx != '':
            if pfx not in self.parser.prefixes:
                ns = pfx + ':'
                self.parser.prefixes[pfx] = ns
                self.parser.nsm.bind(pfx, ns)
            return self.parser.nsm.expand_curie(f'{pfx}:{name}')
        else:
            if self.parser.prefix:
                pfx = self.parser.prefix
            return URIRef(f'{pfx}:{name}')

    def ontology_document(self, args):
        return args[-1]

    def prefix_declaration(self, args):
        name, iri = args
        self.parser.prefixes[name] = str(iri)
        self.parser.nsm.bind(name, iri)
        return self.discard()

    def _fix_punning(self, ext):
        if not ext.is_new_constant():
            return ext          # nothing to do
        (cons,) = ext.unpack_new_constant()
        id, ty = cons.unpack_constant()
        if self.parser.const_counts[id] <= 1:
            return ext          # nothing to do
        if ty == self.ity or ty == self.dty:
            return ext          # nothing to do
        if ty == self.Cty:
            sfx = 'C'
        elif ty == self.OPty:
            sfx = 'P'
        elif ty == self.Dty:
            sfx = 'D'
        elif ty == self.DPty:
            sfx = 'DP'
        else:
            error.should_not_get_here()
        if id[-1] == '>':
            id = f'{id[:-1]}_{sfx}>'
        else:
            id += f'_{sfx}'
        cons._args = (id, ty)
        return ext

    def ontology(self, args):
        imports, annots, axioms = args[-3], args[-2], args[-1]
        if imports:
            annots['imports'] = imports
        if self.parser.ontology_iri:
            annots['ontology_iri'] = str(self.parser.ontology_iri)
        if self.parser.version_iri:
            annots['version_iri'] = str(self.parser.version_iri)
        if self.parser.prefixes:
            annots['prefixes'] = self.parser.prefixes
        if self.parser.theory is None:
            return self.cls.Theory(
                *map(self._fix_punning, axioms), **annots)
        else:
            for k, v in annots.items():
                self.parser.theory._annotations[k] = v
            for ax in map(self._fix_punning, axioms):
                self.parser.theory.extend(ax)
            return self.parser.theory

    @inline_args
    def ontology_iri(self, iri):
        self.parser.ontology_iri = iri
        return self.discard()

    @inline_args
    def version_iri(self, iri):
        self.parser.version_iri = iri
        return self.discard()

    def directly_imports_documents(self, args):
        return list(map(str, args))

    def ontology_annotations(self, annots):
        # TODO: Handle pairs with same key.
        return dict(self._filter_discards_out(annots))

    def axioms(self, args):
        return self._filter_discards_out(args)

    def declaration(self, args):
        if len(args) == 1 or Discard in args:
            return self.discard()
        else:
            annots, cons = args
            return self.cls.NewConstant(cons, **annots)

    def axiom_annotations(self, annots):
        return dict(self._filter_discards_out(annots))

    @inline_args
    def annotation(self, annots_ignored, aprop, aval):
        if (isinstance(aval, Literal)
                and aval.language
                and aval.language != self.parser.language):
            return self.discard()
        else:
            if isinstance(aval, URIRef):
                val = self._iri2str(aval)
            elif isinstance(aval, Literal):
                if aval.datatype:
                    val = self._lit2str(aval)
                else:
                    val = aval.value
            else:
                error.should_not_get_here()
            return (self._iri2str(aprop), val)

    @inline_args
    def annotation_assertion(self, annots, aprop, subj_iri, aval):
        subj_id, subj_cons = self._iri2str(subj_iri), None
        for ((id, _), cons) in self.parser.consts.items():
            if subj_id == id:
                subj_cons = cons
                break
        if subj_cons is not None:
            k = self._iri2str(aprop)
            if isinstance(aval, Literal):
                v = self._lit2str(aval)
            elif isinstance(aval, URIRef):
                v = self._iri2str(aval)
            else:
                error.should_not_get_here()
            subj_cons._annotations[k] = v
        return self.discard()

    @inline_args
    def class_cons(self, iri):
        return self._cons(iri, self.Cty, self._iri2str)

    @inline_args
    def datatype_cons(self, iri):
        return self._cons(iri, self.Dty, self._iri2str)

    @inline_args
    def object_property_cons(self, iri):
        return self._cons(iri, self.OPty, self._iri2str)

    @inline_args
    def data_property_cons(self, iri):
        return self._cons(iri, self.DPty, self._iri2str)

    @inline_args
    def individual_cons(self, iri):
        return self._cons(iri, self.ity, self._iri2str)

    @inline_args
    def literal_cons(self, lit):
        return self._cons(lit, self.dty, self._lit2str)

    @inline_args
    def typed_literal(self, s, datatype):
        return Literal(s, datatype=datatype)

    @inline_args
    def string_literal_no_language(self, s):
        return Literal(s)

    @inline_args
    def string_literal_with_language(self, s, lang):
        return Literal(s, lang=lang)

    @inline_args
    def inverse_object_property(self, prop):
        return lambda x, y: prop(y, x)

    @inline_args
    def data_intersection_of(self, *drans):
        return self.object_intersection_of(*drans)

    @inline_args
    def data_union_of(self, *drans):
        return self.object_union_of(*drans)

    @inline_args
    def data_complement_of(self, dran):
        return self.object_complement_of(dran)

    def data_one_of(self, lits):
        return self.object_one_of(lits)

    @inline_args
    def datatype_restriction(self, datatype, *ignored):
        util.logging.debug('ignoring DatatypeRestriction(...)')
        return datatype

    @inline_args
    def object_intersection_of(self, *cexps):
        return lambda x: self.cls.And(*map(lambda f: f(x), cexps))

    @inline_args
    def object_union_of(self, *cexps):
        return lambda x: self.cls.Or(*map(lambda f: f(x), cexps))

    @inline_args
    def object_complement_of(self, cexp):
        return lambda x: self.cls.Not(cexp(x))

    def object_one_of(self, inds):
        if len(inds) == 1:
            return lambda x: self.cls.Equal(x, inds[0])
        else:
            return (lambda x: self.cls.Or(
                *map(lambda i: self.cls.Equal(x, i), inds)))

    def _object_some_values_from(self, y, pexp, cexp):
        return (lambda x: self.cls.Exists(y, self.cls.And(
            pexp(x, y), cexp(y))))

    @inline_args
    def object_some_values_from(self, pexp, cexp):
        return self._object_some_values_from(self.y, pexp, cexp)

    def _object_all_values_from(self, y, pexp, cexp):
        return (lambda x: self.cls.Forall(y, self.cls.Implies(
            pexp(x, y), cexp(y))))

    @inline_args
    def object_all_values_from(self, pexp, cexp):
        return self._object_all_values_from(self.y, pexp, cexp)

    @inline_args
    def object_has_value(self, pexp, ind):
        return lambda x: pexp(x, ind)

    @inline_args
    def object_has_self(self, pexp):
        return lambda x: pexp(x, x)

    def _object_cardinality_fallback(self, y, n, pexp, cexp):
        if cexp:
            return lambda x: self.cls.Exists(y, pexp(x, y) & cexp(y))
        else:
            return lambda x: self.cls.Exists(y, pexp(x, y))

    @inline_args
    def object_min_cardinality(self, n, pexp, cexp):
        util.logging.debug('ignoring ObjectMinCardinality(...)')
        return self._object_cardinality_fallback(self.y, n, pexp, cexp)

    @inline_args
    def object_max_cardinality(self, n, pexp, cexp):
        util.logging.debug('ignoring ObjectMaxCardinality(...)')
        return self._object_cardinality_fallback(self.y, n, pexp, cexp)

    @inline_args
    def object_exact_cardinality(self, n, pexp, cexp):
        util.logging.debug('ignoring ObjectExactCardinality(...)')
        return self._object_cardinality_fallback(self.y, n, pexp, cexp)

    def data_some_values_from(self, args):
        dpexps, dran = args[:-1], args[-1]
        if len(dpexps) == 1:
            return self._object_some_values_from(self.dy, dpexps[0], dran)
        else:
            x = self.x
            ys = list(map((lambda i: self.cls.Variable(
                f'y{i}', self.dy.type)), range(1, len(dpexps) + 1)))
            lhs = util.starmap(
                (lambda p, y: (lambda x: p(x, y))), zip(dpexps, ys))
            rhs = self.cls.And(*map(lambda y: dran(y), ys))
            return (lambda x: self.cls.Exists(*ys, self.cls.And(
                *map(lambda f: f(x), lhs), rhs)))

    def data_all_values_from(self, args):
        dpexps, dran = args[:-1], args[-1]
        if len(dpexps) == 1:
            return self._object_all_values_from(self.dy, dpexps[0], dran)
        else:
            x = self.x
            ys = list(map((lambda i: self.cls.Variable(
                f'y{i}', self.dy.type)), range(1, len(dpexps) + 1)))
            lhs = util.starmap(
                (lambda p, y: (lambda x: p(x, y))), zip(dpexps, ys))
            rhs = self.cls.And(*map(lambda y: dran(y), ys))
            return (lambda x: self.cls.Forall(*ys, self.cls.Implies(
                *map(lambda f: f(x), lhs), rhs)))

    @inline_args
    def data_has_value(self, dpexp, lit):
        return lambda x: dpexp(x, lit)

    @inline_args
    def data_min_cardinality(self, n, dpexp, dran):
        util.logging.debug('ignoring DataMinCardinality(...)')
        return self._object_cardinality_fallback(self.dy, n, dpexp, dran)

    @inline_args
    def data_max_cardinality(self, n, dpexp, dran):
        util.logging.debug('ignoring DataMaxCardinality(...)')
        return self._object_cardinality_fallback(self.dy, n, dpexp, dran)

    @inline_args
    def data_exact_cardinality(self, n, dpexp, dran):
        util.logging.debug('ignoring DataExactCardinality(...)')
        return self._object_cardinality_fallback(self.dy, n, dpexp, dran)

    @inline_args
    def sub_class_of(self, annots, cexp1, cexp2):
        x = self.x
        return self.cls.NewAxiom(
            self._fresh_axiom_id('sub'),
            self.cls.Forall(x, self.cls.Implies(
                cexp1(x),
                cexp2(x))),
            **annots)

    @inline_args
    def equivalent_classes(self, annots, cexp1, cexp2, *cexps):
        x = self.x
        if not cexps:
            form = self.cls.Iff(cexp1(x), cexp2(x))
        else:
            form = self.cls.And(*util.starmap(
                lambda c1, c2: self.cls.Iff(c1(x), c2(x)),
                util.sliding_pairs_args(cexp1, cexp2, *cexps)))
        return self.cls.NewAxiom(
            self._fresh_axiom_id('equiv'),
            self.cls.Forall(x, form), **annots)

    def _disjoint_classes(self, *cexps):
        x = self.x
        if len(cexps) == 2:
            return self.cls.Implies(cexps[0](x), self.cls.Not(cexps[1](x)))
        else:
            return self.cls.And(*util.starmap(
                lambda c1, c2: self.cls.Implies(c1(x), self.cls.Not(c2(x))),
                util.combinations(cexps, 2)))
        return form

    @inline_args
    def disjoint_classes(self, annots, cexp1, cexp2, *cexps):
        x = self.x
        return self.cls.NewAxiom(
            self._fresh_axiom_id('disj'),
            self.cls.Forall(
                x, self._disjoint_classes(cexp1, cexp2, *cexps)),
            **annots)

    @inline_args
    def disjoint_union(self, annots, cls, cexp1, cexp2, *cexps):
        x = self.x
        return self.cls.NewAxiom(
            self._fresh_axiom_id('disj_union'),
            self.cls.Forall(x, self.cls.And(
                self.cls.Iff(
                    cls(x), self.object_union_of(cexp1, cexp2, *cexps)(x)),
                self._disjoint_classes(cexp1, cexp2, *cexps))),
            **annots)

    @inline_args
    def sub_object_property_of(self, annots, pexp1, pexp2):
        x, y, _ = self.xyz
        pexp1_xy = pexp1(x, y)
        ys = sorted(pexp1_xy.free_variables - {x, y})
        return self.cls.NewAxiom(
            self._fresh_axiom_id('sub'),
            self.cls.Forall(
                x, *ys, y, self.cls.Implies(
                    pexp1(x, y),
                    pexp2(x, y))),
            **annots)

    @inline_args
    def property_expression_chain(self, *pexps):
        ys = list(map((lambda i: self.cls.Variable(
            f'y{i}', self.y.type)), range(0, len(pexps) + 1)))
        return (lambda x, y: self.cls.And(
            *util.starmap(
                lambda yi, yj, p: p(yi, yj),
                zip(ys, ys[1:], pexps))).substitute(
                    {ys[0]: x, ys[-1]: y}))

    @inline_args
    def _equivalent_object_properties(self, y, pexp1, pexp2, *pexps):
        x = self.x
        if not pexps:
            form = self.cls.Iff(pexp1(x, y), pexp2(x, y))
        else:
            form = self.cls.And(*util.starmap(
                lambda p1, p2: self.cls.Iff(p1(x, y), p2(x, y)),
                util.sliding_pairs_args(pexp1, pexp2, *pexps)))
        return self.cls.Forall(x, y, form)

    @inline_args
    def equivalent_object_properties(self, annots, *pexps):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('equiv'),
            self._equivalent_object_properties(self.y, *pexps),
            **annots)

    def _disjoint_object_properties(self, y, pexp1, pexp2, *pexps):
        x = self.x
        if not pexps:
            form = self.cls.Implies(pexp1(x, y), self.cls.Not(pexp2(x, y)))
        else:
            form = self.cls.And(*util.starmap(
                lambda p1, p2: self.cls.Implies(
                    p1(x, y), self.cls.Not(p2(x, y))),
                util.combinations(util.chain([pexp1, pexp2], pexps), 2)))
        return self.cls.Forall(x, y, form)

    @inline_args
    def disjoint_object_properties(self, annots, *pexps):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('disj'),
            self._disjoint_object_properties(self.y, *pexps),
            **annots)

    @inline_args
    def inverse_object_properties(self, annots, pexp1, pexp2):
        x, y, _ = self.xyz
        return self.cls.NewAxiom(
            self._fresh_axiom_id('inv'),
            self.cls.Forall(x, y, self.cls.Implies(
                pexp1(x, y), pexp2(y, x))),
            **annots)

    @inline_args
    def _object_property_domain(self, y, pexp, cexp):
        x = self.x
        return self.cls.Forall(x, y, self.cls.Implies(pexp(x, y), cexp(x)))

    @inline_args
    def object_property_domain(self, annots, pexp, cexp):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('dom'),
            self._object_property_domain(self.y, pexp, cexp),
            **annots)

    def _object_property_range(self, y, pexp, cexp):
        x = self.x
        return self.cls.Forall(x, y, self.cls.Implies(pexp(x, y), cexp(y)))

    @inline_args
    def object_property_range(self, annots, pexp, cexp):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('ran'),
            self._object_property_range(self.y, pexp, cexp),
            **annots)

    def _functional_object_property(self, y, z, pexp):
        x = self.x
        return self.cls.Forall(x, y, z, self.cls.Implies(
            pexp(x, y), pexp(x, z), self.cls.Equal(y, z)))

    @inline_args
    def functional_object_property(self, annots, pexp):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('fun'),
            self._functional_object_property(self.y, self.z, pexp),
            **annots)

    @inline_args
    def inverse_functional_object_property(self, annots, pexp):
        x, y, z = self.xyz
        return self.cls.NewAxiom(
            self._fresh_axiom_id('inv_fun'),
            self.cls.Forall(x, y, z, self.cls.Implies(
                pexp(y, x), pexp(z, x), self.cls.Equal(y, z))),
            **annots)

    @inline_args
    def reflexive_object_property(self, annots, pexp):
        x = self.x
        return self.cls.NewAxiom(
            self._fresh_axiom_id('refl'),
            self.cls.Forall(x, pexp(x, x)), **annots)

    @inline_args
    def irreflexive_object_property(self, annots, pexp):
        x = self.x
        return self.cls.NewAxiom(
            self._fresh_axiom_id('irrefl'),
            self.cls.Forall(x, self.cls.Not(pexp(x, x))), **annots)

    @inline_args
    def symmetric_object_property(self, annots, pexp):
        x, y, _ = self.xyz
        return self.cls.NewAxiom(
            self._fresh_axiom_id('symm'),
            self.cls.Forall(x, y, self.cls.Implies(
                pexp(x, y),
                pexp(y, x))),
            **annots)

    @inline_args
    def asymmetric_object_property(self, annots, pexp):
        x, y, _ = self.xyz
        return self.cls.NewAxiom(
            self._fresh_axiom_id('asymm'),
            self.cls.Forall(x, y, self.cls.Implies(
                pexp(x, y),
                self.cls.Not(pexp(y, x)))),
            **annots)

    @inline_args
    def transitive_object_property(self, annots, pexp):
        x, y, z = self.xyz
        return self.cls.NewAxiom(
            self._fresh_axiom_id('trans'),
            self.cls.Forall(x, y, z, self.cls.Implies(
                pexp(x, y),
                pexp(y, z),
                pexp(x, z))),
            **annots)

    @inline_args
    def sub_data_property_of(self, annots, dpexp1, dpexp2):
        x, y = self.x, self.dy
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_sub'),
            self.cls.Forall(x, y, self.cls.Implies(
                dpexp1(x, y),
                dpexp2(x, y))),
            **annots)

    @inline_args
    def equivalent_data_properties(self, annots, *dpexps):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_equiv'),
            self._equivalent_object_properties(self.dy, *dpexps),
            **annots)

    @inline_args
    def disjoint_data_properties(self, annots, *dpexps):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_disj'),
            self._disjoint_object_properties(self.dy, *dpexps),
            **annots)

    @inline_args
    def data_property_domain(self, annots, dpexp, cexp):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_dom'),
            self._object_property_domain(self.dy, dpexp, cexp),
            **annots)

    @inline_args
    def data_property_range(self, annots, dpexp, dran):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_ran'),
            self._object_property_range(self.dy, dpexp, dran),
            **annots)

    @inline_args
    def functional_data_property(self, annots, dpexp):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_fun'),
            self._functional_object_property(self.dy, self.dz, dpexp),
            **annots)

    @inline_args
    def datatype_definition(self, annots, datatype, dran):
        x = self.dx
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_def'),
            self.cls.Forall(x, self.cls.Iff(datatype(x), dran(x))))

    def _has_key(self, x, y, z, zty, pexps, saved_vars):
        zs = list(map((lambda i: self.cls.Variable(
            f'{z}{i}', zty)), range(1, len(pexps) + 1)))
        saved_vars[z] = zs
        return util.chain(*util.starmap(  # flatten
            lambda p, z: (p(x, z), p(y, z)), zip(pexps, zs)))

    @inline_args
    def has_key(self, annots, cexp, pexps, dpexps):
        if not pexps and not dpexps:
            util.logging.debug('ignoring empty HasKey(...)')
            return self.discard()
        x, y, _ = self.xyz
        saved_vars = dict()
        form = self.cls.Implies(
            self.cls.And(
                cexp(x), cexp(y),
                *self._has_key(x, y, 'z', self.ity, pexps, saved_vars),
                *self._has_key(x, y, 'w', self.dty, dpexps, saved_vars)),
            self.cls.Equal(x, y))
        return self.cls.NewAxiom(
            self._fresh_axiom_id('has_key'),
            self.cls.Forall(
                x, y,
                *saved_vars.get('z', []),
                *saved_vars.get('w', []),
                form),
            **annots)

    def object_property_expression_has_key(self, args):
        return args

    def data_property_expression_has_key(self, args):
        return args

    @inline_args
    def same_individual(self, annots, *inds):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('same'),
            self.cls.Equal.eq(*inds),
            **annots)

    @inline_args
    def different_individuals(self, annots, *inds):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('diff'),
            self.cls.Equal.ne(*inds),
            **annots)

    @inline_args
    def class_assertion(self, annots, cexp, ind):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('class'),
            cexp(ind),
            **annots)

    @inline_args
    def object_property_assertion(self, annots, pexp, ind1, ind2):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('prop'),
            pexp(ind1, ind2),
            **annots)

    @inline_args
    def negative_object_property_assertion(self, annots, pexp, ind1, ind2):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('neg_prop'),
            self.cls.Not(pexp(ind1, ind2)),
            **annots)

    @inline_args
    def data_property_assertion(self, annots, dpexp, ind, lit):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('data_prop'),
            dpexp(ind, lit),
            **annots)

    @inline_args
    def negative_data_property_assertion(self, annots, dpexp, ind, lit):
        return self.cls.NewAxiom(
            self._fresh_axiom_id('neg_data_prop'),
            self.cls.Not(dpexp(ind, lit)),
            **annots)
