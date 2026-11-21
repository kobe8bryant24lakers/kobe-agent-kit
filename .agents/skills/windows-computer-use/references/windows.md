# 在 Windows 上使用

以下命令用于已登录并解锁的 Windows 10（1703 或更新版本）或 Windows 11 桌面。需要 Windows 原生 Python 3.10+。在仓库根目录打开 PowerShell，首次运行：

```powershell
.\.agents\skills\windows-computer-use\setup.cmd
```

安装程序在当前用户目录创建虚拟环境，并以 `doctor` 检查依赖和桌面会话。运行后，PowerShell 中可用以下两个变量调用助手。如果技能装在别处，将 `$desktop` 指向该技能的 `scripts\desktop.py`。

```powershell
$python = Join-Path $env:LOCALAPPDATA 'kobe-agent-kit\windows-computer-use\venv\Scripts\python.exe'
$desktop = (Resolve-Path '.agents/skills/windows-computer-use/scripts/desktop.py').Path
& $python $desktop doctor
```

命令成功时标准输出为 JSON，运行错误写入标准错误并返回非零退出码。PowerShell 5.1 和 7 均可用 `ConvertFrom-Json` 处理结果。

## 从窗口到控件

例如，用户要在“另存为”窗口填写文件名。先列窗口，从结果中选中正确的对话框。若需启动应用，可使用已确认的应用名，例如 `Start-Process notepad.exe`，再观察新窗口。

```powershell
(& $python $desktop windows | ConvertFrom-Json).windows | Format-Table
# 将数字替换为刚观察到的对话框 HWND 和 PID
$target = @('--hwnd', '123456', '--pid', '7890')
& $python $desktop focus @target
$view = & $python $desktop inspect @target | ConvertFrom-Json
$view.controls | Format-List id, type, name, automation_id, enabled, visible, focused, depth
```

从输出中识别文件名编辑框，把该行的 `id` 放入 `$field`。不同系统语言、应用、甚至两次打开同一对话框时的值都可能不同。若 `truncated` 为真，可以调高 `--limit`（最多 2000）。没有可用 ID、控件重建或操作模式不受支持时，重新观察，必要时转用截图。

```powershell
$field = '<刚观察到的编辑框 id>'
& $python $desktop set-text @target --control $field --text '项目纪要.txt'
& $python $desktop read-text @target --control $field
```

核对回读值是否完全等于目标文件名。用户仅要求填写时，保留对话框打开。用户要求保存时，从最新观察中取得保存按钮 ID，执行 `invoke @target --control $button`，再检查覆盖确认框或目标文件。以下简写的命令前均需加上 `& $python $desktop`。

如果编辑框不支持直接设置值，用 `focus @target --control $field` 把键盘焦点移入已识别的字段。自绘界面可点击编辑区，再确认光标。**替换**预填文件名时，在确认该字段获焦后执行 `press @target --keys 'Ctrl+A'`，接着执行 `type-text @target --text '项目纪要.txt'`，最后回读或截图核对完整字段。**追加**时则先确认插入位置，直接使用 `type-text`。该命令输入单行字面文本，支持中文；需要换行的多行编辑区可用 `press @target --keys Enter`。

## 在截图中定位

```powershell
$png = Join-Path $env:TEMP ("window-{0}.png" -f [guid]::NewGuid())
$shot = & $python $desktop screenshot @target --out $png | ConvertFrom-Json
$shot | Format-List path, width, height, frame
```

用图像查看工具打开返回的 `path`。如果预览缩小了，按 `width` 和 `height` 把选中位置换算为原图像素。将实际读图得到的数值放入 `$x` 和 `$y`，执行以下**一项**操作后重新观察。

```powershell
& $python $desktop click @target --frame $shot.frame --x $x --y $y
# 或向下滚动三格
& $python $desktop scroll @target --frame $shot.frame --x $x --y $y --steps -3
```

`click` 可用 `--button right` 打开上下文菜单。保留负的多屏幕桌面坐标给工具处理，传给 `click` 和 `scroll` 的 x/y 始终是窗口图像内的坐标。若有其他窗口遮挡，先移开遮挡或选择对应弹窗。截图会留在指定路径，用完可删除本次创建的临时 PNG。
