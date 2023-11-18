from typing import List, Iterable, Sequence, Any

import math
from itertools import product
from statistics import mean

import numpy as np

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

from tabulate import tabulate

from zerkel.interpreter.interpreter import Interpreter, Argument, AtomicStepCounter
from zerkel.core import (
    Node, Set, Visitable, NodeVisitor, EmptySet, Identity, 
    UnionPlus, IfThenElse, Projection, Composition, 
    Recursion, Union, Merge
)


def coefficient(x, y):
    return np.cov(x, y)[0][1] / np.var(x)


def crop_node_str(node: Node, n=15) -> str:
    program = str(node)
    if len(program) > n:
        middle = (n - 3) // 2
        program = program[:middle] + '...' + program[-middle:]
    return program


class Benchmark:
    def __init__(self, node: Node, iterations: int, *args: Iterable[Argument]):
        self.node = node
        self.iterations = iterations
        self.args: List[List[Set]] = self._parse_arguments(*args)
        self.table: np.ndarray = self.bench(*self.args)
    
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
    
    def bench(self, *args) -> np.ndarray:
        result: List[int] = []
        for x in product(*args):
            interpreter = Interpreter(self.node)
            interpreter.interpret(*x)
            temp = []
            for _ in range(self.iterations):
                interpreter = Interpreter(self.node)
                step_counter = AtomicStepCounter()
                interpreter.add_observer(step_counter)
                interpreter.interpret(*x)
                temp.append(step_counter.steps)
            result.append(sum(temp))
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
    
    def plot(self):
        if len(self.args) == 1:
            x = [e.rank + 1 for e in self.args[0]]
            y = [e for e in self.table]
            plt.xlabel('Rank of the input set')
            plt.ylabel('Number of steps')
            plt.xscale('log')
            plt.yscale('log')
            coef = coefficient(np.log(x), np.log(y))
            plt.plot(x, y, label=f"Coefficient {coef:.3f}")
        elif len(self.args) == 2:
            x, y = zip(*product(*self.args))
            x = [e.rank for e in x]
            y = [e.rank for e in y]
            z = [v for v in self.table.flatten()]
            c = np.linspace(min(z), max(z), len(x))
            fig = plt.figure()
            ax = plt.axes(projection='3d')
            ax.set_xlabel('Rank of the first input')
            ax.set_ylabel('Rank of the second input')
            ax.set_zlabel('Number of steps')
            cx = coefficient(x, z)
            cy = coefficient(y, z)
            label = f"Coefficient nb steps/x={cx:.3f}, nb steps/y={cy:.3f}"
            ax.scatter(x, y, z, c=c, label=label)
        label = crop_node_str(self.node)
        plt.legend(title=f'Benchmark {label} (regular scale)')
        plt.show()
    
    def __str__(self) -> str:
        return self.format()
    
    __repr__ = __str__


class Compare:
    def __init__(self, node1: Node, node2: Node, iterations: int, *args: Iterable[Argument]):
        self.node1 = node1
        self.node2 = node2
        self.benchmark1 = Benchmark(node1, iterations, *args)
        self.benchmark2 = Benchmark(node2, iterations, *args)

    def plot(self):
        x1 = [e.rank for e in self.benchmark1.args[0]]
        x2 = [e.rank for e in self.benchmark2.args[0]]
        y1 = [e for e in self.benchmark1.table]
        y2 = [e for e in self.benchmark2.table]
        plt.xlabel('Rank of the input set')
        plt.ylabel('Number of steps')
        plt.xscale('log')
        plt.yscale('log')
        coef1 = coefficient(np.log(x1), np.log(y1))
        coef2 = coefficient(np.log(x2), np.log(y2))
        plt.plot(x1, y1, label=f"Coefficient of {self.node1} {coef1:.3f}")
        plt.plot(x2, y2, label=f"Coefficient of {self.node2} {coef2:.3f}")
        plt.legend(title=f'Comparison of {self.node1} and {self.node2} (logarithmic scale)')
        plt.show()

    def format(self, format="fancy_grid") -> str:
        return self._format(self.benchmark1.args, self.benchmark1.table, 
                            self.benchmark1.table, format)
    
    def _format(self, args, table1, table2, f):
        return tabulate(zip(args[0], table1, table2), tablefmt=f)
    
    def __str__(self) -> str:
        return self.format()
    
    __repr__ = __str__
