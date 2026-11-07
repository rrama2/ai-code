Hybrid Support Bot — Final Project Report
n8n Cloud | Hybrid retrieval + confidence-based escalation | November 2026
Executive summary
A support bot was built and tested in n8n Cloud using keyword retrieval, OpenAI embedding-based semantic retrieval, reciprocal rank fusion (RRF), conservative answer rules, and a Google Sheets escalation queue. The user reported successful production-webhook tests and a 20-query synthetic benchmark with 12 correct automated answer matches, 8 correctly escalated requests, and zero workflow errors. The automated-resolution proxy increased from 30% to 60%.
Deliverables and verification
	Deliverable
	Status / evidence

	Working n8n support bot
	User-tested; production POST endpoint returned answers and ticket IDs

	Hybrid search + escalation
	Implemented in n8n JavaScript Code nodes; source snippets reconstructed in package

	20-query benchmark
	Reported 20/20 requests completed; final summary 12 answer matches, 8 escalations, 0 errors

	Resolution metrics document
	Included as resolution_metrics.docx

	Chatbot UI
	HTML/CSS/JavaScript frontend included; live browser integration not independently verified

	Python code
	Optional Python benchmark client included; original workflow did not use Python

	Full n8n workflow JSON
	Not included: requires export from n8n; do not mistake reconstructed snippets for workflow export


Architecture and data flow
POST Webhook → Support Knowledge Base (6 synthetic records) → parallel Keyword Search and Semantic Search (OpenAI embeddings + Simple Vector Store) → Preserve Semantic Rank → Merge (Append) → Hybrid Ranking (RRF, K=60, semantic tie-breaker) → Confidence Check → Needs Human? → (answer via Respond to Webhook) OR (Create Ticket ID → Google Sheets Append Row → Respond to Webhook).
Insertion pipeline: Support Knowledge Base → Prepare Documents (one question/answer text per record) → Default Data Loader (JSON, Load Specific Data, text field and id/source/question metadata) → Simple Vector Store (memory key support-knowledge-v3). The same key is configured for semantic retrieval.
Knowledge-base coverage
	Document ID
	Topic

	FAQ001
	Password reset

	FAQ002
	Two-factor authentication

	FAQ003
	Billing information update

	MAN001
	API-key creation

	MAN002
	Account data export

	TKT001
	Password-reset email not received


Ranking and confidence logic
Keyword matches and semantic matches contribute reciprocal-rank terms 1/(60+rank). Semantic ranks are attached before Merge so the rank survives item reordering; semantic rank is used to break RRF ties. The top-ranked document is evaluated for answer evidence. Exact FAQ matches, sufficiently strong dual-method matches, and six narrowly scoped paraphrase rules can produce answers; other requests are escalated. Confidence labels such as 0.8 are rule outputs, not calibrated likelihoods.
Sensitive request detection and narrow exclusion rules are prototype safeguards, not comprehensive authorization or abuse controls. An authenticated human review path is needed for financial disputes, account actions, and secrets.
Benchmark design and results
Twenty synthetic questions: six exact knowledge-base matches, six semantically equivalent paraphrases, and eight requests designated for human review. The benchmark script considered an automated answer correct when the response status was answered, the expected source ID matched, and the answer was nonempty. This proxy was supplemented by manual spot checks during iterative development; it is not a comprehensive factuality assessment.
	Metric
	Initial
	Final

	Correct automated answers
	6/20
	12/20

	Correct escalations
	8/8
	8/8

	Automated-resolution proxy
	30%
	60%

	Escalation rate
	70%
	40%

	Answer-accuracy proxy
	100%
	100%

	Workflow errors
	0
	0


Implementation and debugging history
Key fixes: (1) preserved query and customer ID across Merge/Hybrid Ranking; (2) corrected extraction of semantic documents nested under document or at top level; (3) changed Default Data Loader to Load Specific Data to prevent fragment indexing; (4) reindexed six documents under support-knowledge-v3; (5) added Preserve Semantic Rank before Merge; (6) added RRF semantic-rank tie-breaker; (7) introduced narrow paraphrase recognition for six topics; (8) regression-tested refund, disputed-charge, API-secret, unsupported-question, and 2FA security scenarios.
Published endpoint and UI
Production POST webhook: https://rrama2.app.n8n.cloud/webhook/hybrid-support. This is an API endpoint, not a chatbot page. It was reported working in PowerShell. The included browser UI submits {query, customer_id} and renders answered or escalated responses. Browser CORS support, authentication, rate limiting, and actual UI deployment remain to be configured and verified.
GitHub source-code inventory
n8n/hybrid_ranking.js, n8n/preserve_semantic_rank.js, n8n/confidence_check.js, n8n/create_ticket_id.js: reconstructed JavaScript snippets based on the conversation. scripts/benchmark_client.py: optional newly created Python test utility; not code originally used in n8n. ui/index.html, ui/styles.css, ui/config.js, ui/app.js: newly created static chatbot UI. The authoritative n8n JSON export must be downloaded from n8n and reviewed before committing.
Limitations and production-readiness checklist
The six-document synthetic knowledge base is too small to establish real-world quality.
Observed first-contact resolution requires customer confirmation or no repeat contact; the 60% metric is only an automated-resolution proxy.
Simple Vector Store is temporary; use durable vector storage with versioning and repeatable ingestion.
Protect the production webhook using authentication, authorization, request validation, rate limiting, and audit logging.
Use a server-side proxy for a browser UI; never place credentials in client-side JavaScript.
Separate test tickets from real tickets and minimize customer data stored in Google Sheets.
Add broader evaluation, adversarial tests, human review, and monitoring before production launch.