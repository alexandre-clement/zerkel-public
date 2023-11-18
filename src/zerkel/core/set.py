from typing import Set as _Set, Dict, Tuple
import random

from pyparsing import (
    Literal, Word, ZeroOrMore, Forward,
    nums, oneOf, Group, ParseException, Optional
)



def boxify(lines, rows=None, columns=None):
    size = columns or max(map(len, lines))
    return ["╔" + "═" * (size + 2) + "╗"] + ["║ " + l + " " * (size - len(l)) + " ║" for l in lines] + ["╚" + "═" * (size + 2) + "╝"]


def _syntax():
    op = Literal(',').suppress()
    left_bracket = Literal('{').suppress()
    right_bracket = Literal('}').suppress()
    ordinal = Word(nums)
    ordinal.addParseAction(lambda tokens: Set.generate_ordinal(int(tokens[0])))
    non_ordinal = Word(nums)
    non_ordinal.setParseAction(lambda tokens: Set.generate(int(tokens[0])))
    lt = Literal('<').suppress()
    gt = Literal('>').suppress()
    non_ordinal = lt + non_ordinal + gt
    element = ordinal ^ non_ordinal
    expr = Forward()
    group = Group(left_bracket + Optional(expr) + right_bracket)
    group.addParseAction(lambda tokens: Set(*tokens[0]))
    left_parenthesis = Literal('(').suppress()
    right_parenthesis = Literal(')').suppress()
    atom = Forward()
    tuple = Group(left_parenthesis + atom + op + expr + right_parenthesis)
    tuple.addParseAction(lambda tokens: Set.generate_tuple(*tokens[0]))
    atom << (element | group | tuple)
    expr << (atom + ZeroOrMore(op + atom))
    return expr


class SetParsingException(Exception):
    def __init__(self, text, col):
        self.text = text
        self.col = col - 1

    def __str__(self):
        return f'Invalid expression :\n{self.text}\n' + ' ' * self.col + '^'


NOT_COMPUTED_YET = 'NOT COMPUTED YET'


class Set:
    __slots__ = [
        "elements", "_cardinal", "_rank", "_size", "_ordinal", "_hash",
        "_is_singleton", "_is_transitive", "_is_tuple", "_value"
    ]
    
    syntax = _syntax()
    cache: Dict[frozenset, 'Set'] = {}
    
    @classmethod
    def clear_cache(cls):
        cls.cache.clear()

    def __new__(cls, *elements):
        key = frozenset(elements)
        try:
            return cls.cache[key]
        except KeyError:
            instance = object.__new__(cls)
            cls.cache[key] = instance
            instance.elements = key
            instance.init()
            return instance

    def __init__(self, *elements):
        pass

    def init(self):
        self._cardinal = NOT_COMPUTED_YET
        self._rank = NOT_COMPUTED_YET
        self._size = NOT_COMPUTED_YET
        self._ordinal = NOT_COMPUTED_YET
        self._is_singleton = NOT_COMPUTED_YET
        self._is_transitive = NOT_COMPUTED_YET
        self._is_tuple = NOT_COMPUTED_YET
        self._hash = NOT_COMPUTED_YET
        self._value = NOT_COMPUTED_YET

    @property
    def cardinal(self):
        if self._cardinal is NOT_COMPUTED_YET:
            self._cardinal = len(self.elements)
        return self._cardinal

    @property
    def rank(self):
        if self._rank is NOT_COMPUTED_YET:
            if self.elements:
                self._rank = max(element.rank for element in self.elements) + 1
            else:
                self._rank = 0
        return self._rank

    @property
    def size(self):
        if self._size is NOT_COMPUTED_YET:
            self._size = 1 + sum(u.size for u in self.elements)
        return self._size

    @property
    def ordinal(self):
        if self._ordinal is NOT_COMPUTED_YET:
            n = len(self.elements)
            ords = set(range(n))
            for element in self.elements:
                ords.discard(element.ordinal)
            self._ordinal = n if not ords else None
        return self._ordinal
    
    @property
    def is_singleton(self):
        if self._is_singleton is NOT_COMPUTED_YET:
            self._is_singleton = len(self) == 1
        return self._is_singleton
    
    @property
    def is_transitive(self):
        if self._is_transitive is NOT_COMPUTED_YET:
            self._is_transitive = True
            if self.elements:
                for element in self.elements:
                    if not self.is_upset(element):
                        self._is_transitive = False
        return self._is_transitive

    @property
    def is_tuple(self):
        if self._is_tuple is NOT_COMPUTED_YET:
            if self.is_singleton:
                x, *_ = self
                self._is_tuple = x.is_singleton
            elif len(self) != 2:
                self._is_tuple = False
            else:
                a, b = sorted(self, key=len)
                if len(a) > 0 and len(b) > 0 and len(a) + len(b) == 3:
                    x, y, z = *a, *b
                    self._is_tuple = x == y or x == z
                else:
                    self._is_tuple = False
        return self._is_tuple
    
    @property
    def value(self):
        if self._value is NOT_COMPUTED_YET:
            self._value = sum(2**e.value for e in self)
        return self._value

    def contains(self, other: 'Set') -> bool:
        return other in self.elements
    
    def is_subset(self, other: 'Set') -> bool:
        return all(e in other for e in self)

    def is_upset(self, other: 'Set') -> bool:
        return all(e in self for e in other)

    def __iter__(self):
        yield from self.elements

    def __len__(self):
        return self.cardinal

    def __lt__(self, other):
        if self.rank == other.rank:
            s, o = sorted(self, reverse=True), sorted(other, reverse=True)
            for a, b in zip(s, o):
                if a != b:
                    return a < b
            if len(self) != len(other):
                return len(self) < len(other)
        return self.rank < other.rank

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Set):
            return False
        if self.ordinal is not None and self.ordinal == other.ordinal:
            return True
        return self.elements == other.elements

    def __hash__(self):
        if self._hash is NOT_COMPUTED_YET:
            self._hash = hash(self.elements)
        return self._hash

    def to_string(self, format_ordinal=False, format_tuple=False):
        if format_ordinal and self.ordinal is not None:
            return self.as_ordinal()
        if format_tuple and self.is_tuple:
            return self.as_tuple()
        if not self.elements:
            return '{}'
        return str(set(self.elements))

    def __str__(self):
        return self.to_string(format_ordinal=True)

    def as_ordinal(self):
        return str(self.ordinal)

    def as_tuple(self):
        return str(self._as_tuple())

    def _build_tree(self):
        this = '.' if self.ordinal is None else str(self.ordinal)
        if len(self) == 0:
            return ([this], len(this))
        elif len(self) == 1:
            x, *_ = [u._build_tree() for u in self]
            b, s = x
            size = max(len(this), s)
            this = this.center(size)
            mid = '║'.center(size)
            b = [u.center(size) for u in b]
            return ([this, mid, *b], size)
        children = [u._build_tree() for u in sorted(self)]
        x, *y = children
        size = max(len(this), sum(u[1] for u in children) + len(y))
        middle = size // 2
        this = this.center(size)
        body, length = x
        links = ' ' * (length // 2) + '╔'
        roots = []
        for b, s in y:
            length += 1
            roots.append(length + s // 2)
            for i in range(len(body)):
                body[i] += ' '
            body += [' ' * length for _ in range(len(b) - len(body))]
            b += [' ' * s for _ in range(len(body) - len(b))]
            for i, l in enumerate(b):
                body[i] += l
            length += s
        for i, r in enumerate(roots):
            if len(links) <= middle and r > middle:
                links += '═' * (middle - len(links)) + '╩' + '═' * (r - middle - 1)
            else:
                links += '═' * (r - len(links))
            if r == middle:
                links += '╬'
            elif i < len(roots) - 1:
                links += '╦'
            else:
                links += '╗'
        links += ' ' * (size - len(links))
        body = [u.center(size) for u in body]
        return ([this, links, *body], size)
    
    def as_tree(self):
        return '\n'.join(boxify(self._build_tree()[0]))
    
    def _as_tuple(self):
        if len(self) == 1:
            x, *_ = self
            x, *_ = x
            if x.is_tuple:
                return (x._as_tuple(), *x._as_tuple())
            return (x, x)
        a, b = sorted(self, key=len)
        x, y, z = *a, *b
        if x == y:
            y = z
        if y.is_tuple and not y.is_singleton:
            return (x, *y._as_tuple())
        return (x, y)

    __repr__ = __str__

    @classmethod
    def generate(cls, n: int):
        elt = [cls.generate(i) for i in range(n.bit_length()) if n & (1 << i)]
        return Set(*elt)
    
    @classmethod
    def generate_all(cls, n: int):
        for i in range(n):
            yield Set.generate(i)
    
    @classmethod
    def generate_range(cls, start, end: int, step: int = 1):
        for i in range(start, end, step):
            yield Set.generate(i)
            
    @classmethod
    def generate_ordinal(cls, ordinal: int):
        result = Set()
        for i in range(ordinal):
            result = Set(*result, result)
        return result

    @classmethod
    def generate_from_base(cls, depth: int, base: 'Set'):
        if depth <= 0:
            return base
        return cls(base, cls.generate_from_base(depth - 1, base))

    @classmethod
    def generate_rank(cls, rank: int):
        for i in cls.values_of_trees_of_heigh_n(rank):
            yield Set.generate(i)

    @classmethod
    def generate_tuple(cls, x, y, *args):
        if args:
            return Set(Set(x), Set(x, cls.generate_tuple(y, *args)))
        if x == y:
            return Set(Set(x))
        return Set(Set(x), Set(x, y))

    @classmethod
    def generate_singleton(cls, depth: int):
        if depth <= 0:
            return Set()
        return Set(cls.generate_singleton(depth - 1))

    @classmethod
    def generate_complete(cls, rank: int):
        return Set(*cls.generate_all(cls.number_of_trees_of_heigh_less_than_n(rank)))
    
    @classmethod
    def generate_random(cls, rank: int):
        result = cls._build_number_of_rooted_identity_trees_of_height_n(rank)
        a, b = sum(result[:-1]), sum(result)
        value = random.randrange(a, b)
        return Set.generate(value)

    @classmethod
    def generate_transitive(cls, n: int):
        g = cls._generate_transitive_id()
        for _ in range(n):
            yield cls.generate(next(g))

    @staticmethod
    def _generate_transitive_id():
        i = 0
        while True:
            yield i
            i += 1
            for j in range(i.bit_length()-1, 0, -1):
                if i & (1 << j):
                    i |= j

    @classmethod
    def parse(cls, text: str):
        try:
            return cls.syntax.parseString(text)[0]
        except ParseException as e:
            raise SetParsingException(text, e.col)
    
    @staticmethod
    def _build_number_of_rooted_identity_trees_of_height_n(n):
        result = [1]
        total = 1
        for i in range(n):
            temp = 2 ** total - total
            result.append(temp)
            total += temp
        return result
    
    @classmethod
    def values_of_trees_between_height_a_and_b(cls, a, b):
        a038081 = cls._build_number_of_rooted_identity_trees_of_height_n(b)
        yield from range(sum(a038081[:a]), sum(a038081))
    
    @classmethod
    def values_of_trees_of_heigh_n(cls, n):
        a038081 = cls._build_number_of_rooted_identity_trees_of_height_n(n)
        yield from range(sum(a038081[:-1]), sum(a038081))
    
    @classmethod
    def number_of_trees_of_heigh_n(cls, n):
        return cls._build_number_of_rooted_identity_trees_of_height_n(n)[-1]
    
    @classmethod
    def number_of_trees_of_heigh_less_than_n(cls, n):
        return sum(cls._build_number_of_rooted_identity_trees_of_height_n(n))
