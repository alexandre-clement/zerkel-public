Welcome to the Zerkel's documentation!
======================================

Zerkel is a primitive recursive programming language developped in Python.
This documentation is embedded in a Docker container. This documentation also
comes with a Jupyter Notebook container to provide interactive examples.

For an in-depth explanation, please see |report|.


.. |report| raw:: html

   <a href="http://localhost:8080/_static/final.pdf" target="_blank">Project report</a>


Notebook Tutorial
-----------------

If you discover the Zerkel language and you are looking for interactive
examples, check out our interactive Jupyter Notebook tutorials.

* **You don't know how a Jupyter Notebook works, follow this**:
  :doc:`link <notebook>`

* **Access to the notebook tutorial** |notebook|.

You can also find the Zerkel's source code in the Jupyter Notebook.

* **Access to the source code** |source|.


.. |notebook| raw:: html

   <a href="http://localhost:8888/tree/notebooks" target="_blank">here</a>

.. |source| raw:: html

   <a href="http://localhost:8888/tree/src" target="_blank">here</a>


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Notebook

   notebook


Model introduction
------------------

* **Introcution to the model elements : pure sets**:
  :doc:`Set introduction <set>`

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Model introduction

   set
   notebooks/set


Language syntax
---------------


* **Discover the tokens**:
  :doc:`Tokens definitions <tokens>`

* **Build your first program**:
  :doc:`Building programs <programs>`

* **Save your programs as macro**:
  :doc:`Macro command <macro>`

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Language syntax

   tokens
   notebooks/tokens
   programs
   macro
   notebooks/tutorial
