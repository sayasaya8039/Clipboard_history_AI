import unittest
from pathlib import Path

from startup import (
    STARTUP_FLAG,
    build_launch_at_startup_command,
    is_startup_launch,
    is_launch_at_startup_enabled,
    set_launch_at_startup_enabled,
)


class _FakeRegistryKey:
    def __init__(self, owner):
        self._owner = owner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeWinReg:
    HKEY_CURRENT_USER = object()
    KEY_SET_VALUE = 1
    KEY_READ = 2
    REG_SZ = 1

    def __init__(self, delete_missing: bool = False, query_value: str | None = None):
        self.opened = []
        self.set_calls = []
        self.deleted = []
        self._delete_missing = delete_missing
        self._query_value = query_value

    def OpenKey(self, root, path, reserved, access):  # noqa: N802
        self.opened.append((root, path, reserved, access))
        return _FakeRegistryKey(self)

    def SetValueEx(self, key, name, reserved, reg_type, value):  # noqa: N802
        self.set_calls.append((name, reserved, reg_type, value))

    def DeleteValue(self, key, name):  # noqa: N802
        if self._delete_missing:
            raise FileNotFoundError(name)
        self.deleted.append(name)

    def QueryValueEx(self, key, name):  # noqa: N802
        if self._query_value is None:
            raise FileNotFoundError(name)
        return self._query_value, self.REG_SZ


class StartupManagerTests(unittest.TestCase):
    def test_build_launch_command_uses_pythonw_for_script_run(self) -> None:
        command = build_launch_at_startup_command(
            executable=r"C:\Python314\python.exe",
            frozen=False,
            main_script=Path(r"D:\NEXTCLOUD\Windows_app\Coppy\main.py"),
            pythonw_executable=r"C:\Python314\pythonw.exe",
        )

        self.assertIn('"C:\\Python314\\pythonw.exe"', command)
        self.assertIn('"D:\\NEXTCLOUD\\Windows_app\\Coppy\\main.py"', command)
        self.assertTrue(command.endswith(STARTUP_FLAG))

    def test_build_launch_command_uses_frozen_executable(self) -> None:
        command = build_launch_at_startup_command(
            executable=r"D:\NEXTCLOUD\Windows_app\Coppy\dist\coppy.exe",
            frozen=True,
        )

        self.assertEqual(
            command,
            '"D:\\NEXTCLOUD\\Windows_app\\Coppy\\dist\\coppy.exe" --startup',
        )

    def test_is_startup_launch_detects_flag(self) -> None:
        self.assertTrue(is_startup_launch(["--startup"]))
        self.assertFalse(is_startup_launch(["--debug"]))

    def test_set_launch_at_startup_writes_registry_value(self) -> None:
        fake_reg = _FakeWinReg()

        set_launch_at_startup_enabled(
            True,
            command='"D:\\NEXTCLOUD\\Windows_app\\Coppy\\dist\\coppy.exe" --startup',
            winreg_module=fake_reg,
        )

        self.assertEqual(len(fake_reg.opened), 1)
        self.assertEqual(len(fake_reg.set_calls), 1)
        self.assertEqual(
            fake_reg.set_calls[0][3],
            '"D:\\NEXTCLOUD\\Windows_app\\Coppy\\dist\\coppy.exe" --startup',
        )

    def test_set_launch_at_startup_ignores_missing_registry_value_on_delete(self) -> None:
        fake_reg = _FakeWinReg(delete_missing=True)

        set_launch_at_startup_enabled(False, winreg_module=fake_reg)

        self.assertEqual(len(fake_reg.opened), 1)
        self.assertEqual(fake_reg.deleted, [])

    def test_is_launch_at_startup_enabled_matches_registry_value(self) -> None:
        fake_reg = _FakeWinReg(
            query_value='"D:\\NEXTCLOUD\\Windows_app\\Coppy\\dist\\coppy.exe" --startup'
        )

        self.assertTrue(
            is_launch_at_startup_enabled(
                command='"D:\\NEXTCLOUD\\Windows_app\\Coppy\\dist\\coppy.exe" --startup',
                winreg_module=fake_reg,
            )
        )


if __name__ == "__main__":
    unittest.main()
