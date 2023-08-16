======
Theory
======

.. currentmodule:: ulkb

.. autoclass:: Theory
   :no-members:
   :show-inheritance:

Theory stack
------------

.. autosummary::
   :toctree: generated/

   Theory.top
   Theory.push
   Theory.pop

Adding extensions
-----------------

.. autosummary::
   :toctree: generated/

   Theory.extend
   Theory.new_base_type
   Theory.new_type_constructor
   Theory.new_constant
   Theory.new_axiom
   Theory.new_definition
   Theory.new_theorem
   Theory.new_python_type_alias

Removing extensions
-------------------

.. autosummary::
   :toctree: generated/

   Theory.reset

Querying extensions
-------------------

.. autosummary::
   :toctree: generated/

   Theory.enumerate_extensions
   Theory.lookup_extension
   Theory.lookup_type_constructor
   Theory.lookup_constant
   Theory.lookup_axiom
   Theory.lookup_definition
   Theory.lookup_theorem
   Theory.lookup_python_type_alias

Showing extensions
------------------

.. autosummary::
   :toctree: generated/

   Theory.show_extensions

Modules
-------

.. autosummary::
   :toctree: generated/

   Theory.load

Prelude
-------

.. autosummary::
   :toctree: generated/

   Theory.prelude
   Theory.get_prelude
   Theory.prelude_offset
   Theory.get_prelude_offset
   Theory.args_no_prelude
   Theory.get_args_no_prelude

Settings
--------

.. autosummary::
   :toctree: generated/

   Theory.settings
   Theory.get_settings

The theory settings table is an instance of :class:`TheorySettings`.

.. autoclass:: TheorySettings
   :no-members:

.. autosummary::
   :toctree: generated/

   TheorySettings.graph
   TheorySettings.converter
   TheorySettings.parser
   TheorySettings.serializer
   TheorySettings.generated_id_prefix
   TheorySettings.record_proofs
   TheorySettings.override_object_repr
   TheorySettings.debug
