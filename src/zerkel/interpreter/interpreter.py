from typing import (List, Optional, Union as _Union, 
                    Deque, Sequence, Tuple, Dict, Any, Hashable)

from collections import deque

from tabulate import tabulate

from zerkel.core import (
    Node, Set, Visitable, NodeVisitor, EmptySet, Identity, 
    UnionPlus, IfThenElse, In, Projection, Composition, 
    Recursion, Union, Merge, Function
)


Argument = _Union[int, str, Set]
Expressions = Sequence['Expression']


class Expression:
    __slots__ = ['is_closed', 'value', 'interpreter']

    def __init__(self, is_closed: bool, interpreter: 'Interpreter'):
        self.is_closed = is_closed
        self.interpreter = interpreter
        self.value: Set

    def evaluate(self) -> None:
        raise NotImplementedError()

    def assign_value(self, value: Set) -> None:
        self.value = value
        self.is_closed = True


class ClosedExpression(Expression):
    def __new__(cls, value: Set, interpreter: 'Interpreter'):
        key = value
        try:
            return interpreter.cache[key]
        except KeyError:
            instance = Expression.__new__(cls)
            interpreter.cache[key] = instance
            return instance

    def __init__(self, value: Set, interpreter: 'Interpreter'):
        super().__init__(True, interpreter)
        self.value = value

    def evaluate(self) -> None:
        pass

    def __str__(self) -> str:
        return f'{self.value}'

    __repr__ = __str__


class LazyExpression(Expression): 
    def __new__(cls, interpreter: 'Interpreter', node: Node,
                parameters: Expressions):
        key = (node, parameters)
        try:
            return interpreter.cache[key]
        except KeyError:
            instance = Expression.__new__(cls)
            interpreter.cache[key] = instance
            instance.is_closed = False
            return instance

    def __init__(self, interpreter: 'Interpreter', node: Node,
                 parameters: Expressions):
        super().__init__(self.is_closed, interpreter)
        self.node = node
        self.parameters = parameters

    def evaluate(self) -> None:
        if not self.is_closed:
            Evaluator(self).evaluate()

    def change_node(self, node: Node, parameters: Expressions) -> None:
        self.node = node
        self.parameters = parameters

    def __str__(self) -> str:
        if self.is_closed:
            return f'{self.value}'
        return f'{self.node}({", ".join(map(str, self.parameters))})'

    __repr__ = __str__


class Stack:
    def __init__(self):
        self.stack: Deque[Expression] = deque()
    
    def __iter__(self):
        return iter(self.stack)

    def push(self, expression: Expression) -> None:
        self.stack.append(expression)

    def head(self) -> Expression:
        return self.stack[0]

    def peek(self) -> Expression:
        return self.stack[-1]

    def pop(self) -> None:
        self.stack.pop()

    def __str__(self) -> str:
        return tabulate(
            [[i, e] for i, e in reversed(list(enumerate(self.stack)))], 
            tablefmt="fancy_grid"
        )

    __repr__ = __str__


class Observer:
    def setup(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter

    def init(self):
        pass
    
    def notify(self):
        pass


class StepCounter(Observer):
    def init(self):
        self.steps = 0

    def notify(self):
        self.steps += 1
        

class AtomicStepCounter(Observer):
    def init(self):
        self.steps = 0

    def notify(self):
        peek = self.interpreter.stack.peek()
        if not peek.is_closed and isinstance(peek.node, (EmptySet, UnionPlus, IfThenElse)): 
            self.steps += 1

class Debugger(StepCounter):
    def notify(self):
        super().notify()
        print(f'Step {self.steps}', self.interpreter.stack, '', sep='\n')


class StepByStep(Debugger):
    def notify(self):
        super().notify()
        input('Press enter to continue')


class MismatchedNumberOfArguments(Exception):
    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return f'MismatchedNumberOfArguments: expected {self.expected} but got {self.actual}'


class Interpreter:
    __slots__ = ['root', 'stack', 'observers', 'cache']

    def __init__(self, node: Node):
        self.root = node
        self.stack: Stack
        self.observers: List[Observer] = []
        self.cache: Dict[Hashable, Expression] = {}
    
    def add_observer(self, observer: Observer) -> None:
        observer.setup(self)
        self.observers.append(observer)
        
    def clear_cache(self):
        self.cache.clear()

    def interpret(self, *args: Argument) -> Set:
        if len(args) != self.root.arity:
            raise MismatchedNumberOfArguments(self.root.arity, len(args))
        self.stack = Stack()
        self.stack.push(self._build_root_expression(*args))
        return self.run()

    def run(self):
        for observer in self.observers:
            observer.init()
        while not self.stack.head().is_closed:
            for observer in self.observers:
                observer.notify()
            if self.stack.peek().is_closed:
                self.stack.pop()
            else:
                self.stack.peek().evaluate()
        return self.stack.head().value

    def _build_root_expression(self, *args: Argument) -> Expression:
        parameters = self._parse_arguments(*args)
        return LazyExpression(self, self.root, parameters)
    
    def _parse_arguments(self, *args: Argument) -> Expressions:
        parameters: List[Expression] = []
        for arg in args:
            if isinstance(arg, Set):
                parameters.append(ClosedExpression(arg, self))
            elif isinstance(arg, str):
                parameters.append(ClosedExpression(Set.parse(arg), self))
            elif isinstance(arg, int):
                parameters.append(ClosedExpression(Set.generate_ordinal(arg), self))
        return tuple(parameters)

    def __str__(self):
        return f'Interpreter({self.root})'
    
    __repr__ = __str__


class Evaluator(NodeVisitor):
    def __init__(self, lazy_expression: LazyExpression):
        self.lazy_expression = lazy_expression
    
    @property
    def interpreter(self) -> Interpreter:
        return self.lazy_expression.interpreter
    
    @property
    def parameters(self) -> Expressions:
        return self.lazy_expression.parameters
    
    @property
    def stack(self) -> Stack:
        return self.interpreter.stack
    
    def evaluate(self) -> None:
        self.lazy_expression.node.accept(self)

    def visit_function(self, function: Function) -> None:
        function.call(self.stack, self.lazy_expression, self.parameters)

    def visit_empty_set(self, empty_set: EmptySet) -> None:
        self.lazy_expression.assign_value(Set())

    def visit_identity(self, identity: Identity) -> None:
        x, *_ = self.parameters
        if not x.is_closed:
            self.stack.push(x)
        else:
            self.lazy_expression.assign_value(x.value)

    def visit_union_plus(self, union_plus: UnionPlus) -> None:
        x, y = self.parameters
        if not x.is_closed:
            self.stack.push(x)
        else:
            if not y.is_closed:
                self.stack.push(y)
            else:
                self.lazy_expression.assign_value(Set(*x.value, y.value))

    def visit_if_then_else(self, if_then_else: IfThenElse) -> None:
        x, y, u, v = self.parameters
        if x == y:
            if not x.is_closed:
                self.stack.push(x)
            else:
                self.lazy_expression.assign_value(x.value)
        elif u == v:
            if not y.is_closed:
                self.stack.push(y)
            else:
                self.lazy_expression.assign_value(y.value)
        elif not u.is_closed:
            self.stack.push(u)
        else:
            if not v.is_closed:
                self.stack.push(v)
            elif v.value.contains(u.value):
                if not x.is_closed:
                    self.stack.push(x)
                else:
                    self.lazy_expression.assign_value(x.value)
            elif not y.is_closed:
                self.stack.push(y)
            else:
                self.lazy_expression.assign_value(y.value)
    
    def visit_in(self, in_operator: In):
        *x, u, v = self.parameters
        if in_operator.f == in_operator.g:
            self.lazy_expression.change_node(in_operator.f, self.parameters)
        elif u == v:
            self.lazy_expression.change_node(in_operator.g, self.parameters)
        if not u.is_closed:
            self.stack.push(u)
        else:
            if not v.is_closed:
                self.stack.push(v)
            elif v.value.contains(u.value):
                self.lazy_expression.change_node(in_operator.f, self.parameters)
            else:
                self.lazy_expression.change_node(in_operator.g, self.parameters)
    
    def visit_projection(self, p: Projection) -> None:
        if p.right > 0:
            parameters = self.parameters[p.left: -p.right]
        else:
            parameters = self.parameters[p.left:]
        self.lazy_expression.change_node(p.f, parameters)

    def visit_composition(self, o: Composition):
        i, p = self.interpreter, self.parameters
        parameters = tuple(LazyExpression(i, g, p) for g in o.g)
        self.lazy_expression.change_node(o.f, parameters)

    def visit_recursion(self, r: Recursion):
        z, *x = self.parameters
        union = LazyExpression(self.interpreter, Union(r), self.parameters)
        parameters: Expressions = (union, z, *x)
        self.lazy_expression.change_node(r.g, parameters)

    def visit_union(self, union: Union):
        z, *x = self.parameters
        if not z.is_closed:
            self.stack.push(z)
        else:
            le, ce = LazyExpression, ClosedExpression
            i = self.interpreter
            p = tuple(le(i, union.h, (ce(u, i), *x)) for u in z.value)
            self.lazy_expression.change_node(Merge(), p)

    def visit_merge(self, merge: Merge):
        result: List[Set] = []
        for p in self.parameters:
            if not p.is_closed:
                self.stack.push(p)
                return
            result.extend(p.value)
        self.stack.peek().assign_value(Set(*result))
