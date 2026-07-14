# Workspace Rules & AI Stumping Patterns

Always adhere to these stumping pattern designs and solver playbooks when designing, hardening, or testing task verifiers:

1. **The Homogeneous Sample Trap (Latent Crux):** Ensure visible data samples do not cover all materials/gauge systems/regimes that hidden test cases cover. The agent must fail if it generalizes from the homogeneous visible sample without handling the other hidden regimes.
2. **The Lure (Plausible Heuristic):** Create a cheap, prefix-matching or structure-based heuristic that works on 99% of sample data, but fails on specific edge cases in the hidden test suite (like charged parents or modified keys).
3. **The Decoy (Planted tool/comment):** Maintain tool verification hygiene. Decoy diagnostics pointing at symptoms instead of root cause must not mislead our testing.
4. **Undocumented Conventions:** Uncover constraints through iterative hypothesis verification rather than expecting full documentation of internal parameters.
5. **Epoch Rewriting (Temporal Coupling):** Keep in mind that state transitions are coupled systems; chronological streaming updates must be validated for history rewriting.
6. **Pass@5 Threshold (Solvable Stump):** Verify that the oracle script (`solve.sh`) always achieves 1.0 reward, while the agent's pass@5 score is $\le 2/5$. Failures must be valid (finished and incorrect) rather than timeouts or setup errors.
7. **Timeout Limits:** Maintain the `task.toml` timeout at or below 3600 seconds. Ensure the timeout is set high enough to evaluate cognitive reasoning, not speed or compute efficiency.
8. **Automated Review (Gates):** Address any `FAIL` verdicts or blocking issues immediately by aligning the instruction, solver implementation, and verifier tests. Ensure ground truth tests are independent and tamper-proof.
9. **Verifier Self-Check Checklist:** Validate that every output field format, ID, tie-break, sort order, and edge-case redelivery rule is explicitly specified in the instruction to prevent undisclosed verifier convention rejections.

Always consult [stumping_patterns.md](file:///Users/vsanjay/Downloads/log-report/stumping_patterns.md) for full descriptions of these stumping rules.
