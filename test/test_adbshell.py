from os import environ
from citizenshell import AdbShell
from pytest import skip
from shelltester import AbstractShellTester
from subprocess import check_output


class TestAbdShellRemote(AbstractShellTester):
    @classmethod
    def setup_class(cls):
        if "TEST_ADB_HOST" in environ:
            check_output("adb disconnect", shell=True)
        else:
            skip("need to define TEST_ADB_HOST environment variable")

    @classmethod
    def teardown_class(cls):
        if "TEST_ADB_HOST" in environ:
            check_output("adb disconnect", shell=True)

    def instanciate_new_shell(self, *args, **kwargs):
        hostname = environ.get("TEST_ADB_HOST")
        return AdbShell(hostname=hostname, root=True, *args, **kwargs)


class TestAdbShellLocalDefault(AbstractShellTester):
    @classmethod
    def setup_class(cls):
        local, remote = AdbShell.list_available_devices()
        only_one_local_device = len(local) == 1 and len(remote) == 0
        if not only_one_local_device:
            skip("more than one device found")

    def instanciate_new_shell(self, *args, **kwargs):
        return AdbShell(root=True, *args, **kwargs)


class TestAdbShellUsbSpecific(AbstractShellTester):
    @classmethod
    def setup_class(cls):
        local, _ = AdbShell.list_available_devices()
        if len(local) == 0:
            skip("need at least one local device")

    def instanciate_new_shell(self, *args, **kwargs):
        device = environ.get("TEST_ADB_DEVICE")
        return AdbShell(device=device, root=True, *args, **kwargs)
