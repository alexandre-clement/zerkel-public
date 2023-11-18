import pyparsing as pp
from zerkel.core import (
    Node, EmptySet, Identity, UnionPlus, IfThenElse, In,
    Projection, Composition, Recursion
)


class ParseException(Exception):
    def __init__(self, text, col):
        self.text = text
        self.col = col

    def __str__(self) -> str:
        return (f'ParseException at column {self.col}:\n{self.text}\n' +
                ' ' * (self.col - 1) + '^')


class Parser:
    def __init__(self):
        self._expression = None
        self._compounds = None
        self.syntax = self._syntax()

    def _syntax(self):
        self._expression = pp.Forward()
        e = pp.Literal('E').addParseAction(lambda: EmptySet())
        i = pp.Literal('I').addParseAction(lambda: Identity())
        u = pp.Literal('+').addParseAction(lambda: UnionPlus())
        q = pp.Literal('?').addParseAction(lambda: IfThenElse())
        m = pp.Literal('!').suppress() + self._expression + self._expression
        m.addParseAction(self._build_in_operator)

        left = pp.Literal('<').addParseAction(lambda: (1, 0))
        right = pp.Literal('>').addParseAction(lambda: (0, 1))
        p = pp.OneOrMore(left ^ right) + self._expression
        p.addParseAction(self._build_projection)

        self._compounds = pp.Forward()
        o = pp.Literal('o').suppress() + self._expression
        o.addParseAction(self._build_compounds)
        o = o + self._compounds
        o.addParseAction(self._build_composition)

        r = pp.Literal('R').suppress() + self._expression
        r.addParseAction(self._build_recursion)

        successor = pp.Keyword('successor')
        successor.addParseAction(self._generic_builder('o+II'))

        singleton = pp.Keyword('singleton')
        singleton.addParseAction(self._generic_builder('o+<EI'))

        pair = pp.Keyword('pair')
        pair.addParseAction(
            self._generic_builder('o+> singleton <I')
        )

        couple = pp.Keyword('couple')
        couple.addParseAction(
            self._generic_builder('o pair > singleton pair')
        )

        union = pp.Keyword('union')
        union.addParseAction(self._generic_builder('oRo?<>I>>I<>I<<III'))
        
        inter = pp.Keyword('inter')
        inter.addParseAction(self._generic_builder(
            'o filter o o and map o in <I>I <I>I union I'
        ))
        
        _not = pp.Keyword('not')
        _not.addParseAction(self._generic_builder('o?<E<1<EI'))
        
        _and = pp.Keyword('and')
        _and.addParseAction(self._generic_builder('o?<Eo?<1<E<1I<EI'))
        
        _or = pp.Keyword('or')
        _or.addParseAction(self._generic_builder('o?<1<E<1I'))
        
        _all = pp.Keyword('all').suppress() + self._expression
        _all.addParseAction(self._all)
        
        _any = pp.Keyword('any').suppress() + self._expression
        _any.addParseAction(self._any)     
           
        _in = pp.Keyword('in')
        _in.addParseAction(self._generic_builder('o?<<1<<E>I<I'))
        
        subset = pp.Keyword('subset')
        subset.addParseAction(self._generic_builder('o and map in'))
        
        equal = pp.Keyword('equal')
        equal.addParseAction(
            self._generic_builder('o?<<1<<0>I+')
        )
        
        not_equal = pp.Keyword('not equal')
        not_equal.addParseAction(
            self._generic_builder('oR?<<1>I+')
        )
        
        discard = pp.Keyword('discard')
        discard.addParseAction(
            self._generic_builder('o union filter not equal')
        ) 
        
        is_singleton = pp.Keyword('is singleton')
        is_singleton.addParseAction(
            self._generic_builder('o and o map o and o map equal <I>I II')
        )
        
        is_pair = pp.Keyword('is pair')
        is_pair.addParseAction(
            self._generic_builder("""o and o map oo and map o?<<<1 oo and map o
                                or o pair o equal >>I<>I o equal >>I<<I<>I<<I>>
                                I<<<E o equal >>I<<I<>I<<I>>I III""")
        )
        
        is_transitive = pp.Keyword('is transitive')
        is_transitive.addParseAction(
            self._generic_builder('o all all in II')
        )
        
        is_ordinal = pp.Keyword('is ordinal')
        is_ordinal.addParseAction(
            self._generic_builder('R o and o pair >I < is transitive')
        )
        
        is_limit = pp.Keyword('is limit')
        is_limit.addParseAction(
            self._generic_builder('o and o pair o not equal I <E o all o not equal > successor <I II')
        )
        
        is_omega = pp.Keyword('is omega')
        is_omega.addParseAction(
            self._generic_builder('o and o pair all o not is limit is limit')
        )
        
        extract_omega = pp.Keyword('extract omega')
        extract_omega.addParseAction(
            self._generic_builder('o union filter is omega')
        )
        
        log_omega = pp.Keyword('log omega')
        log_omega.addParseAction(
            self._generic_builder('oo? o log >I<I <<E<<E<I I extract omega')
        )
        
        
        position = pp.pyparsing_common.signed_integer
        _slice = (pp.Optional(position, default=0) +
                  pp.Keyword('...').suppress() +
                  pp.Optional(position, default=None))
        _slice.addParseAction(self._build_slice)
        selection = _slice | position
        selections = pp.OneOrMore(selection)

        select = pp.Keyword('select').suppress()
        among = pp.Keyword('among').suppress() + position
        _for = pp.Keyword('for').suppress()

        none = select + pp.Keyword('none').suppress() + among
        none = none + pp.Optional(_for + self._expression, default=EmptySet())
        none.addParseAction(lambda t: Projection(t[1], t[0], 0))

        select = select + selections + among + _for + self._expression
        select.addParseAction(self._build_select)
        select = none | select

        map = pp.Keyword('map').suppress() + self._expression
        map.addParseAction(self._build_map)

        filter = pp.Keyword('filter').suppress() + self._expression
        filter.addParseAction(self._build_filter)

        op = pp.Keyword('op').suppress() + self._expression + self._expression
        op.addParseAction(self._build_op)

        iop = pp.Keyword('iop').suppress() + self._expression
        iop.addParseAction(self._build_iop)

        add = pp.Keyword('add')
        add.addParseAction(self._generic_builder('op successor << singleton'))
        
        biadd = pp.Keyword('&')
        biadd.addParseAction(self._generic_builder('o?<o?<1<E<EI<<E<<E>I'))  
         
        sub = pp.Keyword('sub')
        sub.addParseAction(self._generic_builder('iop add'))
        
        mult = pp.Keyword('mult')
        mult.addParseAction(self._generic_builder('op add <<<o successor E'))
        
        div = pp.Keyword('div')
        div.addParseAction(self._generic_builder('iop mult'))
        
        power = pp.Keyword('power')
        power.addParseAction(self._generic_builder('op mult <<<oo singleton successor E'))
        
        log = pp.Keyword('log')
        log.addParseAction(self._generic_builder('iop power'))
        
        predecessor = pp.Keyword('predecessor')
        predecessor.addParseAction(self._generic_builder('Ro?>R+>I>R+<I'))   
           
        rank = pp.Keyword('rank')
        rank.addParseAction(self._generic_builder('o predecessor R>R+'))
        
        get_first = pp.Keyword('get first')
        get_first.addParseAction(self._generic_builder('o union o union filter is singleton'))
        
        get_second = pp.Keyword('get second')
        get_second.addParseAction(self._generic_builder('oo?<Io discard > union <I<<E> is singleton I get first'))  
        
        constant = pp.pyparsing_common.integer.copy()
        constant.addParseAction(self._build_constant)
        
        var = pp.Word(pp.alphas, bodyChars=pp.alphanums)
        variables = var + pp.ZeroOrMore(pp.Literal(',').suppress() + var)
        
        self._expression << (
            log_omega | get_first | get_second |        
            is_transitive | is_ordinal | is_limit | is_omega | extract_omega |
            _all | _any | is_singleton | is_pair |
            biadd |
            not_equal | _not | _and | _or | _in | subset | equal | discard |
            add | sub | mult | div | power | log | constant |
            couple | pair | singleton |
            successor | predecessor | rank | 
            op | iop | map | filter | select | union | inter | 
            r | o | p | m | q | u | i | e
        )
        return pp.StringStart() + self._expression + pp.StringEnd()
    
    def _build_in_operator(self, tokens):
        return In(*tokens)

    def _build_projection(self, tokens):
        *values, f = tokens
        left, right = map(sum, zip(*values))
        return Projection(f, left, right)

    def _build_compounds(self, tokens):
        f = tokens[0]
        if f.arity <= 0:
            raise Exception(f'Composition error: main function {f}'
                            ' does not have an arity >= 1.')
        self._compounds << (self._expression * f.arity)

    def _build_composition(self, tokens):
        return Composition(*tokens)

    def _build_recursion(self, tokens):
        return Recursion(tokens[0])

    def _generic_builder(self, code):
        def builder():
            return self.parse(code)
        return builder

    def _build_select(self, tokens):
        *positions, n, p = tokens
        if p.arity == 1:
            position = positions[0]
            return self._select_position(position, n, p)
        compounds = []
        for e in positions:
            if isinstance(e, int) and e < n:
                compounds.append(self._select_position(e, n))
            elif isinstance(e, slice):
                indices = e.indices(n)
                for i in range(*indices):
                    compounds.append(self._select_position(i, n))
        return Composition(p, *compounds)

    def _build_slice(self, t):
        start, end = t
        if end is not None and end < start:
            return slice(t[0], t[1], -1)
        return slice(t[0], t[1])

    def _select_position(self, position, arity, p=None):
        if p is None:
            p = Identity()
        if arity == 1:
            return p
        if position >= 0:
            l = position
            r = arity - position - 1
        else:
            l = arity + position - 1
            r = position + 1
        return Projection(p, l, r)

    def _build_map(self, tokens):
        p = tokens[0]
        n = p.arity
        m = (f'select 0 0 ... among {n} for Ro? select 1 3 ... among {n + 2}'
             f' for o singleton {p} select 0 among {n + 2} for I select 1'
             f' among {n + 2} for I select 2 among {n + 2} for I')
        return self.parse(m)

    def _build_filter(self, tokens):
        p = tokens[0]
        n = p.arity
        m = (f'select 0 0 ... among {n} for Ro? select 1 3 ... among {n + 2}'
             f' for o ? select 0 among {n} for singleton select none among {n}'
             f' select none among {n} {p} select 0 among {n + 2} for I'
             f' select 1 among {n + 2} for I select 2 among {n + 2} for I')
        return self.parse(m)
    
    def _build_op(self, tokens):
        recursive_function, initialization_function = tokens
        return self.parse(
            f'o union oRo? select 0 2 among 3 for o singleton o union map '
            f'{recursive_function} {initialization_function} <<<E<>I<I>I'
        )

    def _build_iop(self, tokens):
        op = tokens[0]
        return self.parse(
            f'oo union o filter o?>> successor >>>Eo {op}'
            ' <<I>>I<>I>I>I<I> successor <I'
        )
    
    def _build_constant(self, tokens):
        return self.parse('o successor ' * tokens[0] + 'E')

    def _all(self, tokens):
        p = tokens[0]
        return self.parse(f'o and map {p}')
    
    def _any(self, tokens):
        p = tokens[0]
        return self.parse(f'o or map {p}')

    def parse(self, text) -> Node:
        try:
            return self.syntax.parseString(text)[0]
        except pp.ParseException as exception:
            e = exception
        # We don't want the full traceback since error messages from
        # pyparsing are not lisible.
        raise ParseException(e.line, e.col)
