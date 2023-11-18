from functools import wraps
from collections import defaultdict


class _cache(type):
    def __call__(cls, *args, **kwargs):
        key = (cls, *args, *kwargs.items())
        try:
            return cls.cache[key]
        except KeyError:
            instance = type.__call__(cls, *args, **kwargs)
            cls.cache[key] = instance
            return instance


cache = _cache('NodeCache', (), {})


class Visitable:
    def accept(self, node_visitor: 'NodeVisitor'):
        raise NotImplementedError()


class Node(Visitable, cache):
    cache = {}
    
    def __init__(self, arity: int, *children: 'Node'):
        self.arity = arity
        self.size: int = 1 + sum(child.size for child in children)
        self.children = children
        self._hash = hash((self.__class__, self.children))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.children == other.children

    def __hash__(self):
        return self._hash

    def __str__(self):
        return ascii_printer.print(self)

    __repr__ = __str__


class Function(Node):
    def __init__(self, node: Node, callback):
        super().__init__(node.arity, *node.children)
        if isinstance(node, Function):
            node = node.node
        self.node = node
        self.callback = callback
        self.cache[(node.__class__, *node.children)] = self
    
    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_function(self)
    
    def call(self, stack, expression, parameters):
        self.callback(stack, expression, parameters)

    def __hash__(self):
        return hash(self.node)

    def __eq__(self, other):
        return self is other or self.node == self.other

    def __str__(self):
        return f'({ascii_printer.print(self.node)})'

    __repr__ = __str__


class EmptySet(Node):
    def __init__(self):
        super().__init__(0)

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_empty_set(self)


class Identity(Node):
    def __init__(self):
        super().__init__(1)

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_identity(self)


class UnionPlus(Node):
    def __init__(self):
        super().__init__(2)

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_union_plus(self)


class IfThenElse(Node):
    def __init__(self):
        super().__init__(4)

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_if_then_else(self)


class In(Node):
    def __init__(self, f: Node, g: Node):
        super().__init__(f.arity, f, g)
        self.f = f
        self.g = g

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_in(self)


class Projection(Node):
    def __init__(self, f: Node, left: int, right: int):
        super().__init__(f.arity + left + right, f)
        self.f = f
        self.left = left
        self.right = right
        self.size: int = left + right + self.size - 1

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_projection(self)
    
    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((super().__hash__(), self.left, self.right))


class Composition(Node):
    def __init__(self, f: Node, *g: Node):
        super().__init__(g[0].arity, f, *g)
        self.f = f
        self.g = g

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_composition(self)


class Recursion(Node):
    def __init__(self, g: Node):
        super().__init__(g.arity - 1, g)
        self.g = g

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_recursion(self)


class Union(Node):
    def __init__(self, h: Node):
        super().__init__(h.arity, h)
        self.h = h

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_union(self)


class Merge(Node):
    def __init__(self):
        super().__init__(0)

    def accept(self, visitor: 'NodeVisitor'):
        visitor.visit_merge(self)


class NodeVisitor:
    def visit_function(self, function: Function):
        pass

    def visit_empty_set(self, empty_set: EmptySet):
        pass

    def visit_identity(self, identity: Identity):
        pass

    def visit_union_plus(self, union_plus: UnionPlus):
        pass

    def visit_if_then_else(self, if_then_else: IfThenElse):
        pass
    
    def visit_in(self, in_operator: In):
        pass
    
    def visit_projection(self, projection: Projection):
        pass

    def visit_composition(self, composition: Composition):
        pass

    def visit_recursion(self, recursion: Recursion):
        pass

    def visit_union(self, union: Union):
        pass

    def visit_merge(self, merge: Merge):
        pass


class Printer(NodeVisitor):
    def __init__(self, empty_set, identity, union_plus, if_then_else, 
                 in_operator, left, right, composition, recursion,
                 union, merge):
        self.empty_set = empty_set
        self.identity = identity
        self.union_plus = union_plus
        self.if_then_else = if_then_else
        self.in_operator = in_operator
        self.left = left
        self.right = right
        self.composition = composition
        self.recursion = recursion
        self.union = union
        self.merge = merge
        self.result = None

    def print(self, node: Node) -> str:
        self.result = ''
        node.accept(self)
        return self.result

    def visit_function(self, function: Function):
        self.result += str(function)

    def visit_empty_set(self, empty_set: EmptySet):
        self.result += self.empty_set

    def visit_identity(self, identity: Identity):
        self.result += self.identity

    def visit_union_plus(self, union_plus: UnionPlus):
        self.result += self.union_plus

    def visit_if_then_else(self, if_then_else: IfThenElse):
        self.result += self.if_then_else
    
    def visit_in(self, in_operator: In):
        self.result += self.in_operator
        in_operator.f.accept(self)
        in_operator.g.accept(self)

    def visit_projection(self, projection: Projection):
        self.result += self.left * projection.left
        self.result += self.right * projection.right
        projection.f.accept(self)

    def visit_composition(self, composition: Composition):
        self.result += self.composition
        composition.f.accept(self)
        for g in composition.g:
            g.accept(self)

    def visit_recursion(self, recursion: Recursion):
        self.result += self.recursion
        recursion.g.accept(self)

    def visit_union(self, union: Union):
        self.result += self.union
        union.h.accept(self)

    def visit_merge(self, merge: Merge):
        self.result += self.merge


ascii_printer = Printer('E', 'I', '+', '?', '!', '<', '>', 'o', 'R', 'U', 'M')
