=================
css
=================

The ``css`` command parses css code

Usage
=============================================

.. code-block:: bash

    cparse css [-g] [-c] [-s] <path>

Positional Arguments
=============================================
+------------+---------------------+
| ``<path>`` | a css file to parse |
+------------+---------------------+

Optional Arguments
=============================================
+--------+----------------------------------------------+
| ``-g`` | group identical selector property blocks     |
+--------+----------------------------------------------+
| ``-c`` | condense redundancies within property blocks |
+--------+----------------------------------------------+
| ``-s`` | stack matching selectors in output           |
+--------+----------------------------------------------+
