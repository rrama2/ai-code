const data=$input.first().json,code=data.code??"",findings=[];
function add(title,recommendation){findings.push({agent:"Test Coverage",severity:"MEDIUM",title,recommendation});}
if(!String(data.tests??"").trim())add("No tests provided","Add unit tests.");
if(/=\s*\[\]/.test(code))add("Missing mutable-default test","Test repeated calls.");
if(/return\s+total\s*\/\s*count/.test(code))add("Missing zero-divisor test","Test count=0.");
if(/\bSELECT\b/i.test(code))add("Missing SQL input tests","Test parameter handling and invalid inputs.");
if(/\bpickle\.loads?\s*\(/.test(code))add("Missing deserialization tests","Test rejection of untrusted data.");
return [{json:{sample_id:data.sample_id,test_findings:findings}}];