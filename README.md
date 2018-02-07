# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is (or rather will be) a python library allowing to execute shell commands
either locally or remotely over several protocols (telnet, ssh, serial or adb) using a consistent
and uniform API. This library is compatible with both python 2 (2.7) and 3 (>=3.4) as well as 
with [PyPy](https://pypy.org/). For now, it focuses on POSIX platforms like Linux and MacOS, 
but may be extended to work to Windows based platform in the future. It is distributed under
[MIT](https://opensource.org/licenses/MIT) license.

## Roadmap

#### Version 1.0
- [x] local shell
- [x] shell over ssh using [paramiko](http://www.paramiko.org/)
- [x] shell over telnet using telnetlib
- [ ] shell over [adb](https://developer.android.com/studio/command-line/adb.html)
- [ ] shell over serial using [pyserial](https://github.com/pyserial/pyserial)
- [x] support for logging with colored formatter 
- [ ] available from PIP repository

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

you can then do eveything you can do with a `LocalShell`. Beware that some SSH servers 
refuse to set environment variable (see documentation of AcceptEnv of 
[sshd_config](https://linux.die.net/man/5/sshd_config) and documentation of `update_environment` of [paramiko's `Channel` class](http://docs.paramiko.org/en/2.4/api/channel.html)) and that will fail silently.