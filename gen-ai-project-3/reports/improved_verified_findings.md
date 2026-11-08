# Improved n8n Verification Results

These results are from the three user-supplied improved n8n Cloud webhook responses.

| Sample | Critical | High | Medium | Total |
|---|---:|---:|---:|---:|
| user_service | 1 | 0 | 2 | 3 |
| backup_utility | 1 | 2 | 2 | 5 |
| billing_calculations | 0 | 1 | 4 | 5 |
| **Total** | **2** | **3** | **8** | **13** |

## Prioritized findings

- **CRITICAL — Potential SQL injection** (user_service, Security Analysis, line 2): Use parameterized queries and bind untrusted values as parameters.
- **CRITICAL — Dynamic evaluation of input** (backup_utility, Security Analysis, line 11): Remove eval/exec and explicitly parse expected data types.
- **HIGH — Shell command execution** (backup_utility, Security Analysis, line 5): Use subprocess argument arrays with shell=False and validate inputs.
- **HIGH — Unsafe deserialization risk** (backup_utility, Security Analysis, line 8): Do not unpickle untrusted data; use a constrained data format such as JSON.
- **HIGH — Mutable default argument** (billing_calculations, Bug Analysis, line 1): Use None and create a new collection inside the function.
- **MEDIUM — No tests provided** (user_service, Test Coverage): Add unit tests for normal, error, and boundary cases.
- **MEDIUM — Missing SQL input safety test** (user_service, Test Coverage): Test unusual and untrusted query parameters with a temporary database.
- **MEDIUM — No tests provided** (backup_utility, Test Coverage): Add unit tests for normal, error, and boundary cases.
- **MEDIUM — Missing dangerous-input regression tests** (backup_utility, Test Coverage): Test rejection of untrusted commands, serialized data, and expressions without executing unsafe payloads.
- **MEDIUM — Potential division by zero** (billing_calculations, Bug Analysis, line 8): Validate the divisor and test zero-count behavior.
- **MEDIUM — No tests provided** (billing_calculations, Test Coverage): Add unit tests for normal, error, and boundary cases.
- **MEDIUM — Missing mutable-default regression test** (billing_calculations, Test Coverage): Test repeated calls and isolation of mutable state.
- **MEDIUM — Missing zero-divisor test** (billing_calculations, Test Coverage): Test division with zero as divisor.

## Scope

All three outputs report `received_items=3`. Findings are heuristic; these results do not measure recall, precision, or executable test coverage. The improved responses were supplied after live n8n Cloud tests.
