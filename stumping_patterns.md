# Strategies & Stumping Patterns for AI Coding Agents

This document records the strategies, stumping patterns, pass@/timeout requirements, automated review gates, scoring rubrics, rejection examples, and verifier self-check lists used to evaluate, harden, and verify agent capabilities in Project Dynamo.

---

## 1. Core Principle
**The model stops at the first green result.**
It tunes to the visible sample data, trusts the obvious rule or diagnostic tool, and never verifies the edge cases it cannot see. A robust task must defeat these lazy solver playbooks to confirm true reasoning and domain mastery.

---

## 2. Stumping Patterns (How Tasks Stump the Model)

### A. The Latent Crux (Homogeneous Sample Trap)
* **Concept:** The visible training or validation sample is completely homogeneous along the one axis that actually matters.
* **Example:** A CAD weight calculator is calibrated using sample parts that are all steel. The agent parses the geometry, applies standard steel gauge-to-thickness tables, and gets perfect validation matches. However, the hidden test cases feature parts made of other metals (aluminum, copper) which use a different gauge standard. 
* **Crux:** The more carefully the agent validates against the visible homogeneous sample, the more confident it becomes in the wrong generic implementation.

### B. The Lure (Plausible/Cheap Heuristics)
* **Concept:** There is a highly intuitive, cheap heuristic that matches the correct rule on 99% of common cases, but diverges on subtle edge cases.
* **Example:** Exclude parent "rollup" rows from a ledger. The intuitive prefix-path rule (`warehouse/east` is parent of `warehouse/east/dock-3`) works on almost everything. The correct rule is value-based (a row is a rollup only if its sum matches child sums). The heuristic diverges on "charged parents" (parents that carry their own charges in addition to children), resulting in silent under-counting.
* **Crux:** The agent takes the cheap bait because it passes casual inspection of visible data, causing a silent failure.

### C. The Decoy (Planted Tools or Comments)
* **Concept:** Providing an official-looking, convenient diagnostic tool, documentation, or code comment that points directly to a downstream symptom rather than the root cause.
* **Example:** During a cascade service outage, a built-in diagnostic tool names service X as the failure root. The agent accepts this answer without tracing the actual service dependency graph back to the upstream cause Y.
* **Crux:** It weaponizes the agent's eagerness to close the task. The agent skips verification because a trusted-looking tool already gave it an answer.

### D. Undocumented Conventions (Hypothesis Testing)
* **Concept:** Enforcing system rules, sentinels, scale factors, or custom structures that are completely undocumented but mathematically forced by the data patterns.
* **Example:** A metrics aggregator service crashed and its code is lost. The agent must reverse-engineer its behavior from logs. The logs contain hidden behaviors: sentinel values for overflow, milliseconds vs seconds timestamps, or rate series scaled by scrape intervals.
* **Crux:** The task requires senior debugging—forming and testing hypotheses against the outputs—forcing the agent to actively analyze the data rather than guessing.

### E. Silent Invariant Breaking
* **Concept:** Quietly breaking an implicit invariant (like sorted files, non-zero values, or chronological order) that holds true in the visible samples.
* **Example:** A stateful GPS decoder tracks rollover cycles by assuming records are chronological. The hidden log contains records out of order (jumping backward in time), causing the stateful assumption to append spurious extra cycles.
* **Crux:** Because the assumption was never stated, the agent never thinks to question it, and validation against chronological sample data reinforces the blind spot.

### F. Joint Guesses / Closed-Fail Authorization
* **Concept:** A security task where guessing is required, but wrong guesses yield identical opaque errors with zero information leakage.
* **Example:** An exploit requires providing the correct combination of role, scope, and channel, but failures fail closed with no feedback on which of the three fields was wrong.
* **Crux:** Prevents binary search narrowing. The value must be discoverable in principle (e.g. hinted in documentation or protocol logs) to test skill rather than luck.

### G. Breadth (All-or-Nothing Interacting Bugs)
* **Concept:** A task containing multiple independent bugs that interact. There is no partial credit—fixing 7 out of 8 bugs still yields a score of 0.
* **Example:** Fixing a binary relinker with 8 distinct alignment, revision, and kind-encoding bugs.
* **Crux:** The agent must resolve all edge cases to pass, preventing partial heuristic shortcuts.

### H. Epoch Rewriting (Event History Coupling)
* **Concept:** Implementing sequential state updates that appear correct when evaluated one at a time, but structurally rewrite or invalidate past states in subtle ways.
* **Example:** Ledger reversals, bitemporal timelines, document approval workflows with resets and revocations. A reset or revocation changes the meaning or validity of historical parent-child states.
* **Crux:** The natural incremental stream implementation fails; the solver must reason about the event history as a coupled system.

### I. Cutoff & Versioning (Point-in-Time Joins)
* **Concept:** Joining data tables as of a specific cutoff time, where retro-corrected entries or late updates exist in the database but must be ignored relative to the historical cutoff.
* **Example:** Valuation of historical fund assets where price revisions were posted late.
* **Crux:** Default code queries the "current" or "latest" value, which silently rewrites history and fails the valuation as of the cutoff day.

---

## 3. Understanding pass@ & Timeouts

### A. The Evaluation Pipeline
Tasks progress through the following automated gates:
1. **Proposal:** Idea draft and submission.
2. **Pull Request:** Open PR containing full task resources.
3. **Validity Check:** Automated LLM format/validation scan.
4. **Pass@2 Check:** Two parallel trials at the `task.toml` timeout. If either run times out or fails environment setup, the PR is blocked.
5. **Automated Review (Gates):** Complete rubric review. All Blocking Issues must be resolved before proceeding.
6. **Pass@5 Check:** Five parallel trials evaluated using the reference model.

### B. Defining a "Good" Task (Solvable Stump)
* **Rule:** The oracle must solve the task (reward = 1.0) while the model must fail at least 3 of 5 attempts.
* **Target:** **pass@5 ≤ 2/5** (0/5, 1/5, or 2/5 are accepted).
* **Valid Failure:** The model completes execution but produces a wrong answer. Timeouts, environment crashes, or ambiguous/unfair prompts **do not count** as valid failures.

### C. Timeout Rules & Best Practices
* **Cap:** 3600 seconds (1 hour) is the absolute ceiling.
* **Correctness focus:** The timeout must be long enough for the model to think and finish. If a model times out, the task has become a speed test rather than a cognitive challenge.
* **Fixing 0/5 Timeouts:** If all 5 runs fail due to timeouts, raise the timeout (up to 3600s) or shift complexity from computation (expensive loops, big builds) to reasoning.

### D. Hardening 3-5/5 Tasks
If the model passes 3 or more times (too easy), increase difficulty by:
* Adding edge cases or degenerate data regimes the model must explicitly handle.
* Requiring multi-step reasoning or interacting variables.
* Strengthening verifier constraints (e.g., exact sizing checks or tight math bounds) to reject approximate solutions.
* **Important:** Never game the score by lowering timeouts or adding trivial busywork.

---

## 4. Automated Review (Gates)

### A. Purpose & Execution
Runs after a successful Pass@2 pre-check but before Pass@5. It conducts a deep gap-rubric review of the whole task branch (`instruction.md`, `solution/`, `tests/`, `Dockerfile`, and agent traces) to preemptively catch blocking defects before human review.

### B. Crucial Rubric Areas checked:
* **Test Coverage:** Every instruction constraint must map to a test assertion.
* **Independent Expected Values:** Expected outcomes must be verified independently, not by blindly trusting the oracle.
* **Fixture/Tamper Protection:** Ground truth files must not reside in or be read directly from agent-writable folders (like `/app/` or local code dirs) unless re-copied or checksum-verified.
* **Traceability:** Instructions, solutions, and tests must align in terms of paths, schemas, and limits.
* **Clean Trace Hygiene:** Agent trials must prove that no reward-hacking or tests/solution directory leaks occurred.

---

## 5. PR Checks & Rejection Reasons

### A. The Five Rejection Reasons (And How to Avoid Them)

| Reason | What it is | How to Avoid It |
| :--- | :--- | :--- |
| **Undisclosed verifier convention** | The verifier requires a specific format, sort order, tie-break, or scale factor that `instruction.md` never mentions. | Disclose every rule, constraint, and expected output detail in the instruction. If multiple sound methods exist, specify the canonical one. |
| **Contradictory shipped data / spec** | A shipped fixture, config, or reference solution contradicts the written instruction. | Ensure every reference file and solution matches the instruction perfectly. Regenerate fixtures upon editing specifications. |
| **Ambiguous spec** | A rule or formula has multiple valid mathematical interpretations, and the verifier accepts only one. | Clarify sorting, rounding, or mapping rules explicitly. If ambiguity remains, correct it before evaluating difficulty. |
| **Collapsed difficulty** | The task relies entirely on a single unstated rule or trick; once that trick is disclosed, the task is trivial. | Anchor difficulty in complex core reasoning that survives full disclosure of conventions. |
| **Misleading decoy documents** | Pointing the agent at a wrong rule using an authoritative decoy document with no way for the agent to correct it. | Avoid uncorrectable lies. Misdirection is only permitted if the task environment provides material to set the record straight. |

### B. Amplifiers & Fairness
* **Amplifier: Silent Failure:** Make wrong answers believable near-misses rather than crash-inducing exceptions, so the agent stops debugging and submits.
* **Amplifier: No Self-Check:** Keep the local samples friendly and simple, but grade against hidden test cases.
* **Amplifier: All-or-Nothing:** Refuse partial credit. If the final output is 90% correct, it still scores 0.
* **Fairness Gut Check:** Would a human domain expert, seeing only what the agent sees, get it right and call the failure fair? If they'd be stuck or forced to guess, the task is unfair.

---

## 6. Scoring (Checkboxes & Quality Scores)

Reviewers evaluate tasks on arrival using a 1–5 Standard Quality Score and specific gate checkboxes.

### A. Issue Checkboxes:
* **Instructions are overspecified:** The prompt details libraries, algorithms, or sequential steps, removing the cognitive crux.
* **Instructions are underspecified:** Missing verifier conventions, arbitrary choices, or unresolvable ambiguities.
* **Verifiers too tight:** Rejects sound alternative implementations due to over-constrained numerical tolerances.
* **Verifiers too loose:** Allows wrong or approximate answers to pass, or suffers from bypasses.
* **Task is not realistic:** Trivial toy puzzles or gimmicks.
* **Incorrect/irrelevant info:** Drifted paths, incorrect facts, or misleading filler.

### B. Standard Quality Score (1-5 Calibration):
* **5 (No Issues):** Verdict is `Accept`.
* **4 (Minor Issues):** Minor non-blocking typos or untested requirements. Verdict is `Accept`.
* **3 (Blocking-but-Fixable):** Ambiguities, category mismatch, or missing `test.sh`. Verdict is `Revise`.
* **2 (Major Design Flaws):** Poor code quality, hardcoded solutions, or flaws that flip difficulty upon fixing. Verdict is `Revise` (if salvageable) or `Reject`.
* **1 (Bad Faith / Spam):** Attempter ignored prior feedback or submitted generic auto-generated spam. Verdict is `Reject`.

---

## 7. Common Errors & Rejection Examples

### A. SQLite Job Queue (Undisclosed string literal)
* **Problem:** Verifier requires an exact string literal (`details = {"reason":"lease_expired"}`) not documented anywhere in the instruction or docstrings.
* **Avoidance:** Disclose the exact details schema payload for each event, or ignore the undocumented fields in verifier tests.

### B. Billing Ledger Repair (Naming convention not specified)
* **Problem:** Output requires literal IDs (`F001`, `F002`) but the naming sequence rule isn't stated, so agent's dual-namespace fails.
* **Avoidance:** Specify ID sequencing (e.g., sequential sorted by account) in the instructions, or match by account IDs.

### C. Retrieval Audit (Aggregation semantics not specified)
* **Problem:** A candidate violates multiple constraints. The golden solution uses a hidden priority sequence (`tenant -> language -> model -> snapshot`) to record a single error code, summing to 313. The agent counts every violation, resulting in a sum of 373, and fails.
* **Avoidance:** Explicitly state the single-assignment prioritization rule.

### D. Event Log Compaction (Underspecified duplicate handling)
* **Problem:** The verifier processes duplicate events, but textbook deduplication logic built by the agent drops them and fails the expected counter.
* **Avoidance:** Explicitly specify duplicate redelivery rules (e.g., "process all lines including duplicate sequence IDs").

### E. Over-strict or broken verifier
* **Problem:** Demanding byte-exact text, exact float formatting, or specific key order when the spec doesn't require it.
* **Avoidance:** Parse and compare JSON/dicts, normalize whitespace, and use floats with defined thresholds.

---

## 8. Verifier Self-Check Checklist

Confirm each item is ticked before submitting:

- [ ] **Exact Output Schema:** All output formats, naming conventions, exact error messages, and string literals are fully specified in `instruction.md`.
- [ ] **No Hidden Expectations:** The verifier asserts strictly on things explicitly specified in the instruction.
- [ ] **Explicit Priority & Ordering:** If values are sorted or aggregated, the single canonical rule, sorting precedence, and tie-breakers are stated.
- [ ] **Deduplication / Exception rules:** Edge cases like duplicates or redeliveries are clearly defined.
- [ ] **Flexible Assertions:** Verifier compares structured items (parsed dicts/JSON) rather than raw bytes or arbitrary formatting.
- [ ] **No Spoilers:** No code comments, docstrings, filenames, or READMEs disclose the bug or expected output values to the agent.
- [ ] **Authoritative Material:** The instruction names every file the agent should use to solve the task.
- [ ] **Task Security:** No payloads, environment flags, or comments command the agent to bypass the verification logic.
