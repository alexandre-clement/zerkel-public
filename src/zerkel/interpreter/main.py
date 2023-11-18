import sys

from typing import List, Iterable, Union as _Union

from zerkel.core.node import Node
from zerkel.interpreter.interpreter import (
    Interpreter, Argument, StepCounter, Debugger, StepByStep
)
from zerkel.interpreter.parser import Parser, ParseException
from zerkel.interpreter.semantic_analyzer import SemanticAnalyzer
from zerkel.interpreter.table import Table
from zerkel.interpreter.benchmark import Benchmark, Compare


_Node = _Union[Node, str]


def parse(text: str) -> Node:
    return Parser().parse(text)


def check(node: _Node):
    if isinstance(node, str):
        node = parse(node)
    return SemanticAnalyzer(node).check()


def interpret(node: _Node, *args: Argument):
    if isinstance(node, str):
        node = parse(node)
    check(node)
    return Interpreter(node).interpret(*args)


def debug(node: _Node, *args: Argument):
    if isinstance(node, str):
        node = parse(node)
    check(node)
    i = Interpreter(node)
    i.add_observer(Debugger())
    return i.interpret(*args)


def step_by_step(node: _Node, *args: Argument):
    if isinstance(node, str):
        node = parse(node)
    check(node)
    i = Interpreter(node)
    i.add_observer(StepByStep())
    return i.interpret(*args)

def table(node: _Node, *args: Iterable[Argument], repeat=None) -> Table:
    if isinstance(node, str):
        node = parse(node)
    if repeat is not None and repeat > 0:
        args = tuple(map(tuple, args))
        args = tuple(tuple(arg) for _ in range(repeat) for arg in args)
    return Table(node, *args)


def benchmark(node: _Node, *args: Iterable[Argument], repeat: int=None, iterations: int=1) -> Benchmark:
    if isinstance(node, str):
        node = parse(node)
    if repeat is not None and repeat > 0:
        
        args = tuple(map(tuple, args))
        args = tuple(tuple(arg) for _ in range(repeat) for arg in args)
    return Benchmark(node, iterations, *args)


def compare(node1: _Node, node2: _Node, *args: Iterable[Argument], repeat: int=None, iterations: int=1) -> Compare:
    if isinstance(node1, str):
        node1 = parse(node1)
    if isinstance(node2, str):
        node2 = parse(node2)
    if repeat is not None and repeat > 0:
        args = tuple(map(tuple, args))
        args = tuple(tuple(arg) for _ in range(repeat) for arg in args)
    return Compare(node1, node2, iterations, *args)
