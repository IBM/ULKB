# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .test_serializer_ulkb import TestSerializerULKB
from .tests import main


class TestSerializerULKB_Abstraction(TestSerializerULKB):

    def test_defaults(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        ha2 = Variable('h', FunctionType(a, a, bool))
        self.assert_to_ulkb(
            (Abstraction(x, y),
             '(𝜆 (x : 𝔹) ⇒ (y : 𝔹)) : 𝔹 → 𝔹'),
            (Abstraction(x@a, y@a, type=FunctionType(a, a)),
             '(𝜆 (x : a) ⇒ (y : a)) : a → a'),
            (Abstraction(x, x, y),
             '(𝜆 (x : 𝔹) (x : 𝔹) ⇒ (y : 𝔹)) : 𝔹 → 𝔹 → 𝔹'),
            ((f@FunctionType(FunctionType(bool, bool, bool), bool))(
                Abstraction(x, x, y)), '\
(f : (𝔹 → 𝔹 → 𝔹) → 𝔹) (𝜆 (x : 𝔹) (x : 𝔹) ⇒ (y : 𝔹)) : 𝔹'),
            (ha2(Abstraction(x, f(x)), Abstraction(x, x)), '\
(h : (𝔹 → 𝔹) → (𝔹 → 𝔹) → 𝔹) \
(𝜆 (x : 𝔹) ⇒ (f : 𝔹 → 𝔹) (x : 𝔹)) \
(𝜆 (x : 𝔹) ⇒ (x : 𝔹)) : 𝔹'),
            (Abstraction(x, x, f(y)), '\
(𝜆 (x : 𝔹) (x : 𝔹) ⇒ (f : 𝔹 → 𝔹) (y : 𝔹)) : 𝔹 → 𝔹 → 𝔹'),
            (Abstraction(x, y, Abstraction(x, x, y)), '\
(𝜆 (x : 𝔹) (y : 𝔹) (x : 𝔹) (x : 𝔹) ⇒ (y : 𝔹)) : 𝔹 → 𝔹 → 𝔹 → 𝔹 → 𝔹'),
            (ha(Abstraction(x, y, Abstraction(x, x, y))), '\
(h : (𝔹 → 𝔹 → 𝔹 → 𝔹 → 𝔹) → 𝔹) \
(𝜆 (x : 𝔹) (y : 𝔹) (x : 𝔹) (x : 𝔹) ⇒ (y : 𝔹)) : 𝔹'),
            (Abstraction(x, y, Abstraction(x, x, y))(x), '\
(𝜆 (x : 𝔹) (y : 𝔹) (x : 𝔹) (x : 𝔹) ⇒ (y : 𝔹)) (x : 𝔹) : 𝔹 → 𝔹 → 𝔹 → 𝔹'))

    def test_ensure_ascii(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        ha2 = Variable('h', FunctionType(a, a, bool))
        self.assert_to_ulkb(
            (Abstraction(x, y),
             '(fun (x : bool) => (y : bool)) : bool -> bool'),
            (Abstraction(Variable('𝛼', a), y),
             '(fun (\\U0001d6fc : a) => (y : bool)) : a -> bool'),
            ensure_ascii=True
        )

    def test_show_annotations(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        ha2 = Variable('h', FunctionType(a, a, bool))
        x, y, z = Variables('x', 'y', 'z', bool)

        self.assert_to_ulkb(
            (Abstraction(x@{'i': 1}, y@{'j': 2}, k=3),
             '(𝜆 (x {i=1} : 𝔹) ⇒ (y {j=2} : 𝔹)) {k=3} : 𝔹 → 𝔹'),
            (Abstraction(x@{'i': 1}, y@{'j': 2}, z, k=3),
             '(𝜆 (x {i=1} : 𝔹) (y {j=2} : 𝔹) ⇒ (z : 𝔹)) {k=3} : 𝔹 → 𝔹 → 𝔹'),
            (Abstraction(x, Abstraction(y, z, k=3)),
             '(𝜆 (x : 𝔹) ⇒ ((𝜆 (y : 𝔹) ⇒ (z : 𝔹)) {k=3})) : 𝔹 → 𝔹 → 𝔹'),
            (Abstraction(x@{'i': 1}, Abstraction(y@{'j': 2}, z, k=3)), '\
(𝜆 (x {i=1} : 𝔹) ⇒ ((𝜆 (y {j=2} : 𝔹) ⇒ (z : 𝔹)) {k=3})) : 𝔹 → 𝔹 → 𝔹'),
            show_annotations=True)

        self.assert_to_ulkb(
            (Abstraction(x, y),
             '(𝜆 x ⇒ y) : 𝔹 → 𝔹'),
            omit_types=True)

        self.assert_to_ulkb(
            (Abstraction(
                x@{'i': 1}, y@{'i': 1, 'j': {'i': 1, 'j': 2}},
                k="a'b'c"), "\
(𝜆 (x {i=1} : 𝔹) ⇒ (y {i=1, j={'i': 1, 'j': 2}} : 𝔹)) {k='a\\'b\\'c'} \
: 𝔹 → 𝔹"),
            show_annotations=True)

    def test_show_parentheses(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        ha2 = Variable('h', FunctionType(a, a, bool))
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        self.assert_to_ulkb(
            (Abstraction(x, y),
             '(𝜆 x ⇒ y) : 𝔹 → 𝔹'),
            (Abstraction(x, x, y),
             '(𝜆 x ⇒ (𝜆 x ⇒ y)) : 𝔹 → (𝔹 → 𝔹)'),
            (Abstraction(x, x, y, f(y)), '\
(𝜆 x ⇒ (𝜆 x ⇒ (𝜆 y ⇒ (f y)))) : 𝔹 → (𝔹 → (𝔹 → 𝔹))'),
            show_parentheses=True,
            show_types=False)

    def test_show_types(self):
        a = TypeVariable('a')
        c = TypeConstructor('c', 1)
        x, y = Variables('x', 'y', bool)
        f = Constant('f', FunctionType(bool, bool))
        g = Constant('g', FunctionType(bool, bool, bool))
        ha = Variable('h', FunctionType(a, bool))
        ha2 = Variable('h', FunctionType(a, a, bool))
        self.assert_to_ulkb(
            (Abstraction(x@a, x@a, y@a),
             '(𝜆 x x ⇒ y) : a → a → a'),
            show_types=False)

        self.assert_to_ulkb(
            (Abstraction(x@a, x@a, y@a),
             '(𝜆 x ⇒ (𝜆 x ⇒ y)) : a → (a → a)'),
            show_types=False, show_parentheses=True)

        self.assert_to_ulkb(
            (Abstraction(x, x@a, y),
             '(𝜆 (x : 𝔹) (x : a) ⇒ (y : 𝔹)) : 𝔹 → a → 𝔹'),
            show_types=True)

    def test_misc(self):
        a = TypeVariable('a')
        f = Constant('f', a >> a)
        g = Constant('g', (a, a) >> a)
        x, y, z, w = Variables('x', 'y', 'z', 'w', a)
        t = Abstraction(x, y, g(y, i=1)(x), j=2)
        self.assert_to_ulkb(
            (t, '\
(𝜆 (x : a) (y : a) ⇒ (g : a → a → a) (y : a) (x : a)) : a → a → a'))

        self.assert_to_ulkb(
            (t, '\
(𝜆 (x : a) (y : a) ⇒ ((g : a → a → a) (y : a) {i=1}) (x : a)) {j=2} \
: a → a → a'),
            show_annotations=True)

        self.assert_to_ulkb(
            (t, '\
(fun (x : a) (y : a) => ((g : a -> a -> a) (y : a) {i=1}) (x : a)) {j=2} \
: a -> a -> a'),
            ensure_ascii=True, show_annotations=True)

        self.assert_to_ulkb(
            (t, '\
(𝜆 (x : a) ⇒ (𝜆 (y : a) ⇒ (((g : a → (a → a)) \
(y : a) {i=1}) (x : a)))) {j=2} : a → (a → a)'),
            omit_parentheses=False, show_annotations=True)

        self.assert_to_ulkb(
            (t,
             '(𝜆 x y ⇒ (g y {i=1}) x) {j=2} : a → a → a'),
            omit_types=True, show_annotations=True,)

        self.assert_to_ulkb(
            (t, '\
(𝜆 (x : a) (y : a) ⇒ (g : a → a → a) (y : a) (x : a)) : a → a → a'),
            omit_annotations=True,)

        self.assert_to_ulkb(
            (t,
             '(𝜆 x y ⇒ g y x) : a → a → a'),
            omit_types=True, omit_annotations=True)

        self.assert_to_ulkb(
            (Abstraction(x, x),
             '(𝜆 x ⇒ x) : a → a'),
            (Abstraction(x, f(x)),
             '(𝜆 x ⇒ f x) : a → a'),
            (Abstraction(x, y, g(x, g(y, x))),
             '(𝜆 x y ⇒ g x (g y x)) : a → a → a'),
            (Abstraction(x, y, g(g(x, y), x)),
             '(𝜆 x y ⇒ g (g x y) x) : a → a → a'),
            (Abstraction(x, Abstraction(y, g(x, y))(x)),
             '(𝜆 x ⇒ (𝜆 y ⇒ g x y) x) : a → a'),
            omit_types=True, show_annotations=False)


if __name__ == '__main__':
    main()
