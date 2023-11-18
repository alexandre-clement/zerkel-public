
from zerkel.core.node import *
from zerkel.core.set import Set
from zerkel.interpreter import parse


def constante(value):
    def callback(stack, expression, parameters):
        expression.assign_value(value)
    return callback


def r_ite(stack, expression, parameters):
    x, u, v = parameters
    if u == v:
        if not x.is_closed:
            stack.push(x)
        else:
            expression.assign_value(x.value)
    elif not u.is_closed:
        stack.push(u)
    else:
        if not v.is_closed:
            stack.push(v)
        elif v.value.contains(u.value):
            expression.assign_value(Set())
        elif not x.is_closed:
            stack.push(x)
        else:
            expression.assign_value(x.value)


def compile_functions():
    Function(parse('R?'), r_ite)
    Function(parse('R>I'), constante(Set()))
    Function(parse('RR?'), constante(Set()))
