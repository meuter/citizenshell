# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is (or rather will be) a python library allowing to execute shell commands either locally or remotely 
over several protocols (telnet, ssh, serial or adb) using a consistent and uniform API. This library is compatible with
both python 2 (>=2.5) and 3 (>=3.4) as well  [PyPy](https://pypy.org/). For now, it focuses on POSIX platform like
Linux and MacOS, but may be extended to Windows based platform in the future.

## Roadmap

#### Version 1.0
- [x] local shell
- [ ] shell over telnet using telnetlib
- [ ] shell over ssh using paramiko
- [ ] shell over adb
- [ ] shell over serial using pyserial

## Examples

#### LocalShell

you can use the built-in `sh` command for simple commands:

```python
from citizenshell import sh

assert sh("echo Hello World") == "Hello World"
```

you can instanciate a `LocalShell` for more complex cases:

```python
from citizenshell import LocalShell

shell = LocalShell(GREET="Hello")
assert shell("echo $GREET $WHO", WHO="Citizen") == "Hello Citizen"
```

you can also iterate over stdout:

```python
from citizenshell import LocalShell

shell = LocalShell()
result = [int(x) for x in shell("""
    for i in 1 2 3 4; do
        echo $i;
    done
""")]
assert result == [1, 2, 3, 4]
```

or you can extract stdout, stderr and exit code seperately:

```python
from citizenshell import LocalShell

shell = LocalShell()
result = shell(">&2 echo error && echo output && exit 13")
assert result.out == ["output"]
assert result.err == ["error"]
assert result.xc == 13
```

