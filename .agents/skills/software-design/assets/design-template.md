<!-- Use only when neither the user nor the project provides an applicable template. Merge or remove sections to fit the scope while retaining the information needed to solve the problem. Remove this comment and all placeholder guidance after completing the document. Place diagrams in the relevant sections instead of adding a duplicate "All diagrams" section. Write generated headings, prose, tables, and diagram labels in the user's output language selected by SKILL.md. Preserve project identifiers, referenced paths, and the format of any user-specified template. The English examples do not require English output. -->
# [Topic] Design

Status: [Draft / Ready for review / Confirmed; use Confirmed only when supported by evidence of confirmation]

Basis: [Requirement sources; code revision or workspace state; state honestly when unknown]

## 1. Goals and Scope

[Describe the business problem, goal, and recommended approach in one paragraph.]

- In scope: [Roles, scenarios, and capabilities involved]
- Out of scope: [Items that could be mistaken for part of this work; remove if none]
- Key constraints: [Confirmed business rules, compatibility requirements, or resource limits; cite their sources]

## 2. Current State and Changes

[Describe only the current state, gaps, and conflicts with existing designs relevant to this work. Reference actual paths and symbols. Include a diagram of the current boundaries when needed.]

| Concern | Current implementation and evidence | Proposed change and impact |
| --- | --- | --- |
| [Capability / Module] | [Behavior; paths and symbols] | [Reuse / Modify / Add; affected parties] |

## 3. Design

### 3.1 Responsibilities and Key Decisions

[Explain module responsibilities, interaction boundaries, the recommended approach, and its rationale. Describe costs and rejected alternatives when there are meaningful tradeoffs. Mark new entities or components as proposed.]

[Include an architecture or class diagram when needed, showing only relationships that affect this decision.]

### 3.2 Business Scenarios and Behavior

[Describe actors, preconditions, rules, and outcomes for each scenario. Use use case diagrams for goals spanning roles, sequence diagrams for collaboration through calls, flowcharts for branching rules, and state diagrams for lifecycle constraints. Choose diagrams that reduce the amount of prose needed.]

[Add key failure cases, boundaries, and handling that the diagrams cannot fully express; do not restate them step by step.]

## 4. Interfaces and Data

[Include only contracts that change or constrain this design. Merge this section into the previous one if no interfaces or data change.]

| Contract / Model | Proposed change | Constraints and failure behavior | Compatibility impact |
| --- | --- | --- | --- |
| [Interface, event, table, or entity] | [Key inputs and outputs, fields, or states] | [Validation, uniqueness, error semantics, etc.] | [Impact on callers and existing data] |

[Provide a small structural example or ER diagram when needed. Explain relevant transaction, consistency, idempotency, and concurrency boundaries without copying complete field lists.]

## 5. Quality and Delivery

[Describe only the performance, security, observability, or availability requirements and implementation mechanisms relevant to this design. Cite sources for supported metrics; otherwise mark them as proposed targets or pending measurement instead of supplying rule-of-thumb numbers.]

[When the design affects a release, explain dependencies, migration, compatibility, release order, and rollback. State recovery limitations for irreversible data changes. Remove this guidance from a current-state document when it does not apply.]

## 6. Acceptance and Risks

| Requirement / Scenario | Addressed in | Acceptance method and expected outcome |
| --- | --- | --- |
| [Business goal or key failure case] | [Section, module, or contract] | [Observable outcome; do not present it as a passed test] |

| Risk / Open question | Impact | Mitigation / Confirmation method |
| --- | --- | --- |
| [Specific uncertainty or risk] | [Affected scope and blocked decisions] | [Recommended action or fact requiring confirmation] |

## 7. References

[List key requirements, existing designs, code, and tests not yet cited near the relevant text, identifying the conclusion each supports. Remove this section if references are already cited nearby and do not need a consolidated list.]
