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
