const items=$input.all(),all=[];
for(const {json:d} of items)for(const key of ["bug_findings","security_findings","test_findings","findings"])if(Array.isArray(d[key]))all.push(...d[key]);
const rank={CRITICAL:4,HIGH:3,MEDIUM:2,LOW:1},seen=new Set();
const findings=all.map(f=>({...f,severity:String(f.severity??"LOW").toUpperCase()})).filter(f=>{const k=[f.agent,f.rule??f.title,f.line??""].join("|");if(seen.has(k))return false;seen.add(k);return true;}).sort((a,b)=>(rank[b.severity]??0)-(rank[a.severity]??0));
const summary={critical:0,high:0,medium:0,low:0,total:findings.length};
for(const f of findings)if(f.severity.toLowerCase() in summary)summary[f.severity.toLowerCase()]++;
return [{json:{sample_id:items[0]?.json.sample_id??"unknown",status:summary.critical||summary.high?"CHANGES_REQUIRED":"REVIEW_COMPLETE",summary,findings,debug:{received_items:items.length,findings_collected:findings.length}}}];