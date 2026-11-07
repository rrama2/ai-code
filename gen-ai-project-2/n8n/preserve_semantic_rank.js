// n8n Code node: Run Once for All Items, between Semantic Search and Merge Input 2.
return $input.all().map((item, index) => ({
  json: {...item.json, semantic_rank: index + 1}
}));