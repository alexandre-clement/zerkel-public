from typing import List, Iterable, Sequence, Any

from itertools import product

import numpy as np
from tabulate import tabulate

from zerkel.interpreter.interpreter import Interpreter, Argument
from zerkel.core import (
    Node, Set, Visitable, NodeVisitor, EmptySet, Identity, 
    UnionPlus, IfThenElse, Projection, Composition, 
    Recursion, Union, Merge
)


class Table:
    def __init__(self, node: Node, *args: Iterable[Argument]):
        self.node = node
        self.args: List[List[Set]] = self._parse_arguments(*args)
        self.table: np.ndarray = self.build(*self.args)
    
    def _parse_arguments(self, *args: Iterable[Argument]) -> List[List[Set]]:
        result = []
        for arg in args:
            t = []
            for e in arg:
                if isinstance(e, Set):
                    t.append(e)
                elif isinstance(e, str):
                    t.append(Set.parse(e))
                elif isinstance(e, int):
                    t.append(Set.generate_ordinal(e))
            result.append(t)
        return result
    
    def build(self, *args) -> np.ndarray:
        result: List[Set] = []
        interpreter = Interpreter(self.node)
        for x in product(*args):
            result.append(interpreter.interpret(*x))
        return np.asarray(result).reshape(tuple(len(arg) for arg in self.args))

    def format(self, format="fancy_grid") -> str:
        return self._format(self.args, self.table, format)
    
    def _format(self, args, table, f):
        if len(args) == 1:
            return tabulate(zip(args[0], table), tablefmt=f)
        if len(args) == 2:    
            table = [[x, *line] for x, line in zip(args[0], table)]
        else:
            t = [[self._format(args[2:], e, f) for e in l] for l in table]
            table = [[x, *line] for x, line in zip(args[0], t)]
        headers: List[Any] = ['', *args[1]]
        return tabulate(table, headers, tablefmt=f)

    def __str__(self) -> str:
        return self.format()
    
    __repr__ = __str__
