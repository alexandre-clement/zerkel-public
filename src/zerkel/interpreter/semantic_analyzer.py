from zerkel.core import (
    Node, NodeVisitor, In, Projection, Composition, Recursion
)


class SemanticAnalyzerException(Exception):
    pass


class MismatchedArity(SemanticAnalyzerException):
    def __init__(self, in_operator: In):
        self.in_operator = in_operator

    def __str__(self):
        return ('Mismatched arity: In operator first compound has an arity of '
                f'{self.in_operator.f.arity} and the secound compound has an '
                f'arity of {self.in_operator.g.arity}.')


class InvalidInOperatorArity(SemanticAnalyzerException):
    def __init__(self, in_operator: In):
        self.in_operator = in_operator
    
    def __str__(self):
        return (f'The In operator "{self.in_operator}" tokens requires a '
                'program of at least arity 2 but a program of arity '
                f'{self.in_operator.f.arity} was given.')


class RequireAtLeastOneCompound(SemanticAnalyzerException):
    def __init__(self, o: Composition):
        self.o = o

    def __str__(self):
        return f'The composition "{self.o}" requires at least one compound.'


class NotEnoughCompounds(SemanticAnalyzerException):
    def __init__(self, o: Composition):
        self.o = o

    def __str__(self):
        return (f'The composition "{self.o}" has not enough compounds for {self.o.f}. '
                f'{len(self.o.g)} were given but {self.o.f.arity} required.')


class TooManyCompounds(SemanticAnalyzerException):
    def __init__(self, o: Composition):
        self.o = o

    def __str__(self):
        return (f'The composition "{self.o}" has too many compounds for {self.o.f}, '
                f'{len(self.o.g)} were given but {self.o.f.arity} required.')


class OneCompoundMismatchedArity(SemanticAnalyzerException):
    def __init__(self, o: Composition):
        self.o = o

    def __str__(self):
        arities = tuple(map(lambda n: n.arity, self.o.g))
        return (f'The compounds of "{self.o}" have an arity of {arities}, '
                'but it is required that they all be equal.')


class InvalidRecursionArity(SemanticAnalyzerException):
    def __init__(self, r: Recursion):
        self.r = r

    def __str__(self):
        return (f'The Recursion "{self.r}" has a compound of arity '
                f' {self.r.g.arity} but it requires a program of '
                'at least arity 2.')


class SemanticAnalyzer(NodeVisitor):
    def __init__(self, node: Node):
        self.node = node
        self.is_valid = True

    def check(self):
        self.node.accept(self)
    
    def visit_in(self, in_operator: In):
        if in_operator.f.arity != in_operator.g.arity:
            raise MismatchedArity(in_operator)
        if in_operator.f.arity < 2:
            raise InvalidInOperatorArity(in_operator)
        in_operator.f.accept(self)
        in_operator.g.accept(self)
    
    def visit_projection(self, projection: Projection):
        projection.f.accept(self)

    def visit_composition(self, o: Composition):
        if len(o.g) < o.f.arity:
            raise NotEnoughCompounds(o)
        if len(o.g) > o.f.arity:
            raise TooManyCompounds(o)
        if not o.g:
            raise RequireAtLeastOneCompound(o)
        if any(g.arity != o.g[0].arity for g in o.g):
            raise OneCompoundMismatchedArity(o)
        o.f.accept(self)
        for g in o.g:
            g.accept(self)

    def visit_recursion(self, r: Recursion):
        if r.g.arity < 2:
            raise InvalidRecursionArity(r)
        r.g.accept(self)
