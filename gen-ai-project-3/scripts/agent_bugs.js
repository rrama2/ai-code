const data=$input.first().json,code=data.code??"",findings=[];
code.split("\n").forEach((s,i)=>{
if(/def\s+\w+\([^)]*=\s*\[\]/.test(s))findings.push({agent:"Bug Analysis",severity:"HIGH",line:i+1,title:"Mutable default argument",recommendation:"Use None as the default."});
if(/return\s+total\s*\/\s*count/.test(s))findings.push({agent:"Bug Analysis",severity:"MEDIUM",line:i+1,title:"Potential division by zero",recommendation:"Check count before division."});
});
return [{json:{sample_id:data.sample_id,bug_findings:findings}}];