from typing import Dict, Tuple, Callable

from zerkel.core import Set, Node

from zerkel.interpreter import parse


_blacklist = {
    'R>I', # Equal to <E
    'RR?', # Equal to <<E
    'RoR++', # Equal to Ro+++
    'o+R+I', # Equal to R+
    'o++<I', # Equal to +
    'R!<I+', # Equal R+
    'R!>I+', # Equal R+
    'R!+<R+', # Equal R+
    'R!+>R+', # Equal R>R+
    'R!<I>I', # Equal I
    'R!<R++', # Equal R+
    'R!>R++', # Equal R+
    'R!<<E+', # Equal R+
    'R!>I<<E', # Equal <E
    'R!<<E>I', # Equal <E
    'R>R!+<I', # Equal <E WHY ?
    'R>R!+>I', # Equal <E WHY ?
    'RR!>+<+', # Equal R+ WHY ?
    'R>R>R+', # Equal to R>R+
    'R>o+II', # Equal to R>R+
    'o+R+<E', # Equal to R+
    'o+R+R+', # Equal to oR+R+
    'RRo+??', # Equal to >R>R+
    'RRoR+?', # Equal to >R>R+
    'o+>I<I', # Equal to +
    'R>o+I<E', # Equal <o+EE
    'R>o+<EI', # Equal o+<EI
    'R>Ro+++', # Equal R>oR+R+
    'Ro++<<E', # Equal R+
    'o+o+III', # Equal o+II
    'RoR>R++', # Equal to oR+R>R+
    'oR?II<E', # Equal I
    'oR?IIR+', # Equal >E
    'oR?IR+I', # Equal I
    'oR>R+R+', # Equal to oR+R>R+
    'o+o++++', # Equal o+++
    'oR?++>I', # Equal <<o+EE
    'oR?+<I+', # Equal <<E
    'oo+I<E+', # Equal o++<<E
    'oo+IR++', # Equal o++oR++
    'oo+<EI+', # Equal o+<<E+
    'RoR>R+?', # Equal >>R>R+
    'oo+IIR?', # Equal o+R?R?
}


tc = (lambda r: lambda x: r(r, x))(lambda f, x: Set(x, *(v for u in x for v in f(f, u))))
rank = (lambda r: lambda x: r(r, x))(lambda f, x: tc(Set(*(v for u in x for v in f(f, u)))))
rtc = (lambda r: lambda x: r(r, x))(lambda f, x: Set(x, *(v for u in x for v in f(f, u)), Set(x, *(v for u in x for v in f(f, u)))))
rxyx = (lambda r: lambda x: r(r, x))(lambda f, x: (lambda a, b: Set(*a, b, a))(Set(*(v for u in x for v in f(f, u))), x))


_programs: Dict[Tuple[int, int], Dict[str, Callable]] = {
    (1, 0): {
        'E': lambda: 0
        }, 
    (1, 1): {
        'I': lambda x: x
        }, 
    (1, 2): {
        '+': lambda x, y: Set(*x, y)
        }, 
    (1, 4): {
        '?': lambda x, y, u, v: x if u in v else y
        },
    (2, 1): {
        'R+': tc
        }, 
    (2, 3): {
        'R?': lambda x, y, z: Set() if y in z else x
        },
    (4, 0): {
        'o+EE': lambda: Set(Set())
        }, 
    (4, 1): {
        'R>R+': rank, 
        'o+II': lambda x: Set(*x, x)
        }, 
    (4, 2): {
        'o+++': lambda x, y: Set(*x, y, Set(*x, y)), 
        'oR++': lambda x, y: tc(Set(*x, y)),
        '!+<I': lambda x, y: Set(*x, y) if x in y else y,
        '!+>I': lambda x, y: Set(*x, y) if x in y else x,
        '!<I+': lambda x, y: y if x in y else Set(*x, y),
        '!>I+': lambda x, y: x if x in y else Set(*x, y)
        }, 
    (4, 3): {}, 
    (4, 4): {
        'o+??': lambda x, y, u, v: Set(*x, x) if u in v else Set(*y, y), 
        'oR+?': lambda x, y, u, v: tc(x if u in v else y) 
        },
    (5, 1): {
        'Ro+++': rtc,
        'o+I<E': lambda x: Set(*x, Set()), 
        'o+IR+': lambda x: Set(*x, tc(x)), 
        'o+<EI': lambda x: Set(x), 
        'oR+R+': lambda x: (lambda y: Set(*y, y))(tc(x)),
        'R!+<I': lambda x: None,
        'R!+>I': lambda x: None
        }, 
    (5, 2): {
        '!+<R+': lambda x, y: Set(*x, y) if x in y else tc(y),
        '!+>R+': lambda x, y: Set(*x, y) if x in y else tc(x),
        '!+<<E': lambda x, y: Set(*x, y) if x in y else Set(),
        '!<I>I': lambda x, y: y if x in y else x,
        '!>I<I': lambda x, y: x if x in y else y,
        '!<R++': lambda x, y: tc(y) if x in y else Set(*x, y),
        '!>R++': lambda x, y: tc(x) if x in y else Set(*x, y),
        '!<<E+': lambda x, y: Set() if x in y else Set(*x, y),
        'o++>I': lambda x, y: Set(*x, y, x), 
        'o+<I+': lambda x, y: Set(*y, Set(*x, y)),
        'o+>I+': lambda x, y: Set(*x, Set(*x, y))
        }, 
    (5, 3): {
        '!<+>+': lambda x, y, z: Set(*y, z) if y in z else Set(*x, y),
        '!>+<+': lambda x, y, z: Set(*x, y) if y in z else Set(*y, z),
        'Ro+??': lambda x, u, v: rank(x) if u in v else Set(*x, x),
        'RoR+?': lambda x, u, v: rank(x) if u in v else tc(x),
        'oR+R?': lambda x, u, v: Set(Set()) if u in v else tc(x)
        },
    (6, 1): {
        'R!+<<E': lambda x: None, # Similar to R!+>I
        'R!>I<I': lambda x: None, # Similar to R!+>I
        'Ro++>I': rxyx,
        'Ro+<I+': (lambda r: lambda x: r(r, x))(lambda f, x: (lambda a, b: Set(*b, Set(*a, b)))(Set(*(v for u in x for v in f(f, u))), x)),
        'Ro+>I+': (lambda r: lambda x: r(r, x))(lambda f, x: (lambda a, b: Set(*a, Set(*a, b)))(Set(*(v for u in x for v in f(f, u))), x)),
        'o+<ER+': lambda x: Set(tc(x))
        }, 
    (6, 2): {
        '!+o+++': lambda x, y: Set(*x, y) if x in y else Set(*x, y, Set(*x, y)),
        '!+oR++': lambda x, y: Set(*x, y) if x in y else tc(Set(*x, y)),
        '!<I<R+': lambda x, y: y if x in y else tc(y),
        '!<I>R+': lambda x, y: y if x in y else tc(x),
        '!<I<<E': lambda x, y: y if x in y else Set(),
        '!>I<R+': lambda x, y: x if x in y else tc(y),
        '!>I>R+': lambda x, y: x if x in y else tc(x),
        '!>I<<E': lambda x, y: x if x in y else Set(),
        '!<R+<I': lambda x, y: tc(y) if x in y else y,
        '!<R+>I': lambda x, y: tc(y) if x in y else x,
        '!>R+<I': lambda x, y: tc(x) if x in y else y,
        '!>R+>I': lambda x, y: tc(x) if x in y else x,
        '!<<E<I': lambda x, y: Set() if x in y else y,
        '!<<E>I': lambda x, y: Set() if x in y else x,
        '!o++++': lambda x, y: Set(*x, y, Set(*x, y)) if x in y else Set(*x, y),
        '!oR+++': lambda x, y: tc(Set(*x, y)) if x in y else Set(*x, y),
        'R!<+>+': lambda x, y: None, # ???
        'R!>+<+': lambda x, y: None, # ???
        'RoR+R?': (lambda r: lambda x, y: r(r, x, y))(lambda f, x, y: (lambda a, u, v: Set(Set()) if u in v else tc(a))(Set(*(v for u in x for v in f(f, u, y))), x, y)), 
        'o++<R+': lambda x, y: Set(*x, y, tc(y)),
        'o++>R+': lambda x, y: Set(*x, y, tc(x)),
        'o++<<E': lambda x, y: Set(*x, y, Set()),
        'o+<I>I': lambda x, y: Set(*y, x),
        'o+<R++': lambda x, y: Set(*tc(y), Set(*x, y)),
        'o+>R++': lambda x, y: Set(*tc(x), Set(*x, y)),
        'o+<<E+': lambda x, y: Set(Set(*x, y)),
        'oR>R++': lambda x, y: rank(Set(*x, y)), 
        'oo+II+': lambda x, y: (lambda a: Set(*a, a))(Set(*x, y))
        },
    (6, 3): {
        '!<+>>I': lambda x, y, z: Set(*y, z) if y in z else x,
        '!>+<<I': lambda x, y, z: Set(*x, y) if y in z else z,
        '!>+<>I': lambda x, y, z: Set(*x, y) if y in z else y,
        '!>+>>I': lambda x, y, z: Set(*x, y) if y in z else x,
        '!<<I>+': lambda x, y, z: z if y in z else Set(*x, y),
        '!<>I>+': lambda x, y, z: y if y in z else Set(*x, y),
        '!>>I<+': lambda x, y, z: x if y in z else Set(*y, z),
        '!>>I>+': lambda x, y, z: x if y in z else Set(*x, y),
        'o+<+>+': lambda x, y, z: Set(*y, z, Set(*x, y)),
        'o+<+R?': lambda x, y, z: Set(*y, z, Set() if y in z else x), 
        'o+>+<+': lambda x, y, z: Set(*x, y, Set(*y, z)), 
        'o+>+R?': lambda x, y, z: Set(*x, y, Set() if y in z else x),
        'o+R?<+': lambda x, y, z: Set(*(Set() if y in z else x), Set(*y, z)),
        'o+R?>+': lambda x, y, z: Set(*(Set() if y in z else x), Set(*x, y)),
        'o+R?R?': lambda x, y, z: (lambda a: Set(*a, a))(Set() if y in z else x)
        },
    (6, 4): {
        'o+?<R?': lambda x, y, u, v: Set(*(x if u in v else y), Set() if u in v else y), 
        'o+?>R?': lambda x, y, u, v: Set(*(x if u in v else y), Set() if y in u else x),
        'o+?<<+': lambda x, y, u, v: Set(*(x if u in v else y), Set(*u, v)),
        'o+?<>+': lambda x, y, u, v: Set(*(x if u in v else y), Set(*y, u)),
        'o+?>>+': lambda x, y, u, v: Set(*(x if u in v else y), Set(*x, y)),
        'o+<R??': lambda x, y, u, v: Set(*(Set() if u in v else y), x if u in v else y),
        'o+>R??': lambda x, y, u, v: Set(*(Set() if y in u else x), x if u in v else y),
        'o+<<+?': lambda x, y, u, v: Set(*u, v, x if u in v else y),
        'o+<>+?': lambda x, y, u, v: Set(*y, u, x if u in v else y),
        'o+>>+?': lambda x, y, u, v: Set(*x, y, x if u in v else y),
        'oR>R+?': lambda x, y, u, v: rank(x if u in v else y),
        'oo+II?': lambda x, y, u, v: (lambda a: Set(*a, a))(x if u in v else y)
        },
    (6, 5): {
        'o+<?>?': lambda x, y, u, v, w: Set(*(y if v in w else u), x if u in v else y),
        'o+>?<?': lambda x, y, u, v, w: Set(*(x if u in v else y), y if v in w else u)
        },
    (7, 0): {
        'o+Eo+EE': lambda: Set.parse('{1}'),
        'oo+++EE': lambda: Set.parse('2')
        },
    (7, 1): {
        'R!<I<<E': lambda x: None,
        'R!<R+<I': lambda x: tc(x) if x.rank % 2 else x, # Almost
        'R!<R+>I': lambda x: None,
        'R!>R+<I': lambda x: rank(x) if x.rank % 2 else x, # Almost
        'R!>R+>I': lambda x: None, # Rang du plus grand ordinal contenue dans l'ensemble + 1
        'R!<<E<I': lambda x: None,
        'RR!<+>+': lambda x: None,
        # 'R>Ro+++': (lambda r: lambda x: r(r, x))((lambda g: lambda f, x: g(Set(*(v for u in x for v in f(f, u)))))(rtc)), # Very slow
        'R>o+IR+': (lambda r: lambda x: r(r, x))(lambda f, x: (lambda a: Set(*a, tc(a)))(Set(*(v for u in x for v in f(f, u))))), 
        'R>oR+R+': (lambda r: lambda x: r(r, x))(lambda f, x: tc(tc(Set(*(v for u in x for v in f(f, u)))))), # Also slow but a bit better than R>Ro+++
        'RRoR+R?': lambda x: None, # ???
        'Ro++<R+': lambda x: None, # Generate sets of rank rank(x) + 2
        'Ro++>R+': lambda x: None, # Same as previous but with missing elements so the representation of the set is bigger
        'Ro+<I>I': lambda x: None, # Variante de R+
        'Ro+<R++': lambda x: None, # Generate sets of rank rank(x) + 2
        'Ro+>R++': lambda x: None, # Same as previous but with missing elements so the representation of the set is bigger
        'Ro+<<E+': lambda x: None, # Variant of R+
        'Roo+II+': lambda x: None, # Variant of R+
        'o+IR>R+': lambda x: Set(*x, rank(x)),
        'o+Io+II': lambda x: Set(*x, Set(*x, x)),
        'o+R>R+I': lambda x: Set(*rank(x), x),
        'oR+R>R+': lambda x: Set.generate_ordinal(x.rank + 2),
        'oR?I<EI': lambda x: Set() if Set() in x else x,
        'oo+IIR+': lambda x: (lambda a: Set(*a, a))(tc(x)), 
        'oo+++II': lambda x: Set(*x, x, Set(*x, x)),
        'ooR++II': lambda x: tc(Set(*x, x))
        },
    (7, 2): {
        'Ro+<+>+': lambda x, y: None, # Generate big sets
        'Ro+<+R?': lambda x, y: None, # ???
        'Ro+>+<+': lambda x, y: None, # Generate big sets
        'Ro+>+R?': lambda x, y: tc(x) if x in y else rxyx(x),
        'Ro+R?<+': lambda x, y: None, # Generate big sets
        'Ro+R?>+': lambda x, y: None, # Generate big sets
        'Ro+R?R?': lambda x, y: None, # Replace occurence of x in y by 1 and then compute the rank of the result set
        'o++o+++': lambda x, y: Set(*x, y, Set(*x, y, Set(*x, y))),
        'o++oR++': lambda x, y: Set(*x, y, tc(Set(*x, y))),
        'o+<I>R+': lambda x, y: Set(*y, tc(x)),
        'o+>I<R+': lambda x, y: Set(*x, tc(y)),
        'o+<R+>I': lambda x, y: Set(*tc(y), x),
        'o+>R+<I': lambda x, y: Set(*tc(x), y),
        'o+oR+++': lambda x, y: Set(*tc(Set(*x, y)), Set(*x, y)),
        'oR?+>I+': lambda x, y: Set() if x in y else Set(*x, y),
        'oo+++++': lambda x, y: Set(*x, y, Set(*x, y), Set(*x, y, Set(*x, y))),
        'ooR++++': lambda x, y: tc(Set(*x, y, Set(*x, y))),
        'oRo++++': lambda x, y: rtc(Set(*x, y)),
        'ooR+R++': lambda x, y: (lambda z: Set(*z, z))(tc(Set(*x, y)))
        },
    (7, 3): {
        'Ro+?<R?': lambda x, y, z: None,
        'Ro+?>R?': lambda x, y, z: None,
        'Ro+?<<+': lambda x, y, z: None,
        'Ro+?<>+': lambda x, y, z: None,
        'Ro+?>>+': lambda x, y, z: None,
        'Ro+<R??': lambda x, y, z: None,
        'Ro+>R??': lambda x, y, z: None,
        'Ro+<<+?': lambda x, y, z: None,
        'Ro+<>+?': lambda x, y, z: None,
        'Ro+>>+?': lambda x, y, z: rxyx(x) if y in z else tc(x),
        'Roo+II?': lambda x, y, z: None,
        'o+<+>>I': lambda x, y, z: Set(*y, z, x),
        'o+>+<<I': lambda x, y, z: Set(*x, y, z),
        'o+R?<<I': lambda x, y, z: Set(*(Set() if y in z else x), z),
        'o+R?<>I': lambda x, y, z: Set(*(Set() if y in z else x), y),
        'o+R?>>I': lambda x, y, z: Set(*(Set() if y in z else x), x),
        'o+<<I>+': lambda x, y, z: Set(*z, Set(*x, y)),
        'o+<<IR?': lambda x, y, z: Set(*z, Set() if y in z else x),
        'o+<>IR?': lambda x, y, z: Set(*y, Set() if y in z else x),
        'o+>>I<+': lambda x, y, z: Set(*x, Set(*y, z)),
        'o+>>IR?': lambda x, y, z: Set(*x, Set() if y in z else x),
        'oR>R+R?': lambda x, y, z: rank(Set() if y in z else x)
        },
}


blacklist = {parse(p) for p in _blacklist}
programs: Dict[Tuple[int, int], Dict[Node, Callable]] = {k: {parse(p): f for p, f in v.items()} for k, v in _programs.items()}
