from itertools import product
from collections import defaultdict
from typing import Dict

from zerkel.core import (
    Set, Node, EmptySet, Identity, UnionPlus, IfThenElse, In, 
    Projection, Composition, Recursion
)
from zerkel.interpreter import interpret

from zerkel.generation.enumeration import blacklist


LEFT_RIGHT = "LEFT_RIGHT"
NO_LEFT = "NO_LEFT"
NO_LEFT_NOR_RIGHT = "NO_LEFT_NOR_RIGHT"


ALLOW_COMPOSITION = True
NO_COMPOSITION = False

USE_IN_OPERATOR = True
USE_IF_THEN_ELSE = False

ALLOW_IN_OPERATOR = True
NO_IN_OPERATOR = False


_constant_cache: Dict[Set, Node] = {Set(): EmptySet()}


def cache_generation(callback):
    _cache = {}
    def wrapper(self, *args, **kwargs):
        key = (self.use_in_operator, *args, *kwargs.items())
        try:
            return _cache[key]
        except KeyError:
            r = tuple(callback(self, *args, **kwargs))
            _cache[key] = r
            return r
    return wrapper


def enumeration(size, use_in_operator: bool = USE_IN_OPERATOR):
    return {(s, a): {str(p): '' for p in generate(s, a, use_in_operator)} 
            for s in range(size) for a in range(s + 4)}


class generate:
    def __init__(self, size: int, arity: int, 
                 use_in_operator: bool = USE_IN_OPERATOR):
        self.size = size
        self.arity = arity
        self.use_in_operator = use_in_operator
    
    def __iter__(self):
        yield from self.generate(self.size, self.arity)
    
    @cache_generation
    def generate(self, size: int, arity: int,
                lr: str = NO_LEFT_NOR_RIGHT, c: bool = ALLOW_COMPOSITION,
                in_op: bool = ALLOW_IN_OPERATOR):
        t = max(1, arity - 3)
        if size < t:
            return
        if size == 1:
            if arity == 0:
                yield EmptySet()
            if arity == 1:
                yield Identity()
            if arity == 2:
                yield UnionPlus()
            if arity == 4 and not self.use_in_operator:
                yield IfThenElse()
        elif size > 1:
            if self.use_in_operator and in_op and arity > 1 and size > 3:
                yield from self.generate_in_operator(arity, size)
            if lr == LEFT_RIGHT:
                yield from self.generate_left_right(arity, size)
            elif lr == NO_LEFT:
                yield from self.generate_right(arity, size)
            if arity > 0:
                yield from self.generate_recursion(arity, size)
            if c:
                yield from self.generate_composition(arity, size)
        
    def generate_in_operator(self, arity, size):
        for f_size in range(1, size - 1):
            for f in self.generate(f_size, arity, LEFT_RIGHT, in_op=False):
                for g in self.generate(size - f_size - 1, arity, LEFT_RIGHT, in_op=False):
                    if not _in_constructor_can_be_simplified(f, g):
                        yield In(f, g)


    def generate_left_right(self, arity, size):
        for n in range(1, min(arity + 1, size)):
            for f in self.generate(size - n, arity - n, NO_LEFT_NOR_RIGHT):
                if n == arity:
                    yield Projection(f, n, 0)
                else:
                    for r in range(n + 1):
                        yield Projection(f, n - r, r)


    def generate_right(self, arity, size):
        for r in range(1, min(arity, size)):
            for f in self.generate(size - r, arity - r, NO_LEFT_NOR_RIGHT):
                yield Projection(f, 0, r)


    def generate_recursion(self, arity, size):
        if arity > 1:
            lr = NO_LEFT_NOR_RIGHT
        else:
            lr = NO_LEFT
        for g in self.generate(size - 1, arity + 1, lr):
            p = Recursion(g)
            if p not in blacklist:
                yield p


    def generate_composition(self, arity, size):
        t = max(1, arity - 3)
        for f_size in range(1, size - t):
            g_size = size - f_size - 1
            max_arity = min(f_size + 3, g_size // t + 1)
            for f_arity in range(1 + (f_size == 1), max_arity + 1):
                f_programs = tuple(self.generate(f_size, f_arity, NO_LEFT_NOR_RIGHT))
                if f_programs:
                    for r in stars_and_bars(g_size - f_arity * t, f_arity, t):
                        p = (self.generate(l, arity, LEFT_RIGHT) for l in r)
                        for compounds in product(*p):
                            if _compounds_can_be_simplified(compounds):
                                continue
                            for f in f_programs:
                                p = Composition(f, *compounds)
                                if _composition_can_be_simplified(p):
                                    continue
                                if p.arity > 0:
                                    yield p
                                else:
                                    yield from cache_constant(p)


def _in_constructor_can_be_simplified(p, q):
    if p == q:
        return True
    if p in blacklist or q in blacklist:
        return True
    if isinstance(p, Projection) and isinstance(q, Projection) and p.left > 0 and q.left > 0 and p.arity > 2:
        return True
    return False


def _compounds_can_be_simplified(compounds):
    if len(compounds) == 1 and isinstance(compounds[0], Identity):
        return True
    if len(compounds) == 1 and isinstance(compounds[0], Composition):
        return True
    if all(isinstance(c, Projection) for c in compounds):
        contains_left = all(c.left > 0 or c.f.arity == 0 for c in compounds)
        contains_right = all(c.right > 0  or c.f.arity == 0 for c in compounds)
        return contains_left or contains_right
    return False


def _composition_can_be_simplified(p):
    if p in blacklist:
        return True
    if isinstance(p.f, IfThenElse) and (p.g[0] == p.g[1] or p.g[2] == p.g[3]):
        return True
    if p.f == Recursion(IfThenElse()) and ((isinstance(p.g[0], Projection) and p.g[0].f == EmptySet()) or p.g[1] == p.g[2]):
        return True
    if isinstance(p.f, In) and all(c.arity == 0 for c in p.g[-2:]):
        return True
    return False


def cache_constant(p):
    r = interpret(p)
    try:
        if p.size < _constant_cache[r].size:
            _constant_cache[r] = p
            yield p
        elif p == _constant_cache[r]:
            yield p
    except KeyError:
        _constant_cache[r] = p
        yield p


def stars_and_bars(v, n, t):
    """
    Distribute v bonus points over n parts with an initial value of t.

    :example:

    >>> tuple(s(4, 2, 9))
    ([9, 13], [10, 12], [11, 11], [12, 10], [13, 9])
    >>> tuple(s(3, 3, 2))
    ([2, 2, 5], [2, 3, 4], [2, 4, 3], [2, 5, 2], [3, 2, 4], [3, 3, 3],
    [3, 4, 2], [4, 2, 3], [4, 3, 2], [5, 2, 2])

    :param v: the number of bonus points for all parts
    :param n: the number of parts
    :param t: the default number of point of a part
    :return: an iterable of list of n values, such as the i th value
    represents the number of points attributed to the i th part.
    """
    if n == 1:
        yield [v + t]
    else:
        for u in range(v + 1):
            for r in stars_and_bars(v - u, n - 1, t):
                yield [t + u] + r
