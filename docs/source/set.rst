Set introduction
=================

Our model manipulate pure sets from the set theory.
A set is pure if it contains only pure sets.
That is, all elements of the set are themselves sets,
as are all elements of the elements, and so on.


In our language, we provide a specific object called `Set` to
represents the pure sets of the set theory.

Properties
-----------

We define several properties on the sets of our model
to facilitate their use and understanding.

* **Rank** we define the rank of a set as its depth, we thus have :

.. math::
    \begin{align}
        rank(\emptyset) & = 0 \\
        rank(x) & = \underset{u \in x}{sup}(rank(u) + 1) \\
    \end{align}

Note that in our model, our sets are well-founded, which means that they can
not contain themselves.

* **Cardinality** The cardinality of a set is
  the number of elements it contains.


Pairing function
----------------

For the case of finite sets, we can associate an unique integer n to any
set z as follows:

.. math::
    |z| = \displaystyle\sum_{u \in z}{2^{|u|}} = n

For example:

.. math::
    \begin{aligned}
        \emptyset & \mbox{ is } 0 \\
        \{\emptyset\} & \mbox{ is } 2^{|\{\}|} = 2^0 = 1 \\
        \{\{\emptyset\}\} & \mbox{ is } 2^{|\{\emptyset\}|} = 2^1 = 2 \\
        \{\emptyset, \{\{\emptyset\}\}\} & \mbox{ is } 2^{|\emptyset|} + 2^{|\{\emptyset\}|} = 2^0 + 2^1 = 3 \\
    \end{aligned}

Ordinals
---------

We use the Von Neumann ordinals which defines the natural numbers as follows :

* the set :math:`\{\} = 0 = \emptyset`
* :math:`n + 1 = n \cup \{n\} = S(n)`

It follows that each natural number is equal to the set of all
natural numbers less than it:

* :math:`0 = \{\} = \emptyset`
* :math:`1 = \{0\} = \{\{\}\}`
* :math:`2 = \{0, 1\} = \{\{\}, \{\{\}\}\}`
* :math:`3 = \{0, 1, 2\} = \{\{\}, \{\{\}\},
  \{\{\}, \{\{\}\}\}\}`
* :math:`4 = \{0, 1, 2, 3\} = \{\{\}, \{\{\}\}, \{\{\},
  \{\{\}\}\}, \{\{\}, \{\{\}\}, \{\{\}, \{\{\}\}\}\}\}`
* etc.

Data structures
---------------

The sets of our model provides good representation for data structures
like couple, tuple or list.

* **couples** are sets that contains exactly 2 elements in a specific order.
  To represent a couple, we use the Kuratowski representation, which defines
  couple as follows : :math:`(x,y) = \{\{x\}, \{x, y\}\}`.

* **tuples** we can extend the definition of couples to build tuples of
  any number of elements. We define a tuple as follow :
  :math:`(e_1, e_2, \dots, e_n) = (e_1, (e_2, \dots, e_n))`.

* **list** for the list, we start by defining the empty
  list as :math:`[] = \emptyset`. Then the list that contains
  :math:`x` as the couple :math:`(x, [])` such as
  :math:`[x] = (x, []) = (x, \emptyset)`. In the general case,
  the list :math:`[x_1, x_2, \dots, x_n] = (x_1, [x_2, \dots, x_n])`.
