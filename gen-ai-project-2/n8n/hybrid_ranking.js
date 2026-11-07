// Reconstructed from user-supplied n8n code and subsequent changes.
// n8n Code node: Run Once for All Items.
const items = $input.all().map(item => item.json);
const keywordItem = items.find(x => Array.isArray(x.keyword_results));
const keywordResults = keywordItem?.keyword_results || [];
const semanticResults = items
  .filter(x => x.pageContent || x.document?.pageContent)
  .map(x => ({document: x.document || x, semantic_rank: Number(x.semantic_rank)}))
  .sort((a, b) => a.semantic_rank - b.semantic_rank);
const ranked = new Map();
const K = 60;
function add(doc, rank, type) {
  const id = String(doc.metadata?.id || doc.id || '').trim();
  if (!id) return;
  if (!ranked.has(id)) ranked.set(id, {
    id, question: doc.question || doc.metadata?.question || '',
    answer: doc.answer || '', source: doc.source || doc.metadata?.source || '',
    pageContent: doc.pageContent || '', keyword_score: 0, rrf_score: 0, matched_by: []
  });
  const entry = ranked.get(id);
  entry.rrf_score += 1 / (K + rank + 1);
  if (!entry.matched_by.includes(type)) entry.matched_by.push(type);
  if (type === 'keyword') entry.keyword_score = doc.keyword_score || 0;
  if (!entry.answer && doc.answer) entry.answer = doc.answer;
  if (!entry.answer && doc.pageContent) {
    const match = doc.pageContent.match(/Answer:\s*([\s\S]*)/i);
    if (match) entry.answer = match[1].trim();
  }
  if (!entry.pageContent && doc.pageContent) entry.pageContent = doc.pageContent;
}
keywordResults.forEach((doc, i) => { if (doc.keyword_score > 0) add(doc, i, 'keyword'); });
semanticResults.forEach((item, i) => add(item.document, i, 'semantic'));
const semanticRankById = new Map();
semanticResults.forEach((item, i) => {
  const doc = item.document;
  const id = String(doc.metadata?.id || doc.id || '').trim();
  if (id && !semanticRankById.has(id)) semanticRankById.set(id, i + 1);
});
const results = [...ranked.values()].sort((a, b) => {
  const diff = b.rrf_score - a.rrf_score;
  if (Math.abs(diff) > 1e-10) return diff;
  return (semanticRankById.get(a.id) ?? Infinity) - (semanticRankById.get(b.id) ?? Infinity);
}).slice(0, 5);
const original = $('Supprt Knowledge base').first().json;
return [{json:{query:original.query || keywordItem?.query || '', customer_id:original.customer_id || keywordItem?.customer_id || 'anonymous', hybrid_results:results}}];