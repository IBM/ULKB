# ULKB #

The Universal Logic Knowledge Base (ULKB) is a HOL-based framework for
reasoning over knowledge graphs.

It consists of two main components:

1. **ULKB Logic**. A higher-order logic (HOL) language and interactive
   theorem-prover like environment for reasoning over knowledge graphs.

2. **ULKB Graph**.  A core knowledge graph in augmented by a federation of
   external knowledge bases.

This repository contains the source code of ULKB Logic (i.e., the Python
library `ulkb`). Code examples and tutorials can be found under
[examples](./examples).  For more detailed documentation, see the [Reference
Manual](https://github.ibm/IBM/ULKB/).

(The ontology files of the ULKB Graph can be found under [graph](./graph).
The ULKB Logic code does not depend on these files.)

## Directory structure ##

- [docs](./docs): Reference manual.
- [docs_src](./docs_src): Reference manual sources.
- [examples](./examples): Code examples and tutorials.
- [graph](./graph): Ontology files and graph generation code.
- [tests](./tests): Testing code.
- [ulkb](./ulkb): `ulkb` library sources.

## Installation ##

```shell
$ git clone https://github.com/IBM/ULKB
$ cd ULKB
$ pip install -e .
```

## Testing ##

Install the test dependencies:
```shell
$ make install-deps
```

Run all tests:
```shell
$ make check
```
