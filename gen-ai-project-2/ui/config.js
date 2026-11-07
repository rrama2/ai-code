// For local demo only. Do not embed API keys or authentication secrets in browser code.
// Direct browser calls require CORS on the n8n webhook; production should use an authenticated proxy.
window.SUPPORT_CONFIG = {
  endpoint: 'https://rrama2.app.n8n.cloud/webhook/hybrid-support',
  timeoutMs: 30000
};