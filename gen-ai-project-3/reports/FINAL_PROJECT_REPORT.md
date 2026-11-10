# Final Project Report — Multi-Agent Code Review System

**Project:** Gen AI Project 3 — Multi-Agent Code Review  
**Report date:** November 2026  
**Implementation:** n8n Cloud workflow, JavaScript rule-based agents, GitHub Pages web UI  
**Repository:** https://github.com/rrama2/ai-code/tree/main/gen-ai-project-3  
**Dashboard:** https://rrama2.github.io/ai-code/gen-ai-project-3/ui/  
**Workflow export:** [latest-published-export.json](../workflow/latest-published-export.json)

## 1. Executive summary

This project implements a web-accessible, multi-agent code review pipeline for Python source code. A GitHub Pages dashboard submits a code sample and optional test text to a published n8n webhook. Three parallel JavaScript review agents examine the submitted source for common bug patterns, security concerns, and missing test scenarios. Their outputs are merged, deduplicated, prioritized by severity, and returned as structured JSON for the dashboard to display.

The latest supplied workflow export contains **eight nodes** and is marked **active**. User-reported dashboard results for three deliberately flawed samples show **14 findings**: **2 Critical, 3 High, 8 Medium, and 1 Low**. Earlier independently recorded n8n webhook responses produced **13 findings**; the later dashboard results included one additional Low-severity database connection lifecycle finding.

**Important distinction:** These are rule-based static checks, not autonomous LLM reasoning or comprehensive Python security analysis. The system does not execute submitted Python code or measure actual test coverage.

## 2. Problem statement and objectives

Manual code review can be repetitive and inconsistent when checking routine issues such as unsafe input handling, mutable defaults, and missing boundary-case tests. The project's objective is to demonstrate how specialized reviewers can run in parallel and return one actionable, severity-ranked report.

The implementation objectives are:
- Accept a Python code sample and optional tests via an HTTP POST request.
- Validate required request fields and reject oversized source submissions.
- Run specialized Bug, Security, and Test Coverage review stages in parallel.
- Merge and deduplicate findings, preserving agent identity, rule ID, severity, location when available, and remediation advice.
- Return machine-readable JSON for a browser UI with filtering and export.
- Verify the workflow using three sample programs and document the results.

## 3. Technology stack

| Layer | Technology | Role |
|---|---|---|
| Workflow orchestration | n8n Cloud | HTTP webhook, branching, merging, response |
| Review rules | JavaScript in n8n Code nodes | Source-pattern checks and test-gap checks |
| Input under review | Python source as text | Review subject; not executed |
| Browser interface | HTML, CSS, JavaScript | Sample selection, live/demo modes, findings, filters, JSON export |
| Hosting | GitHub Pages | Static dashboard deployment |
| Version control | GitHub | Workflow exports, scripts, samples, reports, UI |
| API transport | HTTPS / JSON | Browser or command-line POST to n8n |

## 4. Architecture

```text
GitHub Pages dashboard / JSON POST client
                  |
                  v
          Review Webhook (POST)
                  |
                  v
            Validate Input
                  |
       +----------+-----------+
       |          |           |
       v          v           v
 Agent 1       Agent 2      Agent 3
  Bugs         Security      Tests
       |          |           |
       +----------+-----------+
                  |
                  v
       Merge Agent Findings
           (3 inputs)
                  |
                  v
       Orchestrator — Prioritize
                  |
                  v
         Return Review JSON
                  |
                  v
     Dashboard findings and JSON export
```

The export connects **Review Webhook → Validate Input → three agents → Merge Agent Findings → Orchestrator — Prioritize → Return Review JSON**. The Merge node has three inputs and combines agent results for the orchestrator.

### 4.1 Node inventory

| # | n8n node | Responsibility |
|---|---|---|
| 1 | Review Webhook | Accepts POST requests on `multi-agent-code-review`; uses response node |
| 2 | Validate Input | Checks `sample_id` and `code` as non-empty strings; rejects code over 200,000 characters; forwards `tests` |
| 3 | Agent 1 — Bugs | Detects selected bug patterns and adds severity, line, and recommendation |
| 4 | Agent 2 — Security | Detects selected risky coding patterns |
| 5 | Agent 3 — Tests | Identifies missing tests and rule-specific test scenarios |
| 6 | Merge Agent Findings | Combines the three branches |
| 7 | Orchestrator — Prioritize | Collects findings, deduplicates, sorts, counts severities, sets status |
| 8 | Return Review JSON | Returns HTTP 200 with the JSON review report |

### 4.2 Input contract

The webhook accepts a JSON object of this form:

```json
{
  "sample_id": "billing_calculations",
  "code": "def example():\n    pass",
  "tests": ""
}
```

`sample_id` and `code` must be non-empty strings. The exported validation code limits `code` to 200,000 characters. `tests` is optional. This is a lightweight demonstration validator; it does not implement a full authentication, payload-size, or request-rate policy.

### 4.3 Output contract

The orchestrator produces:
- `sample_id`: source sample identifier.
- `status`: `CHANGES_REQUIRED` if Critical or High findings exist, otherwise `REVIEW_COMPLETE`.
- `summary`: `critical`, `high`, `medium`, `low`, `total`.
- `findings`: severity-prioritized array of findings.
- `debug`: received item count and finding counts before/after deduplication.

Each finding generally includes `agent`, `rule`, `severity`, `title`, `recommendation`, and, where available, `line`. The status is a severity policy, **not** proof that code without High/Critical findings is safe.

## 5. Agent design and implementation

### 5.1 Agent 1 — Bug Analysis

The exported JavaScript rules detect:
- **BUG-MUTABLE-DEFAULT (High):** mutable default arguments in selected Python function definitions.
- **BUG-DIVZERO (Medium):** simple return expressions that may divide by zero.
- **BUG-BARE-EXCEPT (Medium):** bare `except:` clauses.
- **BUG-CONNECTION (Low):** selected SQLite connection creation patterns that warrant lifecycle review.

The agent reports source line numbers for matching lines. These regex checks can produce false positives or miss equivalent patterns written differently.

### 5.2 Agent 2 — Security Analysis

The exported rules detect:
- **SEC-SQL-INJECTION (Critical):** selected dynamically assembled SQL or risky execute calls.
- **SEC-SHELL (High):** shell execution patterns such as `shell=True` or `os.system`.
- **SEC-PICKLE (High):** `pickle.load` / `pickle.loads` patterns.
- **SEC-EVAL (Critical):** dynamic evaluation through `eval` or `exec`.
- **SEC-HARDCODED-SECRET (High):** selected credential-like assignments.

The rule names describe potential issues requiring human validation; a regex match alone is not a complete exploitability determination.

### 5.3 Agent 3 — Test Coverage

The exported rules flag:
- **TEST-NONE:** no test text supplied.
- **TEST-MUTABLE:** missing mutable-default regression scenario.
- **TEST-ZERO:** missing zero-divisor scenario.
- **TEST-SQL:** missing SQL input safety scenario.
- **TEST-SECURITY:** missing dangerous-input regression scenario.

These are **test-gap recommendations**, not a measurement of code coverage or proof that an existing test suite lacks those tests. The current implementation does not parse or run tests to establish actual coverage.

### 5.4 Orchestrator

The orchestrator gathers arrays under keys such as `bug_findings`, `security_findings`, `test_findings`, and `findings`. It deduplicates using rule ID plus line number where available, sorts by **Critical > High > Medium > Low**, and computes counts. This ensures that more urgent items appear first in the returned report.

## 6. Browser UI and deployment

The GitHub Pages dashboard supports:
- Selecting one of three provided Python samples.
- Viewing and editing the code and optional test text.
- Switching between static demo reports and live webhook requests.
- Viewing counts, prioritized findings, agent labels, rule IDs, and recommendations.
- Filtering by severity.
- Exporting the displayed report as JSON.

**Dashboard URL:** https://rrama2.github.io/ai-code/gen-ai-project-3/ui/  
**Production webhook:** `https://rrama2.app.n8n.cloud/webhook/multi-agent-code-review`

For live use, the dashboard's **Use demo reports** option must be unchecked and the production endpoint selected. GitHub Pages hosts static files and cannot securely conceal API keys or run a private backend.

### 6.1 Browser connectivity and CORS

During testing, the dashboard displayed **“Review failed: Failed to fetch”**. The user later reported that the dashboard worked again. A subsequent n8n workflow export confirmed that the Webhook node's **Allowed Origins** value was corrected to:

```text
https://rrama2.github.io
```

An earlier export contained the malformed value `*https://rrama2.github.io`. The corrected export is preserved in GitHub. Although this is a plausible explanation for the connectivity improvement, the conversation does not include a captured browser Network trace proving the exact failure mode.

Browser requests with `Content-Type: application/json` may trigger an OPTIONS preflight. A deployment must return appropriate CORS headers and support the preflight, or route requests through an authorized server-side proxy. **Do not use `no-cors` mode** because the dashboard would not be able to read the JSON response.

### 6.2 Security considerations

The webhook URL is visible in browser-side JavaScript. A public endpoint should be protected against abuse with suitable authentication, request limits, and monitoring. A server-side proxy is preferable if credentials are required. Do not put secrets in the static UI or submit confidential code to an endpoint that has not been approved for that data.

## 7. Testing methodology

Three intentionally flawed Python samples were submitted through the project workflow and later viewed in the dashboard:

1. **User Service:** SQLite query construction and missing SQL safety tests.
2. **Backup Utility:** dynamic evaluation, shell execution, deserialization, and missing security tests.
3. **Billing Calculations:** mutable default argument, potential zero division, and missing regression tests.

The repository retains original and improved n8n response snapshots as well as a separate UI test report. The dashboard findings were supplied by the user; not every dashboard run was independently established to have Demo mode disabled.

### 7.1 Latest dashboard-observed findings

| Sample | Critical | High | Medium | Low | Total |
|---|---:|---:|---:|---:|---:|
| User Service | 1 | 0 | 2 | 1 | 4 |
| Backup Utility | 1 | 2 | 2 | 0 | 5 |
| Billing Calculations | 0 | 1 | 4 | 0 | 5 |
| **Total** | **2** | **3** | **8** | **1** | **14** |

The 14 findings include 2 Critical (14.3%), 3 High (21.4%), 8 Medium (57.1%), and 1 Low (7.1%). These percentages describe the **reported findings**, not defect detection accuracy.

### 7.2 Detailed results

**User Service — 4 findings**
- Critical: Potential SQL injection — Security Analysis, line 5.
- Medium: No tests provided — Test Coverage.
- Medium: Missing SQL input safety test — Test Coverage.
- Low: Database connection lifecycle — Bug Analysis, line 4.

**Backup Utility — 5 findings**
- Critical: Dynamic evaluation of input — Security Analysis, line 11.
- High: Shell command execution — Security Analysis, line 5.
- High: Unsafe deserialization risk — Security Analysis, line 8.
- Medium: No tests provided — Test Coverage.
- Medium: Missing dangerous-input regression tests — Test Coverage.

**Billing Calculations — 5 findings**
- High: Mutable default argument — Bug Analysis, line 1.
- Medium: Potential division by zero — Bug Analysis, line 8.
- Medium: No tests provided — Test Coverage.
- Medium: Missing mutable-default regression test — Test Coverage.
- Medium: Missing zero-divisor test — Test Coverage.

All three dashboard summaries showed `CHANGES_REQUIRED`, consistent with the orchestrator's High/Critical severity policy.

### 7.3 Reconciliation with earlier verification

The earlier improved n8n webhook response set documented **13 findings** (2 Critical, 3 High, 8 Medium). The later dashboard-observed results documented **14 findings**, adding the Low-severity database connection lifecycle finding in User Service. This difference is preserved explicitly rather than silently treating the two result sets as identical.

See:
- [Improved n8n verification report](improved_verified_findings.md)
- [UI end-to-end testing report](ui_end_to_end_testing.md)

### 7.4 What has and has not been verified

**Supported by artifacts and user observations:** workflow structure, exported JavaScript rules, sample inputs, previous successful n8n webhook responses, dashboard-displayed findings, and the corrected CORS origin in the latest export.

**Not established by these artifacts:** systematic false-positive/false-negative rates, full code coverage, production authentication, stress testing, reliable browser Live-mode evidence for every sample, or independent vulnerability exploitation tests.

## 8. Troubleshooting and resolutions

| Issue | Observed symptom | Action or outcome |
|---|---|---|
| Test webhook registration | Test URL returned 404 until a test execution was started | Use n8n Test workflow / Execute Workflow for the temporary test URL |
| Production webhook activation | Production URL initially returned webhook-not-registered | Publish/activate the workflow; later POST returned HTTP 200 |
| Agent aggregation | Earlier merges omitted agent findings | Configure Merge to append all three inputs; orchestrator collects all finding arrays |
| Finding prioritization | Need one consolidated report | Deduplicate, sort by severity, and compute summary in Orchestrator |
| Browser-to-n8n request | UI showed `Failed to fetch` | Inspect CORS/preflight; user reported restored connectivity; latest export uses exact GitHub Pages origin |
| Evidence consistency | Earlier reports had 13 findings; later UI had 14 | Document the additional Low finding and keep both verification stages |

## 9. Deliverables and repository layout

```text
gen-ai-project-3/
├── README.md
├── workflow/
│   ├── original-export.json
│   ├── multi-agent-code-review-improved.json
│   └── latest-published-export.json
├── scripts/
│   ├── agent_bugs.js
│   ├── agent_security.js
│   ├── agent_tests.js
│   └── orchestrator.js
├── samples/
│   ├── code-review.1.json
│   ├── code-review.2.json
│   └── code-review.3.json
├── reports/
│   ├── original-verified-review*.json
│   ├── improved-verified-review*.json
│   ├── improved_verified_findings.md
│   ├── ui_end_to_end_testing.md
│   └── FINAL_PROJECT_REPORT.md
└── ui/
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── README.md
    └── demo/
```

The repository includes workflow exports and separate JavaScript source snapshots. The **latest n8n export is the authoritative snapshot of the supplied live workflow configuration**; standalone script files may reflect an earlier revision unless compared and updated.

## 10. Limitations

- **Heuristic matching:** regex patterns cannot reliably model all Python syntax, data flow, or exploitability.
- **False positives and false negatives:** rule matches are indicators requiring human review.
- **Test coverage:** the Test Coverage agent suggests missing cases but does not execute tests or calculate coverage percentages.
- **Input constraints:** source size is limited, but full API abuse protection is not implemented in the export.
- **Security:** static browser clients cannot keep credentials secret; production access controls are outside the demonstrated implementation.
- **Workflow deployment:** updating GitHub files does not automatically deploy or publish changes in n8n.
- **No automatic PR integration:** GitHub repository storage is implemented; posting review comments to pull requests is not demonstrated.
- **Limited evaluation:** only three deliberately constructed samples are documented, not a broad benchmark dataset.

## 11. Future enhancements

1. Replace or complement regex rules with Python AST parsing and context-aware analysis.
2. Add automated tests for the review rules, including benign and adversarial cases.
3. Add authenticated access, rate limits, request auditing, and secret management for production use.
4. Add robust error responses and input schema validation.
5. Integrate with GitHub pull requests and CI pipelines using scoped permissions.
6. Measure detection precision/recall against a labeled dataset.
7. Add configurable rule packs, suppressions, and richer source-location references.
8. Version the published n8n workflow and UI together through a controlled release process.

## 12. Conclusion

The project demonstrates a working pattern for parallel, specialized code review in n8n, with a browser dashboard and a consolidated severity-ranked JSON response. Across three user-reported dashboard sample results, it surfaced 14 findings covering bugs, security concerns, and recommended tests. The exported workflow and project artifacts provide a reproducible foundation for further development, while the limitations above distinguish the demonstration from a production-grade security review service.

## 13. References and project links

- [Project repository](https://github.com/rrama2/ai-code/tree/main/gen-ai-project-3)
- [Live dashboard](https://rrama2.github.io/ai-code/gen-ai-project-3/ui/)
- [Latest exported workflow](../workflow/latest-published-export.json)
- [UI testing report](ui_end_to_end_testing.md)
- [Improved n8n verification report](improved_verified_findings.md)
- [UI deployment notes](../ui/README.md)

*Prepared from the user-provided n8n workflow export, existing GitHub project artifacts, and user-reported test results. Claims about live browser connectivity are qualified where direct evidence was unavailable.*
