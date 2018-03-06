# citizenshell [![Build Status](https://travis-ci.org/meuter/citizenshell.svg?branch=master)](https://travis-ci.org/meuter/citizenshell)

__citizenshell__ is a python library allowing to execute shell commands either locally or remotely over several protocols (telnet, ssh, serial or adb) using a simple and consistent API. This library is compatible with both python 2 (2.7) and 3 (>=3.4) as well as with [PyPy](https://pypy.org/). For now, it focuses on POSIX platforms like Linux and MacOS, but may be extended to work to Windows based platform in the future. It is distributed under
[MIT](https://opensource.org/licenses/MIT) license.

## Installation

__citizenshell__ can simply installed using `pip install citizenshell`

## Obtaining a shell

First you need a shell. For that you have several options:

1. use the built-in `LocalShell` for quick access:

    ```python
    from citizenshell import sh
    ```

2. you can instanciate your own `LocalShell`:

    ```python
    from citizenshell import LocalShell

    shell = LocalShell()
    ```

3. you can instanciate the `TelnetShell` for shell over telnet:

    ```python
    from citizenshell import TelnetShell

    shell = TelnetShell(hostname="acme.org", username="john",
                        password="secretpassword")
    ```

4. you can instanciate the `SecureShell` for shell over SSH:

    ```python
    from citizenshell import SecureShell

    shell = SecureShell(hostname="acme.org", username="john",
                        password="secretpassword")
    ```

5. you can instanciate the `AdbShell` for shell over ADB:

    ```python
    from citizenshell import AdbShell

    shell = AdbShell(hostname="acme.org", username="john",
                     password="secretpassword")
    ```

6. you can instanciate the `SerialShell` for shell over serial line:

    ```python
    from serial import EIGHTBITS, PARITY_NONE
    from citizenshell import SerialShell

    shell = SerialShell(port="/dev/ttyUSB3", username="john",
                        password="secretpassword",
                        baudrate=115200, parity=PARITY_NONE, bytesize=EIGHTBITS)
    ```

7. you can also obtain shell objects by URI using the `Shell` function:

    ```python
    from citizenshell import Shell

    localshell = Shell()
    telnetshell = Shell("telnet://john:secretpassword@acme.org:1234")
    secureshell = Shell("ssh://john:secretpassword@acme.org:1234")
    adbshell = Shell("adb://myandroiddevice:5555")
    serialshell = Shell("serial://jogn:secretpassword@/dev/ttyUSB3?baudrate=115200")
    ```

    you can also mix and match betweens providing arguments in the URI or via kwargs:

    ```python
    telnetshell = Shell("telnet://john@acme.org", password="secretpassword", port=1234)
    serialshell = Shell("serial://john:secretpassword@/dev/ttyUSB3", baudrate=115200)
    ```

## Using a shell

Once you have shell, any shell, you can call it directly and get the standart output:

```python
assert shell("echo Hello World") == "Hello World"
```

or you can also iterate over the standard output:

```python
result = [int(x) for x in shell("""
    for i in 1 2 3 4; do
        echo $i;
    done
""")]
assert result == [1, 2, 3, 4]
```

you don't have to wait for the command to finish to recieve the lines:

```python
for line in shell("for i in 1 2 3 4; do echo -n 'It is '; date +%H:%M:%S; sleep 1; done", wait=False)
    print ">>>", line + "!"
```

would produce something like:

```text
>>> It is 14:24:52!
>>> It is 14:24:53!
>>> It is 14:24:54!
>>> It is 14:24:55!
```

you can extract stdout, stderr and exit code seperately:

```python
result = shell(">&2 echo error && echo output && exit 13")
assert result.stdout() == ["output"]
assert result.stderr() == ["error"]
assert result.exit_code() == 13
```

you can inject environment variable to the shell

```python
assert shell("echo $VAR", VAR="bar") == "bar"
```

or have the shell raise an exception if the exit code is non-zero:

```python
assert shell("exit 13").exit_code() == 13 # will not raise any exception
try:
    shell("exit 13", check_xc=True) # will raise an exception
    assert False, "will not be reached"
except ShellError as e:
    assert True, "will be reached"
```

the shell can also raise an exception if something is printed on the standard error:

```python
shell("echo DANGER >&2").stderr() == ["DANGER"] # will not raise any exception
try:
    shell("echo DANGER >&2", check_err=True) # will raise an exception
    assert False, "will not be reached"
except ShellError as e:
    assert True, "will be reached"
```

you can pull file from the remote host (for `LocalShell` it's just doing a copy):

```python
shell("echo -n test > remote_file.txt")
shell.pull("local_file.txt", "remote_file.txt")
assert open("local_file.txt", "r").read() == "test"
```

or push file to the remote host (again, for `LocalShell` it's just doing a copy):

```python
open("local_file.txt", "w").write("test")
shell.push("local_file.txt", "remote_file.txt")
assert str(shell("cat remote_file.txt")) == "test"
```
