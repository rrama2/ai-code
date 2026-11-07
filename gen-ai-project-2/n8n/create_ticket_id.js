// n8n Code node. A generated ID is not a transactional uniqueness guarantee.
const data = $input.first().json;
const ticketId = 'SUP-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
return [{json:{...data, ticket_id:ticketId, created_at:new Date().toISOString(), ticket_status:'Open'}}];