# Prioritized Findings — Verified Original n8n Runs

| Sample | Critical | High | Medium | Total |
|---|---:|---:|---:|---:|
| user_service | 0 | 0 | 1 | 1 |
| backup_utility | 1 | 1 | 1 | 3 |
| billing_calculations | 0 | 1 | 4 | 5 |
| **Total** | **1** | **2** | **6** | **9** |

- **CRITICAL: Dynamic evaluation of input** (backup_utility; security): Remove eval/exec and parse expected data types explicitly.
- **HIGH: Shell command execution** (backup_utility; security): Use argument arrays with shell=False and validate inputs.
- **HIGH: Mutable default argument** (billing_calculations; Bug Analysis): Replace discounts=[] with discounts=None.
- **MEDIUM: No tests provided** (user_service; Test Coverage): Add unit tests for all functions.
- **MEDIUM: No tests provided** (backup_utility; Test Coverage): Add unit tests for all functions.
- **MEDIUM: Potential division by zero** (billing_calculations; Bug Analysis): Validate count before division.
- **MEDIUM: No tests provided** (billing_calculations; Test Coverage): Add unit tests for all functions.
- **MEDIUM: Missing mutable-default test** (billing_calculations; Test Coverage): Test repeated function calls.
- **MEDIUM: Missing zero-divisor test** (billing_calculations; Test Coverage): Test count = 0.

Known original detection gaps: SQL injection and unsafe pickle deserialization. Improved rules require new live n8n verification.
