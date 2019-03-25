# cparse

[![PyPI version shields.io](https://img.shields.io/pypi/v/cparse.svg?style=flat-square)](https://pypi.python.org/pypi/cparse/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/cparse.svg?style=flat-square)](https://pypi.python.org/pypi/cparse/)
[![PyPI license](https://img.shields.io/pypi/l/cparse.svg?style=flat-square)](https://pypi.python.org/pypi/cparse/)
[![readthedocs](https://readthedocs.org/projects/cparse/badge/?version=latest&style=flat-square)](https://cparse.readthedocs.io)

Code parsing command line tool.


## Installation

With `pip` via [PyPi](https://pypi.org)

```bash
pip install cparse
```

Clone the repository and install

```bash
git clone git://github.com/luciancooper/cparse.git
cd cparse
python setup.py install
```

## Documentation
Full documentation can be found [**here**](https://cparse.readthedocs.io)

`cparse ` currently includes 6 commands

 * [`ls`](#ls) - list files in directory
 * [`tree`](#tree) - print file tree
 * [`stat`](#stat) - directory file extension stats
 * [`py`](#py) - python code parsing
 * [`html`](#html) - html link parsing
 * [`css`](#css) - css code parsing

### `ls`
Prints a list of the files in a directory. 

```bash
cparse ls [-r] [-n <depth>] [-d | -f] [-a] [-lim <count>] [-fmt <format>]
          [-exc <path>] [-inc <path>]
          [-wc <pattern>] [-grep <regexp>] [-ft <filetype>]
          [-m | -M | -c | -C | -b | -B | -i | -I | -g | -G] <path>
```

### `tree`
Prints a tree representation of the contents of a directory.

```bash
cparse tree [-d | -f] [-a] [-n <depth>] [-fmt <format>]
            [-exc <path>] [-inc <path>]
            [-wc <pattern>] [-grep <regular-expression>] [-ft <file-extension>]
            [-m | -M | -c | -C | -b | -B | -i | -I | -g | -G] <path>
```

### `stat`

Prints a table displaying the file extension proportions of a directory

```bash
cparse stat [-a] <path>
```

### `py`

Parses the code of a provided python file

```bash
cparse py <path>
```

### `html`

Parses the links in an HTML file and represents them as a file tree.

```bash
cparse html <path>
```

### `css`

Parses CSS code, providing options to condense redundant rules and group identical selectors. 

```bash
cparse css [-g] [-c] [-s] <path>
```


## Dependencies

 * [pydecorator](https://github.com/luciancooper/pydecorator)
