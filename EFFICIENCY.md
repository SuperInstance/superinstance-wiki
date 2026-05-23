# Subagent Efficiency Manifesto

Bootstrap injection for all subagents. Follow these rules unconditionally.

---

## 1. Parallelization Mandate

- **Batch reads**: Read 4–8 files in one parallel burst.
- **Batch searches**: Fire 3–5 queries simultaneously.
- **Batch writes**: Write 2–4 files at once.
- **Mixed parallel**: Combine reads, execs, and writes in the same turn when they are independent.
- **Maximum**: Up to 5 tools may be called simultaneously.
- **Prohibition**: Never execute independent operations serially. If two or more calls have no data dependency, they must be parallel.

---

## 2. Phase Discipline

| Phase | Turns | Goal |
|---|---|---|
| **EXPLORE** | 1 | Parallel gather of all relevant context, files, logs, and search results. |
| **ANALYZE** | 1–2 | Process gathered data, identify root causes or required changes, plan the minimal diff. |
| **EXECUTE** | 1–2 | Apply parallel writes, edits, and commands. No new discovery here. |
| **VERIFY** | 1 | Confirm correctness: re-read changed files, run tests, check diffs. |

- **Total budget**: 4–6 turns for a standard task.
- **Yield immediately** if a task exceeds 8 turns. Report what is done and what remains.

---

## 3. Spawn Discipline

- **Default**: Do NOT spawn subagents.
- **Spawn only if ALL of the following are true**:
  1. The task is fully independent of the current workflow (no shared context needed).
  2. The task objectively requires more than 20 turns.
  3. The parent agent can afford to wait (not blocking a critical path).
  4. OR the task involves fundamentally different expertise (e.g., browser automation vs. shell scripting).
- **Light context**: For simple or well-scoped subtasks, always use `lightContext=True` to minimize token overhead.

---

## 4. Rate Limit Protocol

- On receiving a **429 / rate-limited / overloaded** response:
  1. Wait **5 seconds**.
  2. Retry **once**.
  3. If the second attempt fails, **yield immediately** and report the rate-limit to the parent.
- **Never retry more than once.** Do not escalate into retry loops.

---

## 5. Write Check

Before every write operation, perform both checks:

1. **Existence check**: Verify whether the target file already exists.
2. **Content check**: If it exists, compare the proposed content against the current content.
3. **Action**:
   - If identical → skip the write entirely.
   - If different → overwrite.

This prevents redundant rewrites, reduces API calls, and avoids unnecessary diffs.
