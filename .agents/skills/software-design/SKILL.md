---
name: software-design
description: Create, complete, or update software design documents from business requirements, existing project designs, and code, following the applicable template. Use for high-level designs, detailed designs, technical proposals, and change designs that need concise writing, traceable evidence, and appropriate diagrams for review.
---

# Software Design Documents

Help reviewers quickly understand the problem, current state, proposed changes, rationale, and acceptance criteria. Ground the design in project facts and use only the text and diagrams needed to explain it. Writing a design does not authorize implementing the code.

Use the user's explicitly requested output language; otherwise, follow the language of their request or established conversation. English skill instructions and default prompts do not set the output language. Apply the chosen language to responses, document prose, and generated headings, table labels, and diagram labels. Preserve project terminology, code identifiers, paths, literal user-provided text, and headings that a specified template requires unchanged.

## 1. Establish scope and choose a template

- Extract business goals, user roles, key scenarios, constraints, and the scope of this task from the request.
- Read applicable repository conventions, such as `AGENTS.md` and `CLAUDE.md`, and relevant documentation directories first. Prefer the user's specified template, then an applicable project template or comparable design structure. If neither exists, use the [built-in concise template](assets/design-template.md). Do not append the built-in structure to an existing template.
- Follow the specified template's section order, numbering, required content, and diagram requirements. Explain in one sentence why a required section does not apply; remove optional empty sections. A template defines presentation, and its examples are not project facts.
- If the specified template is missing or unreadable, explain the gap and request accessible content. Continue examining the current state where possible, but do not claim to have followed that template. Ask about competing templates only when the choice is unclear and would affect delivery.
- Establish whether the task describes an existing implementation, designs a new capability, or updates an existing document. Prefer the user's output location and format, then project conventions; otherwise use `docs/design/<topic>.md` and keep diagram sources with the document. Preserve valid content and review comments when updating documents.

## 2. Gather sufficient project evidence

Locate relevant material before reading it closely. Use `rg --files`, `rg`, or equivalent host search tools to find requirements, designs, ADRs, API contracts, data models, and related implementations. Skip build artifacts and third-party dependencies; do not dump the entire repository.

Trace the relevant business path through entry points, business logic, storage, external calls, and tests to identify existing capabilities, constraints, and change locations. Follow additional calls only when they help explain a key design decision. A directory listing is not a design.

Keep these categories distinct:

| Category | Presentation and evidence |
| --- | --- |
| Current facts | Support claims with implementations, contracts, configuration, or documents actually read. Cite relative paths and symbols for key conclusions, adding line numbers when useful. Configuration defaults do not establish production settings, and test cases do not prove tests passed. |
| Proposed design | Explicitly label proposed additions or changes and explain the requirement, change, and impact. Do not present new interfaces, classes, tables, or states as existing implementations. |
| Assumptions and open questions | Identify missing evidence, the decision it affects, and how to confirm it. Do not invent capacity, latency, cost, timelines, or business rules. |

- When existing designs conflict with code, describe both the original design intent and the checked-out implementation. Use code to explain that version's behavior without automatically dismissing business requirements or assuming deployment. Record material conflicts as open questions.
- Record the source version or working tree state when available and meaningful. With uncommitted changes, do not equate the entire snapshot with a single commit. Referenced paths must exist; label paths that do not yet exist as proposed additions.
- When missing information could change business scope, interface compatibility, or the core approach, group a few essential questions together. Complete independent portions and mark them as drafts. List smaller gaps explicitly without repeatedly interrupting for minor details.

## 3. Write a design that can be reviewed

Within the chosen template, connect business requirements to design decisions, change locations, and acceptance criteria before adding detail. Use short paragraphs for small changes and a compact mapping table for work spanning modules or multiple requirements. Avoid maintaining duplicate mappings.

- **Lead with conclusions.** State the goal, scope, and recommended approach first. Explain changes and reasons; avoid repeating background, teaching unrelated terminology, or claiming qualities such as high availability or extensibility without evidence.
- **Scale detail to risk.** Cover module responsibilities, interface inputs, outputs and errors, data constraints, and compatibility as needed. Discuss concurrency, idempotency, transactions, timeouts, retries, compensation, permissions, and observability only where their mechanisms or failure behavior matter to this design.
- **Explain real choices.** When tradeoffs exist, briefly describe alternatives, the recommendation, and its costs. Do not manufacture competing architectures for simple problems. Prefer existing capabilities and explain why any new component is necessary.
- **Make acceptance observable.** Use concrete scenarios and expected results for success, important failures, and boundaries. For persistence or externally visible behavior changes, cover necessary migration, compatibility, release, and rollback constraints.
- **Stay concise and complete.** Let each paragraph answer one question. Use tables for comparable information and code snippets only for contracts or key algorithms that prose cannot explain clearly. Omit full source listings, getters and setters, unrelated fields, and file-by-file walkthroughs.
- **Keep facts traceable.** Cite key evidence near conclusions or connect it in a compact source table. Do not claim validation, testing, or review without corresponding execution records.

## 4. Use diagrams to clarify the design

Choose each diagram by the decision it helps a reviewer make. When drawing, read [diagram selection and examples](references/views.md). Select use case, class, sequence, flow, state, architecture, ER, or deployment diagrams as the business problem requires; there is no required set or fixed count. Include diagrams explicitly required by the template, or explain why they do not apply.

- Place each diagram beside the relevant design and title it with the business question and whether it shows the current or proposed state. Names, directions, cardinalities, call order, conditions, and states must agree with the text and evidence.
- Keep each diagram focused on one question. Split crowded relationships by scenario or level. Do not mix business actors, classes, and deployment instances unless their boundaries and levels are clear.
- Use diagram source formats supported by the project. Without an existing convention, prefer Mermaid; choose PlantUML for strict UML use cases or similar needs when the renderer supports it. Keep editable sources and avoid unsupported syntax.
- Use diagrams for relationships and changes, and prose for rationale, rules, and boundaries. Do not repeat every arrow in prose. Show important rejection, failure, retry, and other paths in an appropriate diagram when they affect a workflow, interaction, or lifecycle.

## 5. Check before delivery

1. **Template and coverage:** Required content is complete, and requirements connect to the design and acceptance criteria. Remove irrelevant sections, template guidance, empty tables, and placeholders. Clearly describe unresolved questions.
2. **Accuracy and consistency:** Check key source files, references, contracts, terminology, and agreement between diagrams and prose. Keep facts, proposals, and assumptions distinct; do not treat old documents or test intent as runtime facts.
3. **Diagram readability:** Use existing project tools to check diagram sources. Render and inspect them when possible, checking clipping, overlap, and readable conditions. Without a renderer, review syntax and semantics, explicitly report that rendering was not verified, and do not claim it passed.
4. **Length and changes:** Remove sentences that do not help understanding or review decisions. Check the diff and preserve the user's existing edits. A documentation task does not require starting services or changing business code.

Finish with a brief response giving the document path, key design conclusions, and open questions that affect review. Do not repeat the entire document in chat.
