# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is (or rather will be) a python library allowing to execute shell commands either locally or remotely 
over several protocols (telnet, ssh, serial or adb) using a consistent and uniform API. This library is compatible with
both python 2 (>=2.5) and 3 (>=3.4) as well  [PyPy](https://pypy.org/). For now, it focuses on POSIX platform like
Linux and MacOS, but may be extended to Windows based platform in the future.

## Example

```python
from citizenshell import LocalShell

shell = LocalShell(GREET="Hello")
shell["FIRST"] = 'Citizen'
assert shell("echo $GREET $FIRST $LAST", LAST="Shell") == "Hello Citizen Shell"
```