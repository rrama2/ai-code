Resolution Metrics — Benchmark Report
Hybrid Support Bot | 20-query synthetic evaluation | November 2026
Final results
	Metric
	Formula
	Measured result

	Automated-resolution proxy
	Correct automated answers / all queries
	12/20 = 60%

	Escalation rate
	Escalated queries / all queries
	8/20 = 40%

	Answer-accuracy proxy
	Correct source-ID + nonempty-answer matches / automated answers
	12/12 = 100%

	Correct escalation coverage
	Correctly escalated designated requests / designated requests
	8/8 = 100%

	Workflow error rate
	Errors / all queries
	0/20 = 0%


Baseline vs final
	Outcome
	Baseline
	Final
	Change

	Automated answer matches
	6
	12
	+6

	Correct escalations
	8
	8
	0

	Extra escalations of paraphrases
	6
	0
	−6

	Automated-resolution proxy
	30%
	60%
	+30 percentage points

	Escalation rate
	70%
	40%
	−30 percentage points

	Workflow errors
	0
	0
	No change


Benchmark composition
Tests 1–6: exact knowledge-base matches; tests 7–12: paraphrased equivalents; tests 13–20: requests designated for human review (refund, data deletion, restoration, rate limit, duplicate charge, compromised account, cancellation, application crash).
What “correct” means here
The benchmark script marked an automated response as correct when status=answered, source.id matched the expected document ID, and answer was nonempty. It marked an escalation correct when status=escalated and a ticket ID was present. The script did not independently judge factual correctness of every answer, customer satisfaction, or follow-up contact. Therefore, 60% is an automated-resolution proxy, not verified first-contact resolution (FCR).
True FCR measurement recommendation
For production FCR, track the percentage of customer contacts resolved without subsequent contact for the same issue within a defined window (for example 7 days), using ticket outcomes and customer feedback. Report the window, denominator, channel, and exclusions. Track false answers and missed escalations separately.
Source and reproducibility
Metrics were supplied from the user’s final PowerShell benchmark summary: 20 total, 12 correct answer matches, 8 correct escalations, 8 total escalations, 0 errors. A previous benchmark CSV was reviewed during debugging, but the final CSV was not provided in this conversation. Include the final CSV in GitHub after reviewing it for customer data.