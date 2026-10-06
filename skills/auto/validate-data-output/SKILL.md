---
name: validate-data-output
description: Use when generating data analysis reports to ensure output schema and formatting requirements are met.
---
1. Inspect the output file to confirm it contains a metadata object with the source filename, total input rows, and count of processed rows.
2. Verify that all monetary values are represented as integers in cents.
3. Check that timestamps follow the strict ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ).
4. Ensure categorical fields (like regions) match the canonical spelling required by the project.
5. Validate that the output file is correctly formatted (e.g., CSV headers or JSON structure) before submission.
