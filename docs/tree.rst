
=================
tree
=================

The ``tree`` command prints file trees


Usage
-----------------------------------------

``cparse tree [-h] [-a] [-f FORMAT] [-p pattern | -r regexp | -t filetype] [-exc path] [-inc path] [path]``


Positional Arguments
"""""""""""""""""""""""""

+----------+---------------------+
| ``path`` | tree root directory |
+----------+---------------------+

Optional Arguments
"""""""""""""""""""""""""

+-------------------------------+----------------------------+
| ``-a``                        | include hidden files       |
+-------------------------------+----------------------------+
| ``-f format``                 | display format for files   |
+-------------------------------+----------------------------+
| ``-p pattern``                | wild card pattern          |
+-------------------------------+----------------------------+
| ``-r regexp``                 | regexp match pattern       |
+-------------------------------+----------------------------+
| ``-t filetype``               | file type filter           |
+-------------------------------+----------------------------+
| ``-exc path, --exclude path`` | paths to exclude from tree |
+-------------------------------+----------------------------+
| ``-inc path, --include path`` | paths to include in tree   |
+-------------------------------+----------------------------+
