=================
ls
=================

The ``ls`` command lists the files in a directory


Usage
=============================================

.. code-block:: bash

    cparse ls [-r] [-n <depth>] [-d | -f] [-a] [-lim <count>] [-fmt <format>] 
              [-exc <path>] [-inc <path>] 
              [-wc <pattern>] [-grep <regexp>] [-ft <filetype>] 
              [-m | -M | -c | -C | -b | -B | -i | -I | -g | -G] <path>


Positional Arguments
=============================================
+------------+----------------+
| ``<path>`` | root directory |
+------------+----------------+

Optional Arguments
=============================================
+-------------------+------------------------------------------+
| ``-r``            | list files recursively                   |
+-------------------+------------------------------------------+
| ``-n <depth>``    | max depth if recursive flag is specified |
+-------------------+------------------------------------------+
| ``-d``            | dirs only flag                           |
+-------------------+------------------------------------------+
| ``-f``            | files only flag                          |
+-------------------+------------------------------------------+
| ``-a``            | include hidden files                     |
+-------------------+------------------------------------------+
| ``-lim <count>``  | maximum items to list in output          |
+-------------------+------------------------------------------+
| ``-fmt <format>`` | display format for listed items          |
+-------------------+------------------------------------------+


Sorting Flags
=============================================
Control the order in which files are listed. *Only one of the following flags can be specified.*

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

Pruning Arguments
=============================================
Control which sub directories to include when recursive flag is specified. *These arguments can be specified multiple times.* 

+-----------------+----------------------+
| ``-exc <path>`` | sub paths to exclude |
+-----------------+----------------------+
| ``-inc <path>`` | sub paths to include |
+-----------------+----------------------+

Filtering Arguments
=============================================
Apply filters to control which files are listed.

+--------------------------------+-----------------------------+
| ``-wc <pattern>``              | wild card pattern           |
+--------------------------------+-----------------------------+
| ``-grep <regular-expression>`` | regular expression to match |
+--------------------------------+-----------------------------+
| ``-ft <file-extension>``       | file type filter            |
+--------------------------------+-----------------------------+
