"""Target-scoped desktop actions. DPI awareness must be set by the entry point."""

import ctypes
import unicodedata

import win32api
import win32con as vk
import win32gui
from pywinauto.uia_defines import IUIA, NoPatternInterfaceError
from pywinauto.win32structures import INPUT

from win_observe import find_control


def _require_active(win):
    hwnd = win.handle
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowEnabled(hwnd):
        raise ValueError("Window closed or disabled by a dialog. List windows again.")
    if (not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd)
            or win32gui.GetForegroundWindow() != hwnd):
        raise ValueError("Target window is not active. Focus it and observe again.")


def focus(win, control_id=None):
    hwnd = win.handle
    if not win32gui.IsWindowEnabled(hwnd):
        raise ValueError("Window is disabled. Select its active dialog instead.")
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, vk.SW_RESTORE)
    if win32gui.GetForegroundWindow() != hwnd:
        try:
            win32gui.SetForegroundWindow(hwnd)
        except win32gui.error:
            # Windows can deny foreground activation from a background process.
            pass
    _require_active(win)
    if control_id is not None:
        control = _control(win, control_id)
        element = control.element_info.element
        _require_active(win)
        element.SetFocus()
        if not element.CurrentHasKeyboardFocus:
            raise ValueError("Focus did not land on the selected control. Inspect the window again.")
    return {"focused": True}


def _control(win, control_id):
    control = find_control(win, control_id)
    if not control.is_enabled() or not control.is_visible():
        raise ValueError("Control is disabled or offscreen. Inspect the window again.")
    return control


def invoke(win, control_id):
    control = _control(win, control_id)
    try:
        pattern = control.iface_invoke
    except NoPatternInterfaceError as exc:
        raise ValueError("This control has no Invoke pattern. Inspect before using a different action.") from exc
    _require_active(win)
    pattern.Invoke()
    return {"invoked": True}


def set_text(win, control_id, text):
    control = _control(win, control_id)
    if control.element_info.element.CurrentIsPassword:
        raise ValueError("Password entry requires user input.")
    try:
        pattern = control.iface_value
    except NoPatternInterfaceError as exc:
        raise ValueError("This control has no Value pattern. Focus an editor to use type-text.") from exc
    if pattern.CurrentIsReadOnly:
        raise ValueError("This control is read-only.")
    if "\0" in text:
        raise ValueError("NUL is not supported in UI text.")
    _require_active(win)
    pattern.SetValue(text)
    return {"set_text": True}


def _require_idle_input():
    # A held modifier would change the meaning of a click or shortcut.
    for key in (vk.VK_SHIFT, vk.VK_CONTROL, vk.VK_MENU, vk.VK_LWIN, vk.VK_RWIN,
                vk.VK_LBUTTON, vk.VK_MBUTTON, vk.VK_RBUTTON):
        if win32api.GetAsyncKeyState(key) & 0x8000:
            raise ValueError("Release held keys and mouse buttons before sending input.")


def _send(events):
    send = ctypes.windll.user32.SendInput
    send.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
    send.restype = ctypes.c_uint
    batch = (INPUT * len(events))(*events)
    sent = send(len(batch), batch, ctypes.sizeof(INPUT))
    if sent != len(batch):
        raise RuntimeError(f"Windows accepted {sent}/{len(batch)} input events. Inspect the result before retrying.")


def _key(code=0, *, scan=0, flags=0):
    event = INPUT(type=vk.INPUT_KEYBOARD)
    event.ki.wVk = code
    event.ki.wScan = scan
    event.ki.dwFlags = flags
    return event


def _mouse(flags, data=0):
    event = INPUT(type=vk.INPUT_MOUSE)
    event.mi.dwFlags = flags
    event.mi.mouseData = data & 0xffffffff
    return event


_MODIFIERS = {"ctrl": vk.VK_CONTROL, "alt": vk.VK_MENU, "shift": vk.VK_SHIFT}
_KEYS = {
    "enter": vk.VK_RETURN, "tab": vk.VK_TAB, "esc": vk.VK_ESCAPE,
    "escape": vk.VK_ESCAPE, "space": vk.VK_SPACE, "backspace": vk.VK_BACK,
    "delete": vk.VK_DELETE, "insert": vk.VK_INSERT, "home": vk.VK_HOME,
    "end": vk.VK_END, "pageup": vk.VK_PRIOR, "pagedown": vk.VK_NEXT,
    "up": vk.VK_UP, "down": vk.VK_DOWN, "left": vk.VK_LEFT, "right": vk.VK_RIGHT,
}
_EXTENDED = {vk.VK_DELETE, vk.VK_INSERT, vk.VK_HOME, vk.VK_END, vk.VK_PRIOR,
             vk.VK_NEXT, vk.VK_UP, vk.VK_DOWN, vk.VK_LEFT, vk.VK_RIGHT}
_KEYS.update({f"f{i}": vk.VK_F1 + i - 1 for i in range(1, 13)})
_KEYS.update({chr(i).lower(): i for i in range(ord("A"), ord("Z") + 1)})
_KEYS.update({str(i): ord(str(i)) for i in range(10)})


def press(win, keys):
    *mods, last = [part.strip().lower() for part in keys.split("+")]
    if last not in _KEYS or any(m not in _MODIFIERS for m in mods) or len(set(mods)) != len(mods):
        raise ValueError("Expected one shortcut, e.g. Ctrl+A, Shift+Tab, Enter or F2.")
    codes = [_MODIFIERS[m] for m in mods] + [_KEYS[last]]
    events = []
    for pressed, release in ((codes, 0), (reversed(codes), vk.KEYEVENTF_KEYUP)):
        for code in pressed:
            flags = vk.KEYEVENTF_EXTENDEDKEY if code in _EXTENDED else 0
            events.append(_key(code, flags=flags | release))
    _require_idle_input()
    _require_active(win)
    _send(events)
    return {"pressed": keys}


def _focused_editor(win):
    uia = IUIA().iuia
    element = uia.GetFocusedElement()
    if not element or element.CurrentIsPassword:
        raise ValueError("A focused non-password editor is required.")
    if element.CurrentControlType not in (IUIA().known_control_types["Edit"],
                                          IUIA().known_control_types["Document"]):
        raise ValueError("Focus an Edit or Document control before typing.")
    current = element
    walker = uia.RawViewWalker
    for _ in range(128):
        if not current:
            break
        if uia.CompareElements(current, win.element_info.element):
            return element
        current = walker.GetParentElement(current)
    raise ValueError("The focused editor does not belong to the selected window.")


def type_text(win, text):
    encoded = text.encode("utf-16-le")
    if not encoded or len(encoded) > 8192 or any(unicodedata.category(ch) == "Cc" for ch in text):
        raise ValueError("Send 1–4096 UTF-16 units of single-line text. Use press for Tab or Enter.")
    # KEYEVENTF_UNICODE sends literal UTF-16 units, including surrogate pairs.
    events = []
    for i in range(0, len(encoded), 2):
        unit = int.from_bytes(encoded[i:i + 2], "little")
        events.extend((_key(scan=unit, flags=0x0004),
                       _key(scan=unit, flags=0x0004 | vk.KEYEVENTF_KEYUP)))
    element = _focused_editor(win)
    if not element.CurrentHasKeyboardFocus:
        raise ValueError("Keyboard focus changed. Inspect the target again.")
    _require_idle_input()
    _require_active(win)
    _send(events)
    return {"typed": True}


def _position_pointer(win, x, y, bounds):
    expected = tuple(bounds)
    if len(expected) != 4 or not all(type(n) is int for n in (*expected, x, y)):
        raise ValueError("Expected integer screenshot coordinates and four integer bounds.")
    left, top, right, bottom = expected
    if not (0 <= x < right - left and 0 <= y < bottom - top):
        raise ValueError("Point is outside the screenshot.")
    point = (left + x, top + y)

    def check_target():
        _require_active(win)
        if win32gui.GetWindowRect(win.handle) != expected:
            raise ValueError("Window geometry changed. Take a new screenshot.")
        hit = win32gui.WindowFromPoint(point)
        if not hit or (hit != win.handle and not win32gui.IsChild(win.handle, hit)):
            raise ValueError("Another window covers this point. Take a new screenshot.")
        if not win32gui.IsWindowEnabled(hit):
            raise ValueError("The control at this point is disabled.")

    _require_idle_input()
    check_target()
    win32api.SetCursorPos(point)
    if win32api.GetCursorPos() != point:
        raise ValueError("Pointer did not reach the target.")
    check_target()


def click(win, x, y, bounds, button="left"):
    buttons = {"left": (vk.MOUSEEVENTF_LEFTDOWN, vk.MOUSEEVENTF_LEFTUP),
               "right": (vk.MOUSEEVENTF_RIGHTDOWN, vk.MOUSEEVENTF_RIGHTUP)}
    if button not in buttons:
        raise ValueError("Button must be left or right.")
    events = [_mouse(flag) for flag in buttons[button]]
    _position_pointer(win, x, y, bounds)
    _send(events)
    return {"clicked": button}


def scroll(win, x, y, steps, bounds):
    if type(steps) is not int or not 1 <= abs(steps) <= 12:
        raise ValueError("Use 1–12 wheel notches, positive up or negative down.")
    event = _mouse(vk.MOUSEEVENTF_WHEEL, 120 * steps)
    _position_pointer(win, x, y, bounds)
    _send([event])
    return {"scrolled": steps}
