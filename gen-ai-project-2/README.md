# Hybrid Support Bot — n8n + hybrid retrieval + human escalation

## Evidence and status
The user reported a successful published n8n workflow and 20-query benchmark (12 correct answer matches, 8 correct escalations, 0 errors). This repository contains **reconstructed source snippets**, a browser UI, an optional Python benchmark client, and documentation. It does **not** contain an authenticated export of the actual published n8n workflow. Export the workflow from n8n and add it separately after reviewing it for credentials and private data.

## Project layout
- `docs/final_project_report.docx`: architecture, implementation, tests, limitations
- `docs/resolution_metrics.docx`: metric definitions, calculations, baseline vs final
- `n8n/*.js`: reconstructed n8n Code-node snippets (not an importable workflow)
- `ui/`: static HTML/CSS/JS chat UI
- `scripts/benchmark_client.py`: optional Python 20-query benchmark (not used in original implementation)
- `scripts/requirements.txt`: Python test dependency

## Endpoint
Production webhook (reported as successfully tested):
`https://rrama2.app.n8n.cloud/webhook/hybrid-support`
This is a **POST API**, not a hosted chatbot webpage. It may be inaccessible if the workflow is unpublished, disabled, or protected.

Request: `{"query":"How do I reset my password?","customer_id":"test-001"}`.
Responses include `status=answered` with `answer`/`source`, or `status=escalated` with `ticket_id`/`message`.

## Run the UI
Open `ui/index.html` through a local static server, e.g. `python -m http.server 8080` from the `ui/` folder, then visit `http://localhost:8080`.
Browser calls to n8n require appropriate CORS response headers (including preflight handling). **Do not put n8n credentials or API secrets in browser JavaScript.** For real customers, use an authenticated backend proxy with rate limits and input validation. The UI is a working frontend implementation but has not been verified against your live webhook from this environment.

## Run optional Python benchmark
`pip install -r scripts/requirements.txt`
Set `SUPPORT_WEBHOOK_URL` to your test endpoint. Ensure ticket creation is isolated or labeled, then set `CONFIRM_TEST_TICKETS=yes` and run `python scripts/benchmark_client.py`. This sends real requests and may create tickets. Python is optional and was not part of the original n8n backend.

## n8n workflow
In the n8n editor, use the workflow's menu > Download to export the actual JSON. Check for secrets before committing. Preserve the exact node name `Supprt Knowledge base` or update references accordingly. Insert and retrieval vector stores use `support-knowledge-v3`; the Simple Vector Store is temporary and not recommended for durable production storage.

## Security and limitations
Prototype only. Rule-based confidence numbers are not calibrated probabilities. Test data contains only six synthetic knowledge entries. Add authentication, authorization, data minimization, durable storage, monitoring, privacy controls, and human-reviewed evaluation before production use. Avoid collecting sensitive secrets in the chat UI.