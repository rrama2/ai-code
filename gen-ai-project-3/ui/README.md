# Multi-Agent Code Review UI

Static HTML/CSS/JavaScript dashboard for the n8n workflow. No build tools needed.

## GitHub Pages

In the repository Settings → Pages, select Deploy from branch, main, root. Then open:
https://rrama2.github.io/ai-code/gen-ai-project-3/ui/

The UI supports three sample code inputs, demo findings from saved prior results, severity filtering, JSON export, and live POST to an n8n webhook.

## Live mode

1. Activate an appropriately secured n8n workflow and copy its **Production URL**.
2. Turn off **Use demo reports**.
3. Paste the HTTPS webhook URL and click **Use endpoint**.
4. Run a review.

**Important:** Browser POST requires the webhook (or a server-side proxy) to support CORS for the GitHub Pages origin. A static GitHub Pages site cannot hide webhook URLs or credentials. Do not put API tokens in this UI. For a production deployment, put authentication, rate limits, and CORS handling in a server-side proxy and configure its HTTPS URL in the UI. Do not submit proprietary code to an untrusted endpoint.

Demo reports are static snapshots and do not analyze edits or custom code. No Python code is executed by the UI.
