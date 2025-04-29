pymdt package
=============

Configuration Arguments
-----------------------
There are several arguments that can be used to control the MDT from within your
python script.  They are extracted from the list of system arguments.  Examples
are provided for each as are details of when you may want to use them.  Often
it is not necessary to use any of them.

These arguments should be defined near the top of your python script file and 
**must be provided before importing anything from pymdt**.

.. code-block:: python
   :caption: **INCORRECT**

       import pymdt
       sys.argv.append("MDT_VERSION=1.4.2520.0")


.. code-block:: python
   :caption: **CORRECT**

       sys.argv.append("MDT_VERSION=1.4.2520.0")
       import pymdt


They are:

MDT_VERSION
^^^^^^^^^^^
The default for this is defined in pymdt\\__init__.py.  This is important because
it tells pymdt where to find the MDT binaries as well as other things.  If the
version listed in pymdt\\__init__.py does not match with your installed version
of MDT, you will need to provide this. The format is major.minor[.build[.revision]]
where each component is an integer value.  For example:


.. code-block:: python

    sys.argv.append("MDT_VERSION=1.4.2520.0")

Given this and absent an explicitly provided :ref:`MDT_BIN_DIR` (see below), the MDT
will look for MDT binaries in an installation folder that looks like:

C:\\Program Files\\Sandia National Laboratories\\Microgrid Design Toolkit v1.4.2520.0


MDT_BIN_DIR
^^^^^^^^^^^
The location in which pymdt will look for MDT binaries to use.  This should be
a folder into which the MDT has been installed on your computer.  It is typically
something like:

C:\\Program Files\\Sandia National Laboratories\\Microgrid Design Toolkit v1.4.2520.0

Where the version listed at the end is either the default version defined in
pymdt\\__init__.py or was provided as the :ref:`MDT_VERSION` (see above).  You should use this
value when your MDT installation is in a folder that does not follow the pattern.
For instance, if it was installed on a drive other than the C drive or if there
are any other path differences from what's shown above (other than the version number).

.. note::
    If you use this setting, :ref:`MDT_VERSION` will be ignored for the purpose of
    finding the binaries.  The path provided here should be a complete path
    to the MDT installation directory.
    
.. code-block:: python

    sys.argv.append("MDT_BIN_DIR=<path to MDT binaries>")
    

MDT_DATA_DIR
^^^^^^^^^^^^
The location in which pymdt will look for the file (been.invoked) whose presence
tells the MDT whether or not this is the first invocation of the software.  The
location provided will have the version number appended.  This is typically

C:\\ProgramData\\Sandia National Laboratories\\Microgrid Design Toolkit\\1.4.2520.0

Of course, the version number at the end will align with your current version.
It should be rare that you need to provide this input.

.. note::
    Unlike the :ref:`MDT_BIN_DIR`, the version number will be appended to this input.
    For example, if you provide "D:\\My\\Custom\\Directory" as your input, the
    final folder used will be "D:\\My\\Custom\\Directory\\1.4.2520.0" created by
    appending the provided directory with the :ref:`MDT_VERSION`.
    
.. code-block:: python

    sys.argv.append("MDT_DATA_DIR=<path to MDT data directory>")
    

MDT_SPEC_DB_DIR
^^^^^^^^^^^^^^^
The directory in which the specification DB is located.  The default for this is

C:\\Users\\Public\\Documents\\Microgrid Design Toolkit v1.4.2520.0

Where the version number is the current version of the MDT you have installed.
If you keep your database in a non-standard location, you can provide that path
in this input.

The path provided will be considered complete.  Nothing will be appended to it
including the :ref:`MDT_VERSION`.

.. code-block:: python

    sys.argv.append("MDT_SPEC_DB_DIR=<path to MDT spec DB>")


Submodules
----------

pymdt.core module
^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.core
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.distributions module
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.distributions
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.io module
^^^^^^^^^^^^^^^

.. automodule:: pymdt.io
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.metrics module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.metrics
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.missions module
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.missions
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.results module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.results
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.solving module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.solving
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.specs module
^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.specs
   :members:
   :undoc-members:
   :show-inheritance:

pymdt.utils module
^^^^^^^^^^^^^^^^^^

.. automodule:: pymdt.utils
   :members:
   :undoc-members:
   :show-inheritance:
