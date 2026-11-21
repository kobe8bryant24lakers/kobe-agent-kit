# kobe-agent-kit
A personal toolkit of reusable agent skills, MCP servers, and plugins.

## 软件设计文档

[`software-design`](.agents/skills/software-design/SKILL.md) 根据业务诉求、项目中的存量设计和代码编写或更新可评审的设计文档。优先遵循指定或项目模板，没有模板时采用[内置精简模板](.agents/skills/software-design/assets/design-template.md)。区分现状、拟议设计和待确认项，按需添加用例图、类图、时序图、流程图、状态图等[视图](.agents/skills/software-design/references/views.md)，避免堆砌文字和图表。

完整技能目录可复制到业务项目中使用，无额外运行依赖：

| 工具 | 项目内安装位置 | 显式调用 |
| --- | --- | --- |
| Codex | `.agents/skills/software-design/`（本仓库已放置） | `$software-design` |
| Claude Code | `.claude/skills/software-design/` | `/software-design` |

复制时包含 `SKILL.md`、`assets/`、`references/` 和 `agents/`，后续更新同步整个目录。目录和调用约定见 [Codex 官方文档](https://developers.openai.com/codex/skills/)与 [Claude Code 官方文档](https://code.claude.com/docs/en/skills)。图形预览需要项目编辑器或渲染工具支持所选图源格式。

示例（在 Claude Code 中将技能名改为 `/software-design`）：

```text
用 $software-design 为“订单取消后释放库存”编写设计文档。
按 docs/templates/设计模板.md，结合 docs/design/ 中的存量设计和订单、库存相关代码，
输出到 docs/design/订单取消.md。文字简洁，按需要配图，明确兼容影响和待确认问题。
```

## Windows 桌面操作

在 Windows 的 Codex 中打开这个仓库，即可使用随项目提供的 `$windows-computer-use`。例如：“用 $windows-computer-use 在当前记事本末尾另起一行，输入‘今天的会议纪要’，保留文档未保存状态。”

首次使用内置脚本时，在已安装 Python 3.10+ 的 Windows 电脑上，从仓库根目录运行 `.\.agents\skills\windows-computer-use\setup.cmd`。安装程序会创建独立环境并检查桌面连接。配置完成后，可用 `& $python tests/windows_smoke.py` 打开临时窗口验证中文输入、按钮和截图点击。[Windows 配置和示例](.agents/skills/windows-computer-use/references/windows.md) · [技能说明](.agents/skills/windows-computer-use/SKILL.md)
