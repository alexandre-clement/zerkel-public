Tokens definitions
==================


Initial Tokens
--------------

The 9 language tokens, each consisting of a single character:

1. :code:`E` is the function of arity 0
returning the empty set :math:`\emptyset`.

.. math::
    [f_0]: () \mapsto \emptyset

2. :code:`I` is the **identity** function of arity 1.

.. math::
    [f_1]: (x) \mapsto x

3. :code:`+` is the function of arity 2 returning
which adds the second set into the first one.

.. math::
    [f_2]: (x,y)\mapsto x\cup\{y\}

4. :code:`?` is the function of arity 4 which
checks if the third arguments is in the last one,
if so, then it returns the first arguments, the second one otherwise.

.. math::
    [f_4]: (x,y,u,v)\mapsto \mbox{if }u\in v\mbox{ then }x\mbox{ else }y

Projectors
----------

5. :code:`<` is the function that takes a
function :math:`f_n` of arity n and
transform it to a function :math:`f_{n+1}` with an
additional argument in **first** position.

.. math::
    [\color{#cb17ce}{f_n} \rightarrow f_{n+1}]:
    \color{#dc5610}<\color{#cb17ce}{f_n}(x,\bar{y})
    \mapsto \color{#cb17ce}{f_n}(\bar{y})

6. :code:`>` is the function that takes a
function :math:`f_n` of arity n and
transform it to a function :math:`f_{n+1}`
with an additional argument in **last** position.

.. math::
    [\color{#cb17ce}{f_n} \rightarrow f_{n+1}]: \color{#dc5610}>
    \color{#cb17ce}{f_n}(\bar{y}, x)\mapsto \color{#cb17ce}{f_n}(\bar{y})

Operators
---------

7. :code:`o` is the **composition** function.

.. math::
    [\color{#cb17ce}{f_{n+1}}, \color{#126ed5}{f_p\times(n+1)}
    \rightarrow f_{p}]: \color{#dc5610}o \color{#cb17ce}{f_{n+1}}
    \color{#126ed5}{f_p^1 f_p^2 \dots f_p^{n+1}}(\bar{x}) \mapsto
    \color{#cb17ce}{f_{n+1}}(\color{#126ed5}{f_p^1}(\bar{x}),
    \color{#126ed5}{f_p^2}(\bar{x}), \color{#126ed5}{\dots},
    \color{#126ed5}{f_p^{n+1}}(\bar{x}))

8. :code:`R` is the function of arity 0
returning the empty set :math:`\emptyset`.

.. math::
    [\color{#cb17ce}{f_{n+2}} \rightarrow f_{n+1}]: \color{#dc5610}{R}
    \color{#cb17ce}{f_{n+2}}(x,\bar{y}) \mapsto \color{#cb17ce}
    {f_{n+2}}\left(\bigcup_{z\in x} \color{#cb17ce}
    {f_{n+2}}(z,\bar{y}), x, \bar{y}\right)

9. :code:`!` is the function that takes 2
functions f and g as arguments such as:

.. math::
    [(\color{#cb17ce}{f_{n+2}}, \color{#126ed5}{g_{n+2}} \rightarrow h_{n+2}]:
    \color{#dc5610}!\color{#cb17ce}{f_{n+2}}
    \color{#126ed5}{g_{n+2}}(\bar{x},u,v) \mapsto
    \mbox{if }u\in v\mbox{ then } \color{#cb17ce}{f_{n+2}}(\bar{x}, u, v)
    \mbox{ else } \color{#126ed5}{g_{n+2}}(\bar{x}, u, v)
