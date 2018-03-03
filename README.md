# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is (or rather will be) a python library allowing to execute shell commands either locally or remotely over several protocols (telnet, ssh, serial or adb) using a simple and consistent API. This library is compatible with both python 2 (2.7) and 3 (>=3.4) as well as with [PyPy](https://pypy.org/). For now, it focuses on POSIX platforms like Linux and MacOS, but may be extended to work to Windows based platform in the future. It is distributed under
[MIT](https://opensource.org/licenses/MIT) license.

## Installing

__citizenshell__ can simply installed using `pip install citizenshell`

## Examples

### LocalShell

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
assert result.stdout() == ["output"]
assert result.stderr() == ["error"]
assert result.exit_code() == 13
```

### TelnetShell

you can instanciate the `TelnetShell` for shell over telnet:

```python
from citizenshell import TelnetShell

shell = TelnetShell(hostname="acme.org", username="john", password="secretpassword")
assert shell("echo Hello World") == "Hello World"
```

you can then do eveything you can do with a `LocalShell`.

### SecureShell

you can instanciate the `SecureShell` for shell over SSH:

```python
from citizenshell import SecureShell

shell = SecureShell(hostname="acme.org", username="john", password="secretpassword")
assert shell("echo Hello World") == "Hello World"
```

you can then do eveything you can do with a `LocalShell`.

### AdbShell

you can instanciate the `AdbShell` for shell over ADB:

```python
from citizenshell import AdbShell

shell = AdbShell(hostname="acme.org", username="john", password="secretpassword")
assert shell("echo Hello World") == "Hello World"
```

you can then do eveything you can do with a `LocalShell`.

### SerialShell

you can instanciate the `SerialShell` for shell over serial line:

```python
from serial import EIGHTBITS, PARITY_NONE
from citizenshell import SerialShell

shell = SerialShell(port="/dev/ttyUSB3", username="john", password="secretpassword", baudrate=115200, parity=PARITY_NONE, bytesize=EIGHTBITS)
assert shell("echo Hello World") == "Hello World"
```

you can then do eveything you can do with a `LocalShell`.

### Shell

you can also obtain shell objects by URI using the `Shell` function:

```python
from citizenshell import Shell

localshell = Shell()
telnetshell = Shell("telnet://john:secretpassword@acme.org:1234")
secureshell = Shell("ssh://john:secretpassword@acme.org:1234")
adbshell = Shell("adb://myandroiddevice:5555")
serialshell = Shell("serial://jogn:secretpassword@/dev/ttyUSB3?baudrate=115200")
```

you can mix and match betweens providing arguments in the URI or via kwargs:

```python
from citizenshell import Shell

localshell = Shell()
telnetshell = Shell("telnet://john@acme.org", password="secretpassword", port=1234)
serialshell = Shell("serial://john:secretpassword@/dev/ttyUSB3", baudrate=115200)
```

you can then use the shell objects as you would any other.
