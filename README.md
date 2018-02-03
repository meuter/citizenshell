# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is (or rather will be) a python library allowing to execute shell commands either locally or remotely 
over several protocols (telnet, ssh, serial or adb) using a consistent and uniform API. This library is compatible with
both python 2 (>=2.5) and 3 (>=3.4) as well  [PyPy](https://pypy.org/).

## Example

```python
from citizenshell import LocalShell

shell = LocalShell()
shell["WHO"] = 'Citizen'
assert shell("echo 'Hello $WHO'") == "Hello Citizen"
```