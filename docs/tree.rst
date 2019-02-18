
=================
tree
=================

The ``tree`` command prints file trees

Usage
-----------------------------------------

``cparse tree [-h] [-a] [-n DEPTH] [-fmt FORMAT] [-wc PATTERN | -grep REGEXP | -ft FILETYPE] [-exc PATH] [-inc PATH] [path]``

Positional Arguments
"""""""""""""""""""""""""

+----------+---------------------+
| ``path`` | tree root directory |
+----------+---------------------+

Optional Arguments
"""""""""""""""""""""""""

+------------------+-------------------------------+
| ``-a``           | include hidden files          |
+------------------+-------------------------------+
| ``-n DEPTH``     | max tree depth                |
+------------------+-------------------------------+
| ``-fmt FORMAT``  | display format for tree nodes |
+------------------+-------------------------------+
| ``-wc PATTERN``  | wild card pattern             |
+------------------+-------------------------------+
| ``-grep REGEXP`` | regular expression to match   |
+------------------+-------------------------------+
| ``-ft FILETYPE`` | file type filter              |
+------------------+-------------------------------+
| ``-exc PATH``    | paths to exclude from tree    |
+------------------+-------------------------------+
| ``-inc PATH``    | paths to include in tree      |
+------------------+-------------------------------+
