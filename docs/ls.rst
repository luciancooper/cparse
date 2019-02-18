=================
ls
=================

The ``ls`` command lists the files in a directory


Usage
-----------------------------------------

``cparse ls [-h] [-r] [-n DEPTH] [-a] [-lim COUNT] [-fmt FORMAT] [-wc PATTERN | -grep REGEXP | -ft FILETYPE] [-type ARG] [-sort ARG] [-exc PATH] [-inc PATH] [path]``


Positional Arguments
"""""""""""""""""""""""""

+----------+----------------+
| ``path`` | root directory |
+----------+----------------+


Optional Arguments
"""""""""""""""""""""""""

+------------------+-----------------------------------------------------+
| ``-r``           | list files recursively                              |
+------------------+-----------------------------------------------------+
| ``-n DEPTH``     | max depth if recursive flag is specified            |
+------------------+-----------------------------------------------------+
| ``-a``           | include hidden files                                |
+------------------+-----------------------------------------------------+
| ``-lim COUNT``   | maximum items to list in output                     |
+------------------+-----------------------------------------------------+
| ``-fmt FORMAT``  | display format for listed items                     |
+------------------+-----------------------------------------------------+
| ``-wc PATTERN``  | wild card pattern                                   |
+------------------+-----------------------------------------------------+
| ``-grep REGEXP`` | regular expression to match                         |
+------------------+-----------------------------------------------------+
| ``-ft FILETYPE`` | file type filter                                    |
+------------------+-----------------------------------------------------+
| ``-type ARG``    | specify to include either files or directories only |
+------------------+-----------------------------------------------------+
| ``-sort ARG``    | sort output list by created or modified timestamp   |
+------------------+-----------------------------------------------------+
| ``-exc PATH``    | paths to exclude if recursive flag is specified     |
+------------------+-----------------------------------------------------+
| ``-inc PATH``    | paths to include if recursive flag is specified     |
+------------------+-----------------------------------------------------+
