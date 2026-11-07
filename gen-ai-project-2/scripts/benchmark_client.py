"""Optional Python benchmark client. NOT used to implement the original n8n bot.
Requires: pip install requests
Use only against a test instance or dedicated test-ticket queue.
"""
import csv
import os
import time
from pathlib import Path
import requests

URL = os.getenv('SUPPORT_WEBHOOK_URL', 'https://rrama2.app.n8n.cloud/webhook/hybrid-support')
TESTS = [
 ('How do I reset my password?', 'FAQ001'),
 ('How do I enable two-factor authentication?', 'FAQ002'),
 ('How do I update my billing information?', 'FAQ003'),
 ('How do I create an API key?', 'MAN001'),
 ('How do I export my data?', 'MAN002'),
 ('Why am I not receiving password reset emails?', 'TKT001'),
 ('I forgot my login credentials. How can I access my account?', 'FAQ001'),
 ('How do I turn on 2FA?', 'FAQ002'),
 ('Where can I change my payment details?', 'FAQ003'),
 ('Where do I generate a developer API token?', 'MAN001'),
 ('Can I download my account data?', 'MAN002'),
 ('My password reset email never arrived.', 'TKT001'),
 ('Please refund my last payment.', 'ESCALATE'),
 ('Delete all my personal data.', 'ESCALATE'),
 ('Please restore my deleted workspace.', 'ESCALATE'),
 ('Increase my API rate limit.', 'ESCALATE'),
 ('I was charged twice for my subscription.', 'ESCALATE'),
 ('My account has been compromised.', 'ESCALATE'),
 ('Cancel my subscription immediately.', 'ESCALATE'),
 ('The application crashes when I upload a large file.', 'ESCALATE'),
]

def main():
    if os.getenv('CONFIRM_TEST_TICKETS') != 'yes':
        raise SystemExit('Set CONFIRM_TEST_TICKETS=yes only after isolating or labeling test tickets.')
    rows = []
    for i, (query, expected) in enumerate(TESTS, 1):
        start = time.monotonic()
        row = {'test': i, 'query': query, 'expected': expected, 'status': 'error',
               'source_id': '', 'answer': '', 'ticket_id': '', 'error': ''}
        try:
            r = requests.post(URL, json={'query': query, 'customer_id': f'benchmark-python-{i}'}, timeout=90)
            r.raise_for_status()
            data = r.json()
            source = data.get('source') or {}
            row.update(status=data.get('status', ''), source_id=source.get('id', '') if isinstance(source, dict) else str(source),
                       answer=data.get('answer') or '', ticket_id=data.get('ticket_id') or '')
        except (requests.RequestException, ValueError) as exc:
            row['error'] = str(exc)
        row['latency_ms'] = round((time.monotonic()-start)*1000)
        row['correct_answer_proxy'] = expected != 'ESCALATE' and row['status'] == 'answered' and row['source_id'] == expected and bool(row['answer'])
        row['correct_escalation'] = expected == 'ESCALATE' and row['status'] == 'escalated' and bool(row['ticket_id'])
        rows.append(row)
        print(f"{i:02d} {row['status']:10s} {row['source_id']:7s} {row['latency_ms']} ms")
    out = Path('benchmark_results_python.csv')
    with out.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    total = len(rows)
    correct = sum(x['correct_answer_proxy'] for x in rows)
    answered = sum(x['status']=='answered' for x in rows)
    escalated = sum(x['status']=='escalated' for x in rows)
    print(f'Automated resolution proxy: {100*correct/total:.1f}%')
    print(f'Escalation rate: {100*escalated/total:.1f}%')
    print(f'Answer accuracy proxy: {100*correct/answered:.1f}%' if answered else 'Answer accuracy proxy: N/A')
    print('CSV:', out.resolve())

if __name__ == '__main__': main()