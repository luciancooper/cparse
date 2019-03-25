
=================
tree
=================

The ``tree`` command prints file trees

Usage
=============================================

.. code-block:: bash

    cparse tree [-d | -f] [-a] [-n <depth>] [-fmt <format>] 
                [-exc <path>] [-inc <path>] 
                [-wc <pattern>] [-grep <regular-expression>] [-ft <file-extension>] 
                [-m | -M | -c | -C | -b | -B | -i | -I | -g | -G] <path>

Positional Arguments
=============================================
+------------+---------------------+
| ``<path>`` | tree root directory |
+------------+---------------------+

Optional Arguments
=============================================
+-------------------+--------------------------------------------+
| ``-d``            | dirs only flag                             |
+-------------------+--------------------------------------------+
| ``-f``            | files only flag (ignore empty directories) |
+-------------------+--------------------------------------------+
| ``-a``            | include hidden files                       |
+-------------------+--------------------------------------------+
| ``-n <depth>``    | max tree depth                             |
+-------------------+--------------------------------------------+
| ``-fmt <format>`` | display format for tree nodes              |
+-------------------+--------------------------------------------+


Sorting Flags
=============================================
Control the order in which files are listed within each branch of the tree. *Only one of the following flags can be specified.*

+--------+--------------------------------------------+
| ``-m`` | sort by modified time (most recent first)  |
+--------+--------------------------------------------+
| ``-M`` | sort by modified time (least recent first) |
+--------+--------------------------------------------+
| ``-c`` | sort by created time (newest first)        |
+--------+--------------------------------------------+
| ``-C`` | sort by created time (oldest first)        |
+--------+--------------------------------------------+
| ``-b`` | sort by size (largest first)               |
+--------+--------------------------------------------+
| ``-B`` | sort by size (smallest first)              |
+--------+--------------------------------------------+
| ``-i`` | sort by inode (descending)                 |
+--------+--------------------------------------------+
| ``-I`` | sort by inode (ascending)                  |
+--------+--------------------------------------------+
| ``-g`` | group files by file extension (descending) |
+--------+--------------------------------------------+
| ``-G`` | group files by file extension (ascending)  |
+--------+--------------------------------------------+

Pruning Arguments:
=============================================
Control which sub directories to include in tree. *These arguments can be specified multiple times.*

+-----------------+--------------------------------+
| ``-exc <path>`` | sub paths to exclude from tree |
+-----------------+--------------------------------+
| ``-inc <path>`` | sub paths to include in tree   |
+-----------------+--------------------------------+


Filtering Arguments
=============================================
Apply filters to control which files are included in the tree.

+--------------------------------+-----------------------------+
| ``-wc <pattern>``              | wild card pattern           |
+--------------------------------+-----------------------------+
| ``-grep <regular-expression>`` | regular expression to match |
+--------------------------------+-----------------------------+
| ``-ft <file-extension>``       | file type filter            |
+--------------------------------+-----------------------------+
