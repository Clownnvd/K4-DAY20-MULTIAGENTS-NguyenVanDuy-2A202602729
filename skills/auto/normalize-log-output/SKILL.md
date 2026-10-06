---
name: normalize-log-output
description: Use when parsing logs to ensure service names and error structures are consistent.
---
1. Transform all service names to lower-case and replace hyphens with underscores.
2. Sort the final error list primarily by service name and secondarily by timestamp in ascending order.
3. Ensure the top-level output object includes the required schema version and generator metadata.
4. Verify that all log entries are aggregated correctly, including handling of repeated messages and traceback extraction.
5. Run a validation script to confirm the output JSON structure matches the expected schema.
