Earned all four Anthropic Claude certifications: Associate Foundations, Developer Foundations, Architect Foundations, and Architect Professional.

For anyone pursuing the stack, here is what each one actually demands.

𝗖𝗹𝗮𝘂𝗱𝗲 𝗖𝗲𝗿𝘁𝗶𝗳𝗶𝗲𝗱 𝗔𝘀𝘀𝗼𝗰𝗶𝗮𝘁𝗲, 𝗙𝗼𝘂𝗻𝗱𝗮𝘁𝗶𝗼𝗻𝘀
The entry point. Be ready on model family tradeoffs, capabilities and limits, prompting fundamentals, and the judgment of when Claude is the right tool and when it is not. Daily use of the platform is the best preparation. Reading about it is not enough.

𝗖𝗹𝗮𝘂𝗱𝗲 𝗖𝗲𝗿𝘁𝗶𝗳𝗶𝗲𝗱 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿, 𝗙𝗼𝘂𝗻𝗱𝗮𝘁𝗶𝗼𝗻𝘀
Assumes you have shipped. Be ready on tool use with JSON schemas, structured outputs, MCP development, hooks, agent construction, and debugging real failures. Write working code against the API before this one. The exam can tell.

𝗖𝗹𝗮𝘂𝗱𝗲 𝗖𝗲𝗿𝘁𝗶𝗳𝗶𝗲𝗱 𝗔𝗿𝗰𝗵𝗶𝘁𝗲𝗰𝘁, 𝗙𝗼𝘂𝗻𝗱𝗮𝘁𝗶𝗼𝗻𝘀
The most hands-on of the four, and the least forgiving. Be ready to design multi-agent systems across coordinator-worker, parallel, and sequential patterns. Scope subagents with restricted tools and tightly written prompts. Manage context across sessions that outgrow the window. Configure Claude Code properly: CLAUDE.md, rules, Skills, hooks, permissions. If you have not built a multi-agent pipeline end to end, build one before you book this exam.

𝗖𝗹𝗮𝘂𝗱𝗲 𝗖𝗲𝗿𝘁𝗶𝗳𝗶𝗲𝗱 𝗔𝗿𝗰𝗵𝗶𝘁𝗲𝗰𝘁, 𝗣𝗿𝗼𝗳𝗲𝘀𝘀𝗶𝗼𝗻𝗮𝗹
Scenario judgment from start to finish. Be ready to translate a business problem into an architecture and defend every choice: model selection, cost and latency tradeoffs, retrieval strategy, integration mechanism. Evaluation is tested seriously: metrics, datasets, test frameworks. So are security, compliance, and guardrails. It reads like client work because it is client work.

The bigger takeaway: agentic AI is becoming a discipline. A body of knowledge, standards of practice, and credentials that test judgment rather than vocabulary.

The AI architecture layer of the build is complete. Data and platform layers are underway.

Credit to the Anthropic team for setting a genuinely high bar.

𝗡𝗼𝘁𝗲: these are Partner Exclusive certifications, currently available to Claude Partner Network members.



1) AI Fluency: Framework & Foundations


SystemDesign Primer
1) perfromance vs scalability
2) latency vs throughput
3) availibility vs consistency
4) sql vs nosql

Design patterns
- Design pattern

Deepdives
- API ratelimiter
- caching
- concurrency
- event/kafka design
- elastic search
- time series database

System Design
- bookmyshow
- tinder
- ride hailing
- chatgpt
- ad click agggregator
- notification system
- payment system
- google doc
- UPI system design
- stock exchange


Database
    Relational database management system (RDBMS)
        Master-slave replication
        Master-master replication
        Federation
        Sharding
        Denormalization
        SQL tuning
    NoSQL
        Key-value store
        Document store
        Wide column store
        Graph Database
SQL or NoSQL




Yes. For your software-architecture background, I recommend a **4-week, hands-on learning path** rather than only watching videos. The official CCA-F exam tests trade-offs across Claude Code, Claude Agent SDK, Claude API, and MCP—not just prompt writing. cite [anthropic.skilljar](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)

## Start with these links

### Official resources

1. [CCA-F official Anthropic Academy page](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)  
   First download/read the official exam guide available on this page. Treat it as the primary syllabus. cite [anthropic.skilljar](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)

2. [Claude Code official overview](https://docs.anthropic.com/en/docs/claude-code/overview)

3. [Claude Code 101](https://anthropic.skilljar.com/claude-code-101)  
   This is a free introductory course covering installation, agentic loops, Plan Mode, context management, `CLAUDE.md`, subagents, skills, MCP, hooks, and the course quiz. cite [anthropic.skilljar](https://anthropic.skilljar.com/claude-code-101)

4. [Claude Code quickstart](https://code.claude.com/docs/en/quickstart)

5. [Claude Code documentation index](https://code.claude.com/docs/llms.txt)

### Free video courses

- [Claude Certified Architect complete study guide](https://www.youtube.com/watch?v=of9PPnuBedU) — covers the five domains, scenarios, exam strategy, and sample questions. cite [youtube](https://www.youtube.com/watch?v=of9PPnuBedU)
- [Claude Certified Architect full course – Episode 1](https://www.youtube.com/watch?v=ldqOnljDINc) — useful for learning from the beginning. cite[
- [CCA-F study guide and free preparation repository](https://www.youtube.com/watch?v=rE6cb96M6ks) — includes a GitHub repository with labs, cheat sheets, MCQs, and a four-week plan. cite[
- [How I passed CCA-F and free study kit](https://www.youtube.com/watch?v=SYYtM16wXcI) — includes a free GitHub study-lab repository and exam-preparation workflow. cite[

### Free practice questions

- [Tutorials Dojo free practice sampler](https://portal.tutorialsdojo.com/product/free-claude-certified-architect-foundations-ccar-f-practice-exams-sampler/)
- [FlashGenius free practice questions](https://flashgenius.net/sample-tests/ccar-f)
- [60-question free practice exam](https://szymonpaluch.com/blog/posts/claude-certified-architect-practice-questions)

Use practice questions for learning, not memorization. Avoid relying on “exam dumps”; they may be inaccurate and do not develop the architecture reasoning the exam requires.

## Four-week learning path

The commonly reported domain distribution is approximately:

| Domain | Approx. weight | Priority |
|---|---:|---:|
| Agentic architecture and orchestration | 27% | Highest |
| Claude Code configuration and workflows | 20% | High |
| Prompt engineering and structured output | 20% | High |
| Tool design and MCP integration | 18% | High |
| Context management and reliability | 15% | Important |

These five areas are reflected in the available CCA-F preparation materials and practice exams. cite[ cite[

### Week 1: Agentic architecture

**Study**

- Agentic loop: observe, reason, act, verify.
- Single-agent versus multi-agent design.
- Coordinator–subagent patterns.
- When to use sequential, parallel, or iterative execution.
- Tool permissions, human approval, retries, failure handling, and idempotency.
- State management and long-running workflows.

**Official reading**

- [Claude Code overview](https://code.claude.com/docs/en/overview)
- [Custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Agent SDK overview](https://docs.anthropic.com/en/docs/agents-and-tools/agent-sdk/overview)
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices)

**Hands-on exercise**

Create a small repository and ask Claude Code to:

1. Explore the repository.
2. Create an implementation plan.
3. Delegate testing to a subagent.
4. Implement the change.
5. Run tests and report failures.
6. Review its own changes.

Write down why you selected one agent, multiple agents, or a sequential workflow.

**Checkpoint**

You should be able to answer: “Why is this task better handled by a coordinator and two specialized subagents rather than one large prompt?”

### Week 2: Claude Code configuration and workflows

**Study**

- Explore → Plan → Code → Commit.
- `CLAUDE.md` hierarchy and project instructions.
- Plan Mode and approval modes.
- Context commands such as `/compact`, `/clear`, and `/context`.
- Skills and reusable workflows.
- Subagents and isolated context.
- Hooks for deterministic checks.
- CI/CD and pull-request automation.

**Official reading**

- [Claude Code memory and `CLAUDE.md`](https://code.claude.com/docs/en/memory)
- [Skills](https://code.claude.com/docs/en/skills)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Context windows](https://code.claude.com/docs/en/context-window)

Claude Code uses `CLAUDE.md` for persistent project instructions, skills for repeatable workflows, hooks for deterministic lifecycle actions, and subagents for isolated delegated work. cite[ cite[ cite[

**Hands-on exercise**

Create the following files in a demo project:

```text
CLAUDE.md
.claude/skills/code-review/SKILL.md
.claude/agents/test-engineer.md
.claude/settings.json
```

Configure them to:

- Apply your coding and architecture standards.
- Run a code-review skill.
- Delegate test creation to a subagent.
- Block dangerous shell commands.
- Run formatting and unit tests after changes.

**Checkpoint**

Explain when you would use:

- `CLAUDE.md` instead of a skill.
- A skill instead of a subagent.
- A hook instead of relying on Claude’s instructions.
- A subagent instead of asking Claude to do everything in one context.

### Week 3: Tools, MCP, API, and prompts

**Study**

- Tool schemas and clear tool descriptions.
- Client tools versus server tools.
- MCP architecture: tools, resources, and prompts.
- Authentication and authorization.
- Read-only versus write-capable tools.
- Tool error handling and validation.
- Prompt structure, examples, XML tags, and role instructions.
- Structured output and schema validation.

**Official reading**

- [Tool use with Claude](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)
- [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Claude prompting best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [MCP quickstart in Claude Code](https://code.claude.com/docs/en/mcp-quickstart)
- [MCP introduction](https://modelcontextprotocol.io/docs/getting-started/intro)
- [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

MCP connects AI applications to external data, tools, and workflows; its main server primitives are tools, resources, and prompts. cite[ cite[

**Hands-on exercise**

Build a small MCP server or use an existing local MCP server that exposes:

- A read-only tool, such as `search_documents`.
- A resource, such as architecture documentation.
- A prompt template, such as `review_design`.
- One write operation protected by explicit user approval.

Then test:

- Invalid parameters.
- Timeouts.
- Duplicate requests.
- Unauthorized access.
- Tool failures.
- Sensitive data in tool responses.

**Checkpoint**

For every tool, be able to explain:

- What input schema does it expose?
- What permissions does it require?
- Can it safely be retried?
- Is the operation read-only or state-changing?
- How are failures and partial results returned?

### Week 4: Context, reliability, and exam practice

**Study**

- Context-window limits.
- Context compaction and summarization.
- Prompt caching.
- Retrieval and selective context loading.
- Keeping instructions separate from data.
- Evaluation and regression testing.
- Observability, retries, timeouts, and fallbacks.
- Security, privacy, prompt injection, and excessive permissions.

**Official reading**

- [Context windows](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)
- [Prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Claude Code security](https://code.claude.com/docs/en/security)
- [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [Prompting best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)

Context management is important because tool use, extended thinking, cached input, and conversation history all affect the available context. cite[

**Hands-on capstone**

Build an **AI architecture-review assistant**:

1. Store sample architecture documents in a repository.
2. Add project rules in `CLAUDE.md`.
3. Add a `review-architecture` skill.
4. Create an architecture-review subagent.
5. Add an MCP tool to search documents.
6. Require structured JSON output:

```json
{
  "risks": [],
  "recommendations": [],
  "assumptions": [],
  "open_questions": [],
  "confidence": "high|medium|low"
}
```

7. Add a hook that runs schema validation.
8. Test prompt injection, missing documents, oversized context, tool timeout, and conflicting requirements.
9. Document your architecture decisions and trade-offs.

This project is especially suitable for you because it connects your existing solution-architecture experience with Claude Code, MCP, agent orchestration, and reliability engineering.

## Daily routine

Spend approximately 75–90 minutes per day:

- 20 minutes: official documentation.
- 30 minutes: hands-on implementation.
- 15 minutes: write architecture notes.
- 15–25 minutes: practice questions.

Maintain a one-page table like this:

| Topic | What I learned | Design trade-off | Example |
|---|---|---|---|
| Subagents | Separate context and delegation | More isolation, more coordination overhead | Test engineer |
| Hooks | Deterministic automation | Reliable but limited to defined lifecycle points | Run lint after edits |
| MCP tools | External actions and data | Powerful but increases security risk | Jira lookup |
| Context compaction | Preserve useful state | May lose details | Long coding session |

## Final seven-day revision

- **Day 1:** Agentic architecture and orchestration.
- **Day 2:** Claude Code configuration, `CLAUDE.md`, skills, and hooks.
- **Day 3:** Subagents, Agent SDK, and workflow design.
- **Day 4:** MCP and tool design.
- **Day 5:** Prompt engineering, structured output, and context management.
- **Day 6:** Complete one timed practice exam.
- **Day 7:** Review every incorrect answer and explain why each wrong option is wrong.

Do not schedule the exam merely because you completed the videos. Schedule it when you can consistently score around **80–85%** on fresh practice questions and explain the design trade-offs behind your answers.

### Recommended order

Start with:

1. [Claude Code 101](https://anthropic.skilljar.com/claude-code-101)
2. [Official CCA-F exam guide](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)
3. [Claude Architect complete YouTube guide](https://www.youtube.com/watch?v=of9PPnuBedU)
4. [Claude Code documentation](https://code.claude.com/docs/llms.txt)
5. The hands-on architecture-review capstone
6. Free practice tests

The free learning material is sufficient for preparation, although actual Claude Code usage may require a Claude subscription or Anthropic Console/API account depending on the interface you use. cite[