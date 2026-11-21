"""Windows UIA observations. The caller must first enable per-monitor DPI awareness."""

import ctypes
from ctypes import wintypes
from itertools import islice
from pathlib import Path

import pywintypes
import win32gui
import win32process
from comtypes import COMError
from PIL import ImageGrab
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_defines import IUIA, NoPatternInterfaceError
from pywinauto.uia_element_info import UIAElementInfo


MAX_CONTROLS = 2000
_DWM_CLOAKED = 14
_DWM_EXTENDED_FRAME_BOUNDS = 9
_dwm_attribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
_dwm_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
_dwm_attribute.restype = ctypes.c_long


def _attribute(hwnd, attribute, value):
    return _dwm_attribute(hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)) == 0


def _cloaked(hwnd):
    value = wintypes.DWORD()
    return bool(_attribute(hwnd, _DWM_CLOAKED, value) and value.value)


def windows():
    foreground = win32gui.GetForegroundWindow()
    items = []

    def collect(hwnd, unused):
        try:
            if win32gui.IsWindowVisible(hwnd) and not _cloaked(hwnd):
                items.append({
                    "hwnd": hwnd, "pid": win32process.GetWindowThreadProcessId(hwnd)[1],
                    "title": win32gui.GetWindowText(hwnd), "foreground": hwnd == foreground,
                    "minimized": bool(win32gui.IsIconic(hwnd)),
                })
        except pywintypes.error:
            if win32gui.IsWindow(hwnd):
                raise
        return True

    win32gui.EnumWindows(collect, None)
    return {"windows": items}


def _check_identity(hwnd, pid):
    if not win32gui.IsWindow(hwnd) or win32gui.GetAncestor(hwnd, 2) != hwnd:  # GA_ROOT
        raise ValueError("Target is no longer a top-level window. Run windows again.")
    if win32process.GetWindowThreadProcessId(hwnd)[1] != pid:
        raise ValueError("Window process changed. Run windows again.")
    if not win32gui.IsWindowVisible(hwnd) or _cloaked(hwnd):
        raise ValueError("Target is hidden or on another desktop. Run windows again.")


def resolve_window(hwnd, pid):
    _check_identity(hwnd, pid)
    info = UIAElementInfo(hwnd)
    if info.handle != hwnd or info.process_id != pid:
        raise ValueError("UI Automation returned a different window identity.")
    return UIAWrapper(info)


def _siblings(walker, parent):
    element = walker.GetFirstChildElement(parent)
    while element:
        yield element
        element = walker.GetNextSiblingElement(element)


def _walk(win):
    """Stream the control view, bounding work by nodes consumed, even for wide lists."""
    walker = IUIA().iuia.ControlViewWalker
    stack = [iter((win.element_info.element,))]
    while stack:
        try:
            element = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        try:
            password = bool(element.CurrentIsPassword)
        except COMError:
            password = True  # Suppress names and descendants if sensitivity is unknown.
        yield UIAElementInfo(element), len(stack) - 1, password
        if not password:
            stack.append(_siblings(walker, element))


def _runtime_id(info):
    parts = info.runtime_id
    if not parts:
        return None
    return ".".join(str(part) for part in parts)


def inspect_window(win, limit):
    if not 1 <= limit <= MAX_CONTROLS:
        raise ValueError(f"limit must be between 1 and {MAX_CONTROLS}")
    controls = []
    seen = {}
    truncated = False
    for info, depth, password in islice(_walk(win), limit + 1):
        if len(controls) == limit:
            truncated = True
            break
        key = _runtime_id(info)
        row = {
            "id": key, "depth": depth, "type": info.control_type,
            "name": "" if password else (info.name or "")[:300],
            "automation_id": (info.automation_id or "")[:300] if not password else "",
            "enabled": info.enabled, "visible": info.visible, "password": password,
            "focused": bool(info.element.CurrentHasKeyboardFocus),
        }
        if key and key in seen:
            seen[key]["id"] = row["id"] = None
        elif key:
            seen[key] = row
        controls.append(row)
    return {"hwnd": win.handle, "pid": win.element_info.process_id,
            "controls": controls, "truncated": truncated}


def find_control(win, control_id):
    if not control_id:
        raise ValueError("Choose a control with an id from the current inspection.")
    match = None
    for count, (info, _, _) in enumerate(islice(_walk(win), MAX_CONTROLS + 1)):
        if count == MAX_CONTROLS:
            raise ValueError("Control tree is too large to validate a unique id. Use a screenshot.")
        if _runtime_id(info) == control_id:
            if match is not None:
                raise ValueError("Ambiguous control id. Inspect again or use a screenshot.")
            match = info
    if match is None:
        raise ValueError("Control no longer exists. Inspect the target window again.")
    return UIAWrapper(match)


def read_text(win, control_id, limit):
    if not 1 <= limit <= 16000:
        raise ValueError("limit must be between 1 and 16000 characters")
    control = find_control(win, control_id)
    if control.element_info.element.CurrentIsPassword:
        raise ValueError("Cannot read a password control.")
    try:
        # UIA providers may count UTF-16 units; a Python character takes up to two.
        value = control.iface_text.DocumentRange.GetText(2 * (limit + 1))
    except NoPatternInterfaceError:
        try:
            value = control.iface_value.CurrentValue
        except NoPatternInterfaceError as error:
            raise ValueError("This control exposes neither TextPattern nor ValuePattern.") from error
    value = value or ""
    return {"text": value[:limit], "truncated": len(value) > limit}


def _frame_bounds(hwnd):
    rect = wintypes.RECT()
    if _attribute(hwnd, _DWM_EXTENDED_FRAME_BOUNDS, rect):
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)


def _overlaps(first, second):
    l1, t1, r1, b1 = first
    l2, t2, r2, b2 = second
    return max(l1, l2) < min(r1, r2) and max(t1, t2) < min(b1, b2)


def _capture_bounds(hwnd, pid):
    _check_identity(hwnd, pid)
    if win32gui.IsIconic(hwnd) or win32gui.GetForegroundWindow() != hwnd:
        raise ValueError("Bring the target window to the foreground before capturing it.")
    bounds = win32gui.GetWindowRect(hwnd)
    if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        raise ValueError("Target window has empty bounds.")
    # Use visible (DWM) bounds for occlusion, but keep GetWindowRect as the common
    # screenshot/click origin; maximized windows have invisible resize borders.
    frame = _frame_bounds(hwnd)
    above = hwnd
    visited = {hwnd}
    while True:
        above = win32gui.GetWindow(above, 3)  # GW_HWNDPREV: next higher in Z order
        if not above:
            return bounds
        if above in visited or len(visited) > 2048:
            raise ValueError("Window order changed during capture. Take a fresh screenshot.")
        visited.add(above)
        if (win32gui.IsWindowVisible(above) and not win32gui.IsIconic(above)
                and not _cloaked(above) and _overlaps(frame, _frame_bounds(above))):
            raise ValueError("Another window overlaps the target. Dismiss the overlay or select its window.")


def screenshot(win, path):
    hwnd, pid = win.handle, win.element_info.process_id
    bounds = _capture_bounds(hwnd, pid)
    with ImageGrab.grab(bbox=bounds, all_screens=True, include_layered_windows=True) as image:
        if tuple(_capture_bounds(hwnd, pid)) != tuple(bounds):
            raise ValueError("Window moved during capture. Take a fresh screenshot.")
        destination = Path(path).resolve()
        image.save(destination, format="PNG")
        width, height = image.size
    return {"hwnd": hwnd, "pid": pid, "bounds": list(bounds), "width": width,
            "height": height, "path": str(destination)}
