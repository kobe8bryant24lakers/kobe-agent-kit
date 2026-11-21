# kobe-agent-kit

English | [简体中文](README.zh-CN.md)

A personal toolkit of reusable agent skills, MCP servers, and plugins.

Instructions, default prompts, and supporting templates for skills, plugins, and MCP servers are written in English. Responses and generated content follow the user's requested language, or the language of their request or conversation when none is specified. Literal text, code identifiers, and required template headings are preserved. See [project conventions](AGENTS.md) when creating or updating components.

## Software design documents

[`software-design`](.agents/skills/software-design/SKILL.md) creates or updates design documents for review based on business requirements, existing project designs, and code. It follows a specified template or the project's template, falling back to the [built-in concise template](.agents/skills/software-design/assets/design-template.md) when neither is available. It distinguishes the current state, proposed design, and open questions, adding [diagrams](.agents/skills/software-design/references/views.md) such as use case, class, sequence, flow, and state diagrams as needed while keeping text and visuals focused.

Copy the complete skill directory into your project to use it, with no additional runtime dependencies:

| Tool | Installation path within the project | Explicit invocation |
| --- | --- | --- |
| Codex | `.agents/skills/software-design/` (included in this repository) | `$software-design` |
| Claude Code | `.claude/skills/software-design/` | `/software-design` |

Include `SKILL.md`, `assets/`, `references/`, and `agents/` when copying, and sync the entire directory for subsequent updates. See the official [Codex documentation](https://developers.openai.com/codex/skills/) and [Claude Code documentation](https://code.claude.com/docs/en/skills) for directory and invocation conventions. Diagram previews require an editor or rendering tool that supports the chosen diagram source format.

Example (replace the skill name with `/software-design` in Claude Code):

```text
Use $software-design to write a design document for releasing inventory after an order is canceled.
Follow docs/templates/design-template.md, using the existing designs in docs/design/ and the order
and inventory code. Save it to docs/design/order-cancellation.md. Keep the text concise, add diagrams
where needed, and identify compatibility impacts and open questions.
```

## Windows desktop automation

Open this repository in Codex on Windows to use the included `$windows-computer-use` skill. For example: "Use $windows-computer-use to add a new line at the end of the current Notepad document, type 'Today's meeting notes', and leave the document unsaved."

Before using the bundled scripts for the first time, run `.\.agents\skills\windows-computer-use\setup.cmd` from the repository root on a Windows computer with Python 3.10+ installed. The setup script creates an isolated environment and checks the desktop connection. After setup, run `& $python tests/windows_smoke.py` to open a temporary window and verify Chinese text input, buttons, and screenshot-based clicks. [Windows setup and examples](.agents/skills/windows-computer-use/references/windows.md) · [Skill instructions](.agents/skills/windows-computer-use/SKILL.md)
