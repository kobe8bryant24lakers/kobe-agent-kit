# Project Conventions

## Language

Apply this convention when creating or updating skills, plugins, and MCP servers in this repository:

- Write operational instructions in English, including skill instructions, prompts, agent-facing tool and configuration descriptions, reference guidance, and reusable template sources. This also applies when the request to create them is in another language.
- Use the user's explicitly requested language for responses and generated natural-language content; otherwise, follow the language of their request or established conversation. English instructions, default prompts, and examples do not determine the output language.
- Apply the output language to prose, generated headings, table labels, and diagram labels. Preserve literal text supplied for exact use, observed UI labels, code identifiers, commands, paths, protocol fields, and template headings required to remain unchanged.
- Keep localized reader documentation, such as `README.zh-CN.md`, in its intended language. Multilingual examples and test fixtures may retain the text needed to demonstrate or verify language support.
- Include the output-language rule in each component's relevant instruction or prompt entry point so it remains effective when the component is copied or installed outside this repository.
