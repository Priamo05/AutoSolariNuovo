async function api(path, opts={}){const r=await fetch('/api'+path,{headers:{'content-type':'application/json'},credentials:'include',...opts});const ct=r.headers.get('content-type')||'';const d=ct.includes('json')?await r.json():await r.text();if(!r.ok) throw new Error(d.error||d);return d}
async function register(){await api('/auth/register',{method:'POST',body:JSON.stringify({full_name:name.value,email:email.value,password:pwd.value})});alert('Registrazione ok')}
async function login(){await api('/auth/login',{method:'POST',body:JSON.stringify({email:email.value,password:pwd.value})});app.style.display='block';loadAll()}
async function logout(){await api('/auth/logout',{method:'POST'});app.style.display='none';out.textContent=''}
async function loadAll(){const d=await api('/dashboard');out.textContent=JSON.stringify(d,null,2)}
