# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestRuleDerived(ULKB_TestCase):

    def test_rule_cut(self):
        p, q = Constants('p', 'q', bool)

        self.assertRaises(TypeError, RuleCut, 0, 0)
        self.assertRaises(TypeError, RuleCut, BoolType(), BoolType())
        self.assertRaises(TypeError, RuleCut, p, q)
        self.assertRaises(TypeError, RuleCut, p, q)

        seq = RuleCut(
            RuleAssume(q), RuleAssume(p), annotations={'i': 1, 'j': 2})
        self.assert_rule_cut(seq, ({p, q}, p), {'i': 1, 'j': 2})

        seq = RuleCut(
            RuleAssume(p), RuleAssume(p), annotations={'i': 1, 'j': 2})
        self.assert_rule_cut(seq, ({p}, p), {'i': 1, 'j': 2})

        seq = RuleCut(
            RuleTruth(), RuleAssume(Truth()), annotations={'i': 1, 'j': 2})
        self.assert_rule_cut(seq, (set(), Truth()), {'i': 1, 'j': 2})

        seq = RuleCut(
            RuleWeaken(q, RuleTruth()),
            RuleWeaken(p, RuleAssume(Truth())))
        self.assert_rule_cut(seq, ({p, q}, Truth()))

        self.assertTrue(seq.is_rule_cut())
        self.assertTrue(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertFalse(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_weaken(self):
        p, q = Constants('p', 'q', bool)

        self.assertRaises(TypeError, RuleWeaken, 0, 0)
        self.assertRaises(TypeError, RuleWeaken, BoolType(), BoolType())
        self.assertRaises(TypeError, RuleWeaken, p, q)
        self.assertRaises(TypeError, RuleWeaken, p, q)

        seq = RuleWeaken(q, RuleAssume(p), annotations={'i': 1, 'j': 2})
        self.assert_rule_weaken(seq, ({p, q}, p), {'i': 1, 'j': 2})

        seq = RuleWeaken(q, RuleTruth())
        self.assert_rule_weaken(seq, ({q}, Truth()))

        seq = RuleWeaken(Truth(), RuleTruth())
        self.assert_rule_weaken(seq, ({Truth()}, Truth()))

        seq = RuleWeaken(Truth(), RuleAssume(Truth()))
        self.assert_rule_weaken(seq, ({Truth()}, Truth()))

        self.assertTrue(seq.is_rule_cut())
        self.assertTrue(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertFalse(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_ap_term(self):
        x = Variable('x', bool)
        self.assertRaises(TypeError, RuleApTerm, 0, 0)
        self.assertRaises(
            TypeError, RuleApTerm, TypeVariable('a'), RuleRefl(x))
        self.assertRaises(TypeError, RuleApTerm, x, x)
        self.assertRaises(RuleError, RuleApTerm, x, RuleRefl(x))

        a = BaseType('a')
        f = Constant('f', FunctionType(a, a, a))
        k = Constant('k', a)
        x, y = Variables('x', 'y', a)

        seq = RuleApTerm(
            f(k), RuleAssume(Equal(x, y)), annotations={'i': 1, 'j': 2})
        self.assert_rule_ap_term(
            seq, ({Equal(x, y)}, Equal(f(k, x), f(k, y))),
            {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_ap_term())
        self.assertFalse(f(k).is_rule_ap_term())
        self.assertFalse(RuleAssume(x@bool).is_rule_ap_term())
        self.assertFalse(RuleRefl(x).is_rule_ap_term())

        seq = RuleApTerm(
            f(k), RuleAssume(Equal(x, y)), annotations={'i': 1, 'j': 2})
        self.assertTrue(seq.is_rule_cut())
        self.assertTrue(seq.is_rule_weaken())
        self.assertTrue(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_ap_thm(self):
        x = Variable('x', bool)
        self.assertRaises(TypeError, RuleApThm, 0, 0)
        self.assertRaises(
            TypeError, RuleApThm, TypeVariable('a'), x)
        self.assertRaises(
            TypeError, RuleApThm, RuleRefl(x >> x), RuleRefl(x))
        self.assertRaises(RuleError, RuleApThm, RuleRefl(x), x)

        a = BaseType('a')
        f = Constant('f', FunctionType(a, a, a))
        g = Constant('g', FunctionType(a, a))
        k = Constant('k', a)
        x, y = Variables('x', 'y', a)

        seq = RuleApThm(
            RuleAssume(Equal(f(k), g)), x, annotations={'i': 1, 'j': 2})
        self.assert_rule_ap_thm(
            seq, ({Equal(f(k), g)}, Equal(f(k, x), g(x))),
            {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_ap_thm())
        self.assertFalse(f(k).is_rule_ap_thm())
        self.assertFalse(RuleAssume(x@bool).is_rule_ap_thm())
        self.assertFalse(RuleRefl(x).is_rule_ap_thm())

        seq = RuleApThm(
            RuleAssume(Equal(f(k), g)), x, annotations={'i': 1, 'j': 2})
        self.assertTrue(seq.is_rule_cut())
        self.assertTrue(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertTrue(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_sym(self):
        x = Variable('x', bool)
        self.assertRaises(TypeError, RuleSym, 0, 0)
        self.assertRaises(TypeError, RuleSym, TypeVariable('a'), x)
        self.assertRaises(TypeError, RuleSym, x)
        self.assertRaisesRegex(
            RuleError, 'not an equation', RuleSym, RuleAssume(x))

        a = BaseType('a')
        x, y = Variables('x', 'y', a)

        seq = RuleSym(RuleAssume(Equal(x, y)), annotations={'i': 1, 'j': 2})
        self.assert_rule_sym(
            seq, ({Equal(x, y)}, Equal(y, x)), {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_sym())
        self.assertFalse(RuleAssume(x@bool).is_rule_sym())

        seq = RuleSym(RuleAssume(Equal(x, y)), annotations={'i': 1, 'j': 2})
        self.assertTrue(seq.is_rule_cut())
        self.assertTrue(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_alpha(self):
        x = Variable('x', bool)
        self.assertRaises(TypeError, RuleAlpha, 0, 0)
        self.assertRaises(TypeError, RuleAlpha, TypeVariable('a'), x)
        self.assertRaises(TypeError, RuleAlpha, x, RuleRefl(x))

        a = BaseType('a')
        x, y = Variables('x', 'y', a)
        f = Constant('f', a >> a)

        seq = RuleAlpha(x >> f(x), y >> f(y), annotations={'i': 1, 'j': 2})
        self.assert_rule_alpha(
            seq, (set(), Equal(x >> f(x), y >> f(y))), {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_alpha())
        self.assertTrue(RuleRefl(x).is_rule_alpha())
        self.assertFalse(RuleAssume(Equal(x, y)).is_rule_alpha())
        self.assertFalse(RuleAssume(Equal(x >> x, y >> y)).is_rule_alpha())

        seq = RuleAlpha(x >> f(x), y >> f(y), annotations={'i': 1, 'j': 2})
        self.assertTrue(seq.is_rule_cut())
        self.assertFalse(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertTrue(seq.is_rule_alpha())
        self.assertTrue(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_alpha_rename(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleAlpha, 0, 0)
        self.assertRaises(
            TypeError, RuleAlphaRename, Constant('a', bool), x >> x)
        self.assertRaises(TypeError, RuleAlphaRename, x, x)
        self.assertRaisesRegex(
            RuleError, "occurs free in", RuleAlphaRename, y, x >> y)

        a = BaseType('a')
        x, y, z, v = Variables('x', 'y', 'z', 'v', a)
        f = Constant('f', FunctionType(a, a, a))

        t = x >> f(z, f(x, y))
        seq = RuleAlphaRename(x, t, annotations={'i': 1, 'j': 2})
        self.assert_rule_alpha_rename(
            seq, (set(), Equal(t, t)), {'i': 1, 'j': 2})

        t = (x, y) >> f(z, f(x, y))
        seq = RuleAlphaRename(v, t, annotations={'i': 1, 'j': 2})
        self.assert_rule_alpha_rename(
            seq, (set(), Equal(t, (v, y) >> f(z, f(v, y)))),
            {'i': 1, 'j': 2})

        t = (x, y) >> f(z, f(x, y))
        y1 = Variable("y'", y.type)
        seq = RuleAlphaRename(y, t, annotations={'i': 1, 'j': 2})
        self.assert_rule_alpha_rename(
            seq, (set(), Equal(t, (y, y1) >> f(z, f(y, y1)))),
            {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_alpha_rename())
        self.assertFalse(RuleAssume(x@bool).is_rule_alpha_rename())
        self.assertFalse(RuleRefl(x).is_rule_alpha_rename())
        self.assertTrue(RuleRefl(x >> x).is_rule_alpha_rename())

        t1 = x >> f(x, y)
        t2 = Abstraction(y, t1[1], _open=False)
        seq = RuleAlpha(t1, t2)
        self.assertTrue(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())

        seq = RuleAlphaRename(y, t, annotations={'i': 1, 'j': 2})
        self.assertTrue(seq.is_rule_cut())
        self.assertFalse(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertTrue(seq.is_rule_alpha())
        self.assertTrue(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_truth(self):
        seq = RuleTruth(annotations={'i': 1, 'j': 2})
        self.assert_rule_truth(seq, (set(), Truth()), {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_cut())
        self.assertFalse(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertFalse(seq.is_rule_sym())
        self.assertFalse(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertTrue(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_eq_truth_intro(self):
        a = BaseType('a')
        x = Variable('x', a)
        f = Constant('f', FunctionType(a, bool))

        self.assertRaises(TypeError, RuleEqTruthIntro, 0)
        self.assertRaises(TypeError, RuleEqTruthIntro, f(x))

        seq = RuleEqTruthIntro(RuleAssume(f(x)), annotations={'i': 1, 'j': 2})
        self.assert_rule_eq_truth_intro(
            seq, ({f(x)}, Iff(f(x), Truth())), {'i': 1, 'j': 2})

        seq = RuleEqTruthIntro(RuleAssume(Truth()))
        self.assert_rule_eq_truth_intro(
            seq, ({Truth()}, Iff(Truth(), Truth())))

        seq = RuleEqTruthIntro(RuleTruth())
        self.assert_rule_eq_truth_intro(
            seq, (set(), Iff(Truth(), Truth())))

        self.assertTrue(seq.is_rule_cut())
        self.assertFalse(seq.is_rule_weaken())
        self.assertFalse(seq.is_rule_ap_term())
        self.assertFalse(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertTrue(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertTrue(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())

    def test_rule_eq_truth_elim(self):
        a = BaseType('a')
        x = Variable('x', a)
        f = Constant('f', FunctionType(a, bool))

        self.assertRaises(TypeError, RuleEqTruthElim, 0)
        self.assertRaises(TypeError, RuleEqTruthElim, f(x))
        self.assertRaises(RuleError, RuleEqTruthElim, RuleAssume(f(x)))
        self.assertRaises(RuleError, RuleEqTruthElim, RuleRefl(f(x)))
        self.assertRaises(
            RuleError, RuleEqTruthElim, RuleAssume(Iff(Truth(), f(x))))

        seq = RuleEqTruthElim(
            RuleAssume(Iff(f(x), Truth())),
            annotations={'i': 1, 'j': 2})
        self.assert_rule_eq_truth_elim(
            seq, ({Iff(f(x), Truth())}, f(x)), {'i': 1, 'j': 2})

        seq = RuleEqTruthElim(
            RuleEqTruthIntro(RuleRefl(f(x))), annotations={'i': 1, 'j': 2})
        self.assert_rule_eq_truth_elim(
            seq, (set(), Equal(f(x), f(x))), {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_cut())
        self.assertFalse(seq.is_rule_weaken())
        self.assertTrue(seq.is_rule_ap_term())
        self.assertTrue(seq.is_rule_ap_thm())
        self.assertTrue(seq.is_rule_sym())
        self.assertTrue(seq.is_rule_alpha())
        self.assertFalse(seq.is_rule_alpha_rename())
        self.assertFalse(seq.is_rule_truth())
        self.assertFalse(seq.is_rule_eq_truth_intro())
        self.assertTrue(seq.is_rule_eq_truth_elim())


if __name__ == '__main__':
    main()
