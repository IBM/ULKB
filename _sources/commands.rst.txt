========
Commands
========

.. currentmodule:: ulkb

Commands are top-level functions that operate on the top :class:`Theory`.

.. autosummary::
   :toctree: generated/

   _thy

Adding extensions
-----------------

.. autosummary::
   :toctree: generated/

   extend
   new_base_type
   new_type_constructor
   new_constant
   new_axiom
   new_definition
   new_theorem
   new_python_type_alias

Removing extensions
-------------------

.. autosummary::
   :toctree: generated/

   reset

Querying extensions
-------------------

.. autosummary::
   :toctree: generated/

   enumerate_extensions
   lookup_extension
   lookup_type_constructor
   lookup_constant
   lookup_axiom
   lookup_definition
   lookup_theorem
   lookup_python_type_alias

Showing extensions
------------------

.. autosummary::
   :toctree: generated/

   show_extensions
   show_type_constructors
   show_constants
   show_axioms
   show_definitions
   show_theorems
   show_python_type_aliases

Settings
--------

The settings table of the top theory resides in constant :const:`settings`.

.. autosummary::
   :toctree: generated/

   settings

.. currentmodule:: ulkb

See :attr:`Theory.settings`.
