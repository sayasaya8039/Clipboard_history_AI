"""Windows 自動起動設定。"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Sequence


RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "Coppy"
STARTUP_FLAG = "--startup"
APP_ROOT = Path(__file__).resolve().parent
MAIN_SCRIPT = APP_ROOT / "main.py"


class StartupRegistrationError(OSError):
    """自動起動設定の反映に失敗した。"""


def is_startup_launch(args: Optional[Sequence[str]] = None) -> bool:
    """自動起動経由の起動かどうか。"""
    return STARTUP_FLAG in list(args or ())


def build_launch_at_startup_command(
    *,
    executable: Optional[str] = None,
    frozen: Optional[bool] = None,
    main_script: Optional[Path] = None,
    pythonw_executable: Optional[str] = None,
) -> str:
    """Windows の Run キーへ保存するコマンドを組み立てる。"""
    executable_path = Path(executable or sys.executable)
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen

    if is_frozen:
        return f'{_quote_windows_path(executable_path)} {STARTUP_FLAG}'

    launcher = Path(pythonw_executable) if pythonw_executable else executable_path.with_name("pythonw.exe")
    if not pythonw_executable and not launcher.exists():
        launcher = executable_path

    script_path = Path(main_script or MAIN_SCRIPT)
    return f'{_quote_windows_path(launcher)} {_quote_windows_path(script_path)} {STARTUP_FLAG}'


def is_launch_at_startup_enabled(
    *,
    command: Optional[str] = None,
    winreg_module=None,
) -> bool:
    """現在のコマンドで自動起動が有効かを返す。"""
    reg = _resolve_winreg(winreg_module)
    if reg is None:
        return False

    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, reg.KEY_READ) as key:
            current_value, _ = reg.QueryValueEx(key, RUN_VALUE_NAME)
    except FileNotFoundError:
        return False
    except OSError:
        return False

    return current_value == (command or build_launch_at_startup_command())


def set_launch_at_startup_enabled(
    enabled: bool,
    *,
    command: Optional[str] = None,
    winreg_module=None,
) -> None:
    """自動起動を有効または無効にする。"""
    reg = _resolve_winreg(winreg_module)
    if reg is None:
        return

    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, reg.KEY_SET_VALUE) as key:
            if enabled:
                reg.SetValueEx(key, RUN_VALUE_NAME, 0, reg.REG_SZ, command or build_launch_at_startup_command())
            else:
                try:
                    reg.DeleteValue(key, RUN_VALUE_NAME)
                except FileNotFoundError:
                    pass
    except OSError as exc:
        raise StartupRegistrationError(f"自動起動の設定に失敗しました: {exc}") from exc


def _resolve_winreg(winreg_module):
    if winreg_module is not None:
        return winreg_module
    if sys.platform != "win32":
        return None

    import winreg

    return winreg


def _quote_windows_path(path: Path) -> str:
    return f'"{path}"'
