# kobe-agent-kit
A personal toolkit of reusable agent skills, MCP servers, and plugins.

## Windows 桌面操作

在 Windows 的 Codex 中打开这个仓库，即可使用随项目提供的 `$windows-computer-use`。例如：“用 $windows-computer-use 在当前记事本末尾另起一行，输入‘今天的会议纪要’，保留文档未保存状态。”

首次使用内置脚本时，在已安装 Python 3.10+ 的 Windows 电脑上，从仓库根目录运行 `.\.agents\skills\windows-computer-use\setup.cmd`。安装程序会创建独立环境并检查桌面连接。配置完成后，可用 `& $python tests/windows_smoke.py` 打开临时窗口验证中文输入、按钮和截图点击。[Windows 配置和示例](.agents/skills/windows-computer-use/references/windows.md) · [技能说明](.agents/skills/windows-computer-use/SKILL.md)
