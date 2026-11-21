"""Observe and operate one window on the local, interactive Windows desktop."""

import argparse
import ctypes
from ctypes import wintypes
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys
import threading


def integer(value):
    try:
        return int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a decimal or 0x-prefixed integer") from exc


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("doctor", help="check runtime, dependencies and desktop access")
    commands.add_parser("windows", help="list visible top-level windows")
    target = argparse.ArgumentParser(add_help=False)
    target.add_argument("--hwnd", required=True, type=integer, help="window handle from windows")
    target.add_argument("--pid", required=True, type=int, help="owning process ID from windows")

    def command(name, help_text):
        return commands.add_parser(name, parents=[target], help=help_text)

    command("focus", "activate the target window or focus a control").add_argument("--control")
    inspect = command("inspect", "list controls exposed by UI Automation")
    inspect.add_argument("--limit", type=int, default=150)
    read = command("read-text", "read text from one non-password control")
    read.add_argument("--control", required=True)
    read.add_argument("--limit", type=int, default=2000, help="maximum characters to return (1-16000)")
    snap = command("screenshot", "capture the foreground window and return its frame token")
    snap.add_argument("--out", type=Path, required=True, help="destination PNG")
    command("invoke", "invoke a UIA control").add_argument("--control", required=True)
    edit = command("set-text", "replace the value of an editable UIA control")
    edit.add_argument("--control", required=True)
    edit.add_argument("--text", required=True)
    command("type-text", "insert literal Unicode at the current caret").add_argument("--text", required=True)
    command("press", "send one chord, such as Ctrl+A or Shift+Tab").add_argument("--keys", required=True)
    for name, help_text in [("click", "click once within a captured window"),
                            ("scroll", "scroll at a point within a captured window")]:
        pointer = command(name, help_text)
        pointer.add_argument("--frame", required=True, help="frame token from screenshot")
        pointer.add_argument("--x", type=int, required=True, help="physical pixels from the PNG left")
        pointer.add_argument("--y", type=int, required=True, help="physical pixels from the PNG top")
        if name == "click":
            pointer.add_argument("--button", choices=["left", "right"], default="left")
        else:
            pointer.add_argument("--steps", type=int, required=True, help="wheel notches, positive is up")
    return parser.parse_args(argv)


def prepare_desktop():
    if sys.platform != "win32":
        raise RuntimeError("Run this helper in the target user's Windows desktop session.")
    if sys.version_info < (3, 10):
        raise RuntimeError("Use Python 3.10 or newer.")
    user = ctypes.WinDLL("user32", use_last_error=True)
    # UIA, GetWindowRect and Pillow must agree even across mixed-DPI displays.
    per_monitor_v2 = ctypes.c_void_p(-4)
    user.GetThreadDpiAwarenessContext.restype = ctypes.c_void_p
    user.AreDpiAwarenessContextsEqual.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    if not user.SetProcessDpiAwarenessContext(per_monitor_v2):
        if not user.AreDpiAwarenessContextsEqual(user.GetThreadDpiAwarenessContext(), per_monitor_v2):
            raise RuntimeError("Cannot enable per-monitor DPI awareness. Use a fresh Windows Python process.")

    user.OpenInputDesktop.restype = wintypes.HANDLE
    user.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    user.CloseDesktop.argtypes = [wintypes.HANDLE]
    user.GetThreadDesktop.restype = wintypes.HANDLE
    user.GetUserObjectInformationW.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)
    ]

    def desktop_name(handle):
        name = ctypes.create_unicode_buffer(256)
        size = wintypes.DWORD()
        if not user.GetUserObjectInformationW(handle, 2, name, ctypes.sizeof(name), ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        return name.value

    input_desktop = user.OpenInputDesktop(0, False, 0x0001)  # DESKTOP_READOBJECTS
    if not input_desktop:
        raise RuntimeError("Input desktop is inaccessible. Unlock Windows or reconnect the desktop session.")
    try:
        thread = ctypes.windll.kernel32.GetCurrentThreadId()
        current = desktop_name(input_desktop)
        if current.casefold() == "winlogon" or current != desktop_name(user.GetThreadDesktop(thread)):
            raise RuntimeError("Switch back to the target user's interactive desktop.")
    finally:
        user.CloseDesktop(input_desktop)


def frame_bounds(args):
    try:
        hwnd, pid, left, top, right, bottom = map(int, args.frame.split(":"))
    except ValueError as exc:
        raise ValueError("Invalid frame. Capture the target window again.") from exc
    if (hwnd, pid) != (args.hwnd, args.pid):
        raise ValueError("Frame belongs to a different window. Capture the target again.")
    return [left, top, right, bottom]


def dispatch(args, observe, actions):
    if args.action == "windows":
        return observe.windows()
    if args.action == "doctor":
        return {"ready": True, "python": sys.version.split()[0],
                "pywinauto": version("pywinauto"), "pillow": version("Pillow"),
                "visible_windows": len(observe.windows()["windows"])}

    win = observe.resolve_window(args.hwnd, args.pid)
    if args.action == "inspect":
        return observe.inspect_window(win, args.limit)
    if args.action == "read-text":
        return observe.read_text(win, args.control, args.limit)
    if args.action == "screenshot":
        shot = observe.screenshot(win, args.out)
        shot["frame"] = ":".join(map(str, [args.hwnd, args.pid, *shot["bounds"]]))
        return shot
    if args.action == "focus":
        return actions.focus(win, args.control)
    if args.action == "invoke":
        return actions.invoke(win, args.control)
    if args.action == "set-text":
        return actions.set_text(win, args.control, args.text)
    if args.action == "type-text":
        return actions.type_text(win, args.text)
    if args.action == "press":
        return actions.press(win, args.keys)
    bounds = frame_bounds(args)
    if args.action == "click":
        return actions.click(win, args.x, args.y, bounds, button=args.button)
    if args.action == "scroll":
        return actions.scroll(win, args.x, args.y, args.steps, bounds)
    raise ValueError(f"Unknown operation: {args.action}")


def main():
    args = parse_args()
    # Some UIA providers block the calling thread until a modal dialog closes.
    # End this one-shot helper so the next observation can discover the dialog.
    def timed_out():
        error = {"action": args.action, "error": "Desktop operation timed out. Observe the window before retrying."}
        os.write(2, (json.dumps(error) + "\n").encode("ascii"))
        os._exit(124)

    watchdog = threading.Timer(30, timed_out)
    watchdog.daemon = True
    watchdog.start()
    try:
        prepare_desktop()
        try:
            import win_actions
            import win_observe
        except ImportError as exc:
            raise RuntimeError(f"Cannot load Windows dependencies ({exc}). Install this skill's requirements.txt.") from exc
        result = dispatch(args, win_observe, win_actions)
    except Exception as exc:
        print(json.dumps({"error": str(exc) or type(exc).__name__, "action": args.action}), file=sys.stderr)
        return 1
    finally:
        watchdog.cancel()
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
