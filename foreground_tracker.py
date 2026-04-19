"""前面ウィンドウ追跡モジュール (Windows).

SetWinEventHook で EVENT_SYSTEM_FOREGROUND を購読し、
自プロセス以外で最後に前面化されていたウィンドウ HWND を保持する。
貼り付け時にこの HWND へフォーカスを戻してから Ctrl+V を送る。

重要: editor → Coppy の遷移ではイベントの引数が Coppy(self) のため、
      「遷移直前まで前面だった他プロセス窓」を覚えておく必要がある。
      そのため内部で _current_fg を保持し、遷移時に旧値を last_other_hwnd に退避する。
"""
from __future__ import annotations

import ctypes
import os
import sys
from ctypes import wintypes


EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000

_WIN_EVENT_PROC = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD,
)


class ForegroundTracker:
    """自プロセス以外の最新前面 HWND を保持する。"""

    def __init__(self) -> None:
        self.last_other_hwnd: int = 0
        self._current_fg: int = 0
        self._hook = 0
        self._own_pid = os.getpid()
        self._user32 = None

        if sys.platform != "win32":
            return

        self._user32 = ctypes.windll.user32
        self._proc = _WIN_EVENT_PROC(self._on_event)
        self._hook = self._user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            self._proc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT,
        )
        # 初期値として現在の前面ウィンドウを記録
        current = int(self._user32.GetForegroundWindow() or 0)
        self._current_fg = current
        if current and self._pid_of(current) != self._own_pid:
            self.last_other_hwnd = current

    def _on_event(self, hook, event, hwnd, id_object, id_child, thread, time_ms) -> None:  # noqa: N803
        try:
            new_hwnd = int(hwnd) if hwnd else 0
            if new_hwnd == 0:
                return

            # 遷移直前まで前面だったウィンドウ（他プロセス）を退避
            prev = self._current_fg
            if prev and prev != new_hwnd:
                try:
                    if self._pid_of(prev) != self._own_pid:
                        self.last_other_hwnd = prev
                except Exception:
                    pass

            # 新しい前面が他プロセスなら、それも記録しておく（最新化）
            try:
                if self._pid_of(new_hwnd) != self._own_pid:
                    self.last_other_hwnd = new_hwnd
            except Exception:
                pass

            self._current_fg = new_hwnd
        except Exception:
            pass

    def _pid_of(self, hwnd: int) -> int:
        pid = wintypes.DWORD()
        self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(pid.value)

    def stop(self) -> None:
        if self._user32 and self._hook:
            try:
                self._user32.UnhookWinEvent(self._hook)
            except Exception:
                pass
            self._hook = 0


def activate_window(hwnd: int) -> bool:
    """AttachThreadInput + Alt-key unlock で対象ウィンドウを確実に前面化する。"""
    if sys.platform != "win32" or not hwnd:
        return False
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        if not user32.IsWindow(hwnd):
            return False

        # 最小化されている場合は復元
        if user32.IsIconic(hwnd):
            SW_RESTORE = 9
            user32.ShowWindow(hwnd, SW_RESTORE)

        # Foreground lock を解除するため Alt を一瞬叩く
        VK_MENU = 0x12
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

        fg_hwnd = user32.GetForegroundWindow()
        fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
        tgt_thread = user32.GetWindowThreadProcessId(hwnd, None)
        cur_thread = kernel32.GetCurrentThreadId()

        attached_fg = False
        attached_tgt = False
        try:
            if fg_thread and fg_thread != cur_thread:
                attached_fg = bool(user32.AttachThreadInput(cur_thread, fg_thread, True))
            if tgt_thread and tgt_thread != cur_thread:
                attached_tgt = bool(user32.AttachThreadInput(cur_thread, tgt_thread, True))

            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SetFocus(hwnd)
            user32.SetActiveWindow(hwnd)
        finally:
            if attached_fg:
                user32.AttachThreadInput(cur_thread, fg_thread, False)
            if attached_tgt:
                user32.AttachThreadInput(cur_thread, tgt_thread, False)

        return int(user32.GetForegroundWindow()) == int(hwnd)
    except Exception as exc:
        print(f"activate_window 失敗: {exc}")
        return False


def window_title(hwnd: int) -> str:
    """ウィンドウタイトルを取得（ログ用）。"""
    if sys.platform != "win32" or not hwnd:
        return ""
    try:
        user32 = ctypes.windll.user32
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""
