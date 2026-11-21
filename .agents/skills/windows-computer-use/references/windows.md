# Using the Skill on Windows

These commands target a signed-in, unlocked Windows 10 (version 1703 or later) or Windows 11 desktop. A native Windows installation of Python 3.10+ is required. Open PowerShell at the repository root and run this command for first-time setup:

```powershell
.\.agents\skills\windows-computer-use\setup.cmd
```

The setup script creates a virtual environment under the current user's directory and runs `doctor` to check dependencies and the desktop session. After setup, use these two PowerShell variables to invoke the helper. If the skill is installed elsewhere, point `$desktop` to that skill's `scripts\desktop.py`.

```powershell
$python = Join-Path $env:LOCALAPPDATA 'kobe-agent-kit\windows-computer-use\venv\Scripts\python.exe'
$desktop = (Resolve-Path '.agents/skills/windows-computer-use/scripts/desktop.py').Path
& $python $desktop doctor
```

Successful commands write JSON to standard output. Runtime errors go to standard error and return a nonzero exit code. Both PowerShell 5.1 and 7 can process the results with `ConvertFrom-Json`.

## From Windows to Controls

For example, the user wants to fill in a filename in a Save As dialog. List the windows first and select the correct dialog from the results. If the application needs to be started, use its confirmed name, such as `Start-Process notepad.exe`, then observe the new window.

```powershell
(& $python $desktop windows | ConvertFrom-Json).windows | Format-Table
# Replace these numbers with the dialog HWND and PID just observed.
$target = @('--hwnd', '123456', '--pid', '7890')
& $python $desktop focus @target
$view = & $python $desktop inspect @target | ConvertFrom-Json
$view.controls | Format-List id, type, name, automation_id, enabled, visible, focused, depth
```

Identify the filename edit control in the output and assign its `id` to `$field`. Values may differ across system languages, applications, and even consecutive openings of the same dialog. If `truncated` is true, increase `--limit` up to 2000. If no usable ID is available, a control has been recreated, or an automation pattern is unsupported, observe again and switch to screenshots if needed.

```powershell
$field = '<edit control id just observed>'
& $python $desktop set-text @target --control $field --text 'project-notes.txt'
& $python $desktop read-text @target --control $field
```

Verify that the value read back exactly matches the intended filename. Leave the dialog open if the user only asked to fill it in. If the user asked to save, get the Save button's ID from the latest observation, run `invoke @target --control $button`, then check for an overwrite confirmation or the target file. Prefix each abbreviated command below with `& $python $desktop`.

If the edit control does not support setting its value directly, use `focus @target --control $field` to move keyboard focus to the identified field. In a custom-drawn interface, click the editing area and confirm the cursor position. To **replace** a prefilled filename, confirm the field has focus, run `press @target --keys 'Ctrl+A'`, then `type-text @target --text 'project-notes.txt'`, and finally read back or capture the complete field to verify it. To **append**, first confirm the insertion point, then use `type-text` directly. This command enters a single line of literal text and supports Chinese input; use `press @target --keys Enter` for line breaks in multiline editors.

## Locating Targets in Screenshots

```powershell
$png = Join-Path $env:TEMP ("window-{0}.png" -f [guid]::NewGuid())
$shot = & $python $desktop screenshot @target --out $png | ConvertFrom-Json
$shot | Format-List path, width, height, frame
```

Open the returned `path` with an image viewer. If the preview is scaled down, use `width` and `height` to convert the selected position to pixels in the original image. Assign the coordinates actually observed in the image to `$x` and `$y`, perform **one** of the following actions, then observe again.

```powershell
& $python $desktop click @target --frame $shot.frame --x $x --y $y
# Or scroll down three notches.
& $python $desktop scroll @target --frame $shot.frame --x $x --y $y --steps -3
```

Use `click` with `--button right` to open a context menu. Let the tool handle negative desktop coordinates across multiple monitors; the x/y values passed to `click` and `scroll` are always coordinates within the window image. If another window obscures the target, move the obstruction or select the relevant dialog first. Screenshots remain at the specified paths; temporary PNGs created during this task may be deleted after use.
