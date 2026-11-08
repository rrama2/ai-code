const data=$input.first().json,code=data.code??data.body?.code??"",findings=[];
function add(rule,severity,line,title,recommendation){findings.push({agent:"security",rule,severity,line,title,recommendation});}
code.split("\n").forEach((s,i)=>{
const line=i+1;
if(/\b(SELECT|UPDATE|INSERT|DELETE)\b/i.test(s)&&(/(\+|f["']|\.format\()/.test(s)))add("SEC-SQL-INJECTION","CRITICAL",line,"Potential SQL injection","Use parameterized queries.");
if(/shell\s*=\s*True|\bos\.system\s*\(/.test(s))add("SEC-SHELL","HIGH",line,"Shell command execution","Use shell=False with argument arrays.");
if(/\bpickle\.loads?\s*\(/.test(s))add("SEC-PICKLE","HIGH",line,"Unsafe deserialization","Do not deserialize untrusted pickle data.");
if(/\b(eval|exec)\s*\(/.test(s))add("SEC-EVAL","CRITICAL",line,"Dynamic evaluation of input","Avoid eval/exec on untrusted data.");
});
return [{json:{sample_id:data.sample_id,agent:"security",findings:[...new Map(findings.map(f=>[f.rule+":"+f.line,f])).values()]}}];