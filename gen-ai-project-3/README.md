# Multi-Agent Code Review — n8n

Three parallel JavaScript agents review Python source for bugs, security patterns, and missing tests. An Append Merge feeds a severity-ranking Orchestrator and Respond to Webhook.

## Contents

- `workflow/original-export.json` — original n8n export
- `workflow/multi-agent-code-review-improved.json` — updated detection rules; not yet verified in n8n Cloud
- `scripts/` — agent and orchestrator source
- `samples/` — three JSON POST inputs containing intentionally flawed Python as text
- `reports/` — three verified original responses and consolidated findings

## Run

Import the improved JSON into n8n **as a new workflow**. Open its Webhook and click **Test workflow**. Ensure its webhook path does not conflict with an existing workflow. POST each sample using PowerShell (single line):

`curl.exe -X POST "YOUR_TEST_WEBHOOK_URL" -H "Content-Type: application/json" --data-binary "@code-review.1.json"`

Inspect Orchestrator → Output → JSON, and repeat for samples 2 and 3. Export new results for verification.

## Limitations

Regex heuristics, not a full AST/LLM security scanner; no measured line coverage, no live GitHub PR integration. Do not execute the intentionally flawed Python code.
