---
name: verify-code-standards
description: Use when submitting code changes to ensure compliance with project-wide quality and documentation rules.
---
1. Scan all modified or new public functions for type annotations on parameters and return values.
2. Create a regression test file if one does not exist, ensuring it contains at least one test function per bug fix.
3. Verify that the test suite passes by executing the test runner with the appropriate environment variables.
4. Update the project changelog with a bulleted entry for each fix, following the required format: `- fix(<function_name>): <description>`.
5. Confirm that all new tests and documentation entries are committed or saved before finalizing.
