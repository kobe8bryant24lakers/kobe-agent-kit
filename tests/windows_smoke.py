"""Run on an unlocked Windows desktop with the skill's Python environment.

    python tests/windows_smoke.py
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid


CLI = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/windows-computer-use/scripts/desktop.py"
)
FIXTURE = r"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$form = New-Object System.Windows.Forms.Form
$form.Text = $env:COMPUTER_USE_TEST_TITLE
$form.StartPosition = 'CenterScreen'
$pad = New-Object System.Windows.Forms.Panel
$pad.Dock = 'Fill'
$pad.BackColor = [System.Drawing.Color]::FromArgb(35, 193, 71)
$pad.Add_Click({ $form.Text = $env:COMPUTER_USE_TEST_TITLE + ' | pixel clicked' })
$inputBox = New-Object System.Windows.Forms.TextBox
$inputBox.AccessibleName = 'Smoke input'
$inputBox.Dock = 'Top'
$apply = New-Object System.Windows.Forms.Button
$apply.Text = 'Apply'
$apply.AccessibleName = 'Smoke apply'
$apply.Dock = 'Bottom'
$apply.Add_Click({ $form.Text = $env:COMPUTER_USE_TEST_TITLE + ' | ' + $inputBox.Text })
$form.Controls.Add($pad)
$form.Controls.Add($inputBox)
$form.Controls.Add($apply)
$form.Add_Shown({ $form.Activate() })
[System.Windows.Forms.Application]::Run($form)
"""


def cli(*args, success=True):
    result = subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", timeout=25,
        creationflags=subprocess.CREATE_NO_WINDOW,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"),
    )
    if not success:
        if result.returncode == 0:
            raise AssertionError("The CLI accepted a stale target")
        return
    if result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def wait_for_window(process, title):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f"Fixture exited early with status {process.returncode}")
        windows = cli("windows")["windows"]
        for window in windows:
            if window["pid"] == process.pid and window["title"] == title:
                return window
        time.sleep(0.25)
    raise AssertionError(f"Fixture window did not reach the expected title: {title!r}")


@unittest.skipUnless(sys.platform == "win32", "requires an interactive Windows desktop")
class WindowsSmokeTest(unittest.TestCase):
    def test_edit_invoke_click_and_stale_window(self):
        from PIL import Image

        title = f"Windows Computer Use test {uuid.uuid4().hex}"
        shell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        process = subprocess.Popen(
            [str(shell), "-NoLogo", "-NoProfile", "-NonInteractive", "-Sta", "-Command", FIXTURE],
            env=dict(os.environ, COMPUTER_USE_TEST_TITLE=title),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            window = wait_for_window(process, title)
            target = ["--hwnd", window["hwnd"], "--pid", window["pid"]]
            cli("focus", *target)
            controls = cli("inspect", *target)["controls"]
            ids = {item["name"]: item["id"] for item in controls}
            sample = "中文 café {Tab} + 123"
            cli("set-text", *target, "--control", ids["Smoke input"], "--text", sample)
            value = cli("read-text", *target, "--control", ids["Smoke input"])
            self.assertEqual(value["text"], sample)
            self.assertFalse(value["truncated"])
            cli("focus", *target, "--control", ids["Smoke input"])
            cli("press", *target, "--keys", "End")
            cli("type-text", *target, "--text", "追加字")
            sample += "追加字"
            cli("invoke", *target, "--control", ids["Smoke apply"])
            wait_for_window(process, f"{title} | {sample}")
            with tempfile.TemporaryDirectory() as directory:
                png = Path(directory) / "window.png"
                capture = cli("screenshot", *target, "--out", png)
                with Image.open(png) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertEqual(image.size, (capture["width"], capture["height"]))
                    # The colored pad occupies the middle of this fixture at every DPI.
                    x, y = image.width // 2, image.height // 2
                    self.assertEqual(image.convert("RGB").getpixel((x, y)), (35, 193, 71))
                cli("click", *target, "--frame", capture["frame"], "--x", x, "--y", y)
                wait_for_window(process, f"{title} | pixel clicked")
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
        cli("inspect", *target, success=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
