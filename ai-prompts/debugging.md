# AI Prompts — Debugging

## 1. Purpose

This document records how AI was used during the debugging and validation of the
AI Capability Exercise — Medallion Architecture Data Pipeline.

The purpose was not to blindly accept AI-generated fixes, but to use AI to:

- Understand error messages
- Identify likely root causes
- Compare possible solutions
- Validate the proposed changes
- Apply the smallest appropriate fix
- Re-run tests after changes
- Document the debugging process and lessons learned

The main debugging areas covered were:

1. Local PySpark/Spark environment setup
2. Java version compatibility
3. Spark driver binding issues
4. Data quality test failures
5. Validation of the final test suite

---

# 2. Debugging Approach

I followed this general debugging workflow:

1. Run the relevant command or test.
2. Capture the complete error message.
3. Identify the first meaningful/root error rather than focusing on
   secondary warnings.
4. Provide the error and relevant project context to the AI tool.
5. Ask AI to explain the likely root cause.
6. Compare the suggested solution with the project requirements.
7. Apply the smallest required change.
8. Re-run the failing test or command.
9. Run the complete test suite.
10. Record the result and what was learned.

This approach helped separate environment-related failures from actual
application or data-quality logic failures.

---

# 3. Debugging Issue: Java Version

## Problem

The project uses PySpark locally. When setting up the local environment,
Java was initially configured to OpenJDK 11.

The initial Java version was:

```text
openjdk version "11.0.29" 2025-10-21
OpenJDK Runtime Environment Homebrew (build 11.0.29+0)
OpenJDK 64-Bit Server VM Homebrew (build 11.0.29+0, mixed mode)