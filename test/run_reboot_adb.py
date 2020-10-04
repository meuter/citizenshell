from citizenshell import AdbShell, DEBUG
from sys import argv
from os import environ

if argv[1] == "local":
    sh = AdbShell(device=environ.get("TEST_ADB_DEVICE"), log_level=DEBUG, root=True)
elif argv[1] == "remote":
    sh = AdbShell(hostname=environ.get("TEST_ADB_HOST"), log_level=DEBUG, root=True)
sh("ls -a")
sh.reboot_wait_and_reconnect()
sh("ls -a")

