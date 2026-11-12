const $=id=>document.getElementById(id);
let token=localStorage.getItem('ghost_token')||'',authMode='login',allBots=[],allContacts=[];
const api=async(path,options={})=>{
  const headers={'Content-Type':'application/json',...(options.headers||{})};
  if(token)headers.Authorization='Bearer '+token;
  let response;
  try{response=await fetch('/api'+path,{...options,headers})}catch(e){throw new Error('No se pudo conectar con el servidor. Revisa tu conexión.')}
  let data={};try{data=await response.json()}catch{}
  if(!response.ok){if(response.status===401&&token){logout(false)}throw new Error(data.detail||'Ocurrió un error.')}
  return data;
};
function toast(message,type='ok'){const el=document.createElement('div');el.className='toast '+(type==='error'?'error':'');el.textContent=message;$('toastHost').append(el);setTimeout(()=>el.remove(),3500)}
function setAuthMode(mode){authMode=mode;const register=mode==='register';$('authTitle').textContent=register?'Crear tu cuenta':'Bienvenido de nuevo';$('authDescription').textContent=register?'Configura tu acceso al centro de control.':'Entra a tu centro de control y administra tus automatizaciones.';$('authSubmit').innerHTML=register?'Crear cuenta <span>→</span>':'Iniciar sesión <span>→</span>';$('switchText').textContent=register?'¿Ya tienes una cuenta?':'¿Todavía no tienes una cuenta?';$('switchAuth').textContent=register?'Iniciar sesión':'Crear cuenta';$('authPassword').autocomplete=register?'new-password':'current-password';$('authAlert').textContent=''}
$('switchAuth').addEventListener('click',()=>setAuthMode(authMode==='login'?'register':'login'));
$('togglePassword').addEventListener('click',()=>{$('authPassword').type=$('authPassword').type==='password'?'text':'password'});
$('authForm').addEventListener('submit',async e=>{e.preventDefault();const username=$('authUsername').value.trim(),password=$('authPassword').value;if(username.length<3||password.length<8){$('authAlert').textContent='Usa un usuario de al menos 3 caracteres y una contraseña de 8 o más.';return}const submit=$('authSubmit');submit.disabled=true;submit.textContent='Conectando...';$('authAlert').textContent='';try{const data=await api('/auth/'+authMode,{method:'POST',body:JSON.stringify({username,password})});token=data.token;localStorage.setItem('ghost_token',token);toast(authMode==='register'?'Cuenta creada correctamente.':'Sesión iniciada.');await boot()}catch(err){$('authAlert').textContent=err.message}finally{submit.disabled=false;submit.innerHTML=authMode==='register'?'Crear cuenta <span>→</span>':'Iniciar sesión <span>→</span>'}});
async function boot(){try{const me=await api('/me');$('authScreen').classList.add('hidden');$('dashboard').classList.remove('hidden');$('userName').textContent=me.username;$('userAvatar').textContent=me.username[0].toUpperCase();$('topAvatar').textContent=me.username[0].toUpperCase();$('todayDate').textContent=new Intl.DateTimeFormat('es-MX',{weekday:'long',day:'2-digit',month:'long'}).format(new Date()).toUpperCase();applySavedPrefs();await refreshAll()}catch(e){token='';localStorage.removeItem('ghost_token');$('dashboard').classList.add('hidden');$('authScreen').classList.remove('hidden')}}
function logout(show=true){token='';localStorage.removeItem('ghost_token');$('dashboard').classList.add('hidden');$('authScreen').classList.remove('hidden');if(show)toast('Sesión cerrada.')}
$('logoutBtn').addEventListener('click',()=>logout());
async function refreshAll(){try{const s=await api('/stats');$('statBots').textContent=s.bots;$('statContacts').textContent=s.contacts;$('statMessages').textContent=s.messages;await loadBots();await loadContacts();await loadMessages();await checkWhatsApp()}catch(e){toast(e.message,'error')}}
$('refreshBtn').addEventListener('click',()=>refreshAll().then(()=>toast('Panel actualizado.')));
function navigate(view){document.querySelectorAll('.page-view').forEach(x=>x.classList.add('hidden'));const target=$('view-'+view);if(target)target.classList.remove('hidden');document.querySelectorAll('.nav-item').forEach(x=>x.classList.toggle('active',x.dataset.view===view));const labels={overview:'Resumen',bots:'Mis bots',contacts:'Contactos',messages:'Mensajes',assistant:'Asistente',integrations:'Integraciones',settings:'Personalización'};$('pageName').textContent=labels[view]||view;if(view==='messages')loadMessages();if(view==='contacts')loadContacts();if(view==='bots')loadBots()}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.view)));
document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.go)));
$('mobileMenu').addEventListener('click',()=>$('sidebar').classList.toggle('mobile-open'));
$('newBotBtn').addEventListener('click',()=>{$('botForm').reset();$('botId').value='';$('botFormTitle').textContent='Crear bot';$('botFormPanel').classList.remove('hidden')});
['closeBotForm','cancelBot'].forEach(id=>$(id).addEventListener('click',()=>$('botFormPanel').classList.add('hidden')));
$('botForm').addEventListener('submit',async e=>{e.preventDefault();const id=$('botId').value,body=JSON.stringify({name:$('botName').value.trim(),description:$('botDescription').value.trim()});try{await api('/bots'+(id?'/'+id:''),{method:id?'PATCH':'POST',body});$('botFormPanel').classList.add('hidden');toast(id?'Bot actualizado.':'Bot creado.');await loadBots();await refreshStats()}catch(err){toast(err.message,'error')}});
async function loadBots(){allBots=await api('/bots');renderBots()}
function renderBots(){const q=($('botSearch').value||'').toLowerCase();const rows=allBots.filter(b=>(b.name+' '+b.description).toLowerCase().includes(q));$('botCount').textContent=rows.length+' perfiles';$('botGrid').innerHTML=rows.map(b=>`<article class="bot-card"><div class="bot-card-top"><span class="bot-symbol">◈</span><span class="state-badge">${escapeHtml(b.status)}</span></div><h3>${escapeHtml(b.name)}</h3><p>${escapeHtml(b.description||'Sin descripción todavía.')}</p><div class="bot-actions"><button class="small-btn" data-edit="${b.id}">Editar</button><button class="small-btn" data-delete="${b.id}">Eliminar</button></div></article>`).join('')||'<div class="panel empty-state">No hay bots que mostrar. Crea tu primer perfil.</div>';document.querySelectorAll('[data-edit]').forEach(b=>b.addEventListener('click',()=>{const bot=allBots.find(x=>x.id==b.dataset.edit);$('botId').value=bot.id;$('botName').value=bot.name;$('botDescription').value=bot.description;$('botFormTitle').textContent='Editar bot';$('botFormPanel').classList.remove('hidden')}));document.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',async()=>{if(!confirm('¿Eliminar este perfil?'))return;try{await api('/bots/'+b.dataset.delete,{method:'DELETE'});toast('Bot eliminado.');await loadBots();await refreshStats()}catch(e){toast(e.message,'error')}}))}
$('botSearch').addEventListener('input',renderBots);
$('newContactBtn').addEventListener('click',()=>$('contactFormPanel').classList.remove('hidden'));
['closeContactForm','cancelContact'].forEach(id=>$(id).addEventListener('click',()=>$('contactFormPanel').classList.add('hidden')));
$('contactForm').addEventListener('submit',async e=>{e.preventDefault();try{await api('/contacts',{method:'POST',body:JSON.stringify({name:$('contactName').value.trim(),phone:$('contactPhone').value.trim().replace(/[^0-9+]/g,''),opted_in:$('contactConsent').checked,consent_source:$('contactSource').value.trim()})});$('contactForm').reset();$('contactFormPanel').classList.add('hidden');toast('Contacto guardado.');await loadContacts();await refreshStats()}catch(err){toast(err.message,'error')}});
async function loadContacts(){allContacts=await api('/contacts');renderContacts();const select=$('messageContact');const selected=select.value;select.innerHTML='<option value="">Selecciona un contacto</option>'+allContacts.map(c=>`<option value="${c.id}" ${c.id==selected?'selected':''}>${escapeHtml(c.name)} — ${escapeHtml(c.phone)}${c.opted_in?'':' (sin consentimiento)'}</option>`).join('');updateConsentHint()}
function renderContacts(){const q=($('contactSearch').value||'').toLowerCase();const rows=allContacts.filter(c=>(c.name+' '+c.phone).toLowerCase().includes(q));$('contactCount').textContent=rows.length+' contactos';$('contactRows').innerHTML=rows.map(c=>`<tr><td><b>${escapeHtml(c.name)}</b></td><td>${escapeHtml(c.phone)}</td><td><span class="consent-badge ${c.opted_in&&c.consent_source?'':'no'}">${c.opted_in&&c.consent_source?'Consentimiento registrado':'No autorizado'}</span></td><td><button class="small-btn" data-message="${c.id}">Escribir</button></td></tr>`).join('')||'<tr><td colspan="4" class="empty-state">No hay contactos registrados.</td></tr>';document.querySelectorAll('[data-message]').forEach(b=>b.addEventListener('click',()=>{navigate('messages');$('messageContact').value=b.dataset.message;updateConsentHint()}))}
$('contactSearch').addEventListener('input',renderContacts);
$('messageContact').addEventListener('change',updateConsentHint);
function updateConsentHint(){const c=allContacts.find(x=>x.id==$('messageContact').value);const valid=c&&c.opted_in&&c.consent_source;$('consentHint').textContent=!c?'Selecciona un contacto con consentimiento registrado.':valid?'Consentimiento registrado. Puedes preparar el mensaje.':'Este contacto no tiene consentimiento verificable; el envío está bloqueado.';$('consentHint').classList.toggle('warn',!!c&&!valid);$('sendMessageBtn').disabled=!!c&&!valid}
$('messageBody').addEventListener('input',()=>$('charCount').textContent=$('messageBody').value.length+' / 4096');
$('messageForm').addEventListener('submit',async e=>{e.preventDefault();const btn=$('sendMessageBtn');btn.disabled=true;btn.textContent='Enviando...';try{const result=await api('/whatsapp/send',{method:'POST',body:JSON.stringify({contact_id:$('messageContact').value,body:$('messageBody').value.trim()})});$('messageBody').value='';$('charCount').textContent='0 / 4096';toast('Mensaje enviado correctamente.');await loadMessages();await refreshStats()}catch(err){toast(err.message,'error')}finally{btn.innerHTML='Enviar mensaje <span>➤</span>';updateConsentHint()}});
async function loadMessages(){const rows=await api('/messages');$('messageHistory').innerHTML=rows.map(m=>`<article class="message-entry"><div class="message-entry-top"><b>${escapeHtml(m.contact)}</b><span>${escapeHtml(m.status)} · ${new Date(m.created_at).toLocaleString('es-MX')}</span></div><p>${escapeHtml(m.body)}</p></article>`).join('')||'<div class="empty-state">Todavía no hay mensajes registrados.</div>';const recent=rows.slice(0,4);$('recentActivity').innerHTML=recent.map(m=>`<div class="item"><div><b>${escapeHtml(m.contact)}</b><div class="muted">${escapeHtml(m.body.slice(0,90))}</div></div><span class="state-badge">${escapeHtml(m.status)}</span></div>`).join('')||'<div class="empty-state">Aún no hay actividad. Cuando registres acciones, aparecerán aquí.</div>'}
$('refreshMessages').addEventListener('click',()=>loadMessages().then(()=>toast('Historial actualizado.')));
async function refreshStats(){const s=await api('/stats');$('statBots').textContent=s.bots;$('statContacts').textContent=s.contacts;$('statMessages').textContent=s.messages}
async function checkWhatsApp(){try{const s=await api('/integrations/whatsapp/status');$('statApi').textContent=s.configured?'READY':'SETUP';$('whatsappState').textContent=s.configured?'Conectado · Credenciales detectadas':'Pendiente · Faltan variables de entorno';$('whatsappState').className='state-badge'+(s.configured?'':' no')}catch(e){$('statApi').textContent='CHECK'}}
$('checkWhatsApp').addEventListener('click',()=>checkWhatsApp().then(()=>toast('Estado de integración actualizado.')));
$('generateDraft').addEventListener('click',async()=>{try{const d=await api('/assistant/draft',{method:'POST',body:JSON.stringify({topic:$('assistantTopic').value})});$('assistantDraft').value=d.draft;toast('Borrador generado.')}catch(e){toast(e.message,'error')}});
$('copyDraft').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('assistantDraft').value);toast('Texto copiado.')}catch{toast('No se pudo copiar automáticamente.','error')}});
function applyTheme(theme){document.documentElement.dataset.theme=theme;localStorage.setItem('ghost_theme',theme);document.querySelectorAll('.theme-option').forEach(b=>b.classList.toggle('selected',b.dataset.theme===theme))}
document.querySelectorAll('.theme-option').forEach(b=>b.addEventListener('click',()=>{applyTheme(b.dataset.theme);toast('Tema aplicado.')}));$('themeQuick').addEventListener('click',()=>{const themes=['ghost','ocean','purple','sunset','light'];const current=localStorage.getItem('ghost_theme')||'ghost';applyTheme(themes[(themes.indexOf(current)+1)%themes.length]);toast('Tema cambiado.')});
function applySavedPrefs(){applyTheme(localStorage.getItem('ghost_theme')||'ghost');const prefs=JSON.parse(localStorage.getItem('ghost_prefs')||'{}');$('animationsToggle').checked=prefs.animations!==false;$('glowToggle').checked=prefs.glow!==false;$('ambientToggle').checked=prefs.ambient!==false;applyPrefs()}
function applyPrefs(){const p={animations:$('animationsToggle').checked,glow:$('glowToggle').checked,ambient:$('ambientToggle').checked};document.body.classList.toggle('no-animations',!p.animations);document.body.classList.toggle('no-glow',!p.glow);document.body.classList.toggle('no-ambient',!p.ambient);localStorage.setItem('ghost_prefs',JSON.stringify(p))}
['animationsToggle','glowToggle','ambientToggle'].forEach(id=>$(id).addEventListener('change',applyPrefs));
function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}
(async()=>{try{const s=await fetch('/api/auth/status').then(r=>r.json());if(!s.registration_enabled){$('switchAuth').classList.add('hidden');$('switchText').classList.add('hidden')}}catch{}if(token)boot()})();


/* GHOST BOTS PRO v5 — interaction layer */
(function(){
  const byId = id => document.getElementById(id);
  const safe = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  // Respect reduced-motion preferences and user toggles.
  const motionQuery = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motionQuery && motionQuery.matches) document.documentElement.classList.add('reduce-motion');
  // Add a subtle interactive pointer glow without blocking touch input.
  document.addEventListener('pointermove', e => {
    if (e.pointerType === 'touch') return;
    document.documentElement.style.setProperty('--pointer-x', (e.clientX / innerWidth * 100) + '%');
    document.documentElement.style.setProperty('--pointer-y', (e.clientY / innerHeight * 100) + '%');
  }, {passive:true});
  // Keyboard shortcuts.
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const input = document.querySelector('.page-view:not(.hidden) input:not([type=hidden])');
      if (input) input.focus();
    }
    if (e.key === 'Escape') {
      ['botFormPanel','contactFormPanel'].forEach(id => byId(id)?.classList.add('hidden'));
      byId('sidebar')?.classList.remove('mobile-open');
    }
  });
  // Theme/effect preferences are persistent per browser.
  const savePrefs = () => {
    const prefs = {animations:byId('animationsToggle')?.checked!==false,
      glow:byId('glowToggle')?.checked!==false, ambient:byId('ambientToggle')?.checked!==false};
    localStorage.setItem('ghost_prefs', JSON.stringify(prefs));
    document.documentElement.classList.toggle('no-animations', !prefs.animations);
    document.documentElement.classList.toggle('no-glow', !prefs.glow);
    document.documentElement.classList.toggle('no-ambient', !prefs.ambient);
  };
  ['animationsToggle','glowToggle','ambientToggle'].forEach(id => byId(id)?.addEventListener('change', savePrefs));
  const oldApply = window.applyPrefs;
  window.applyPrefs = function(){ if(oldApply) oldApply(); savePrefs(); };
  // Add export action to contacts toolbar.
  const contactToolbar = document.querySelector('#view-contacts .toolbar');
  if (contactToolbar && !byId('exportContacts')) {
    const btn = document.createElement('a');
    btn.id='exportContacts'; btn.className='ghost-btn export-btn';
    btn.href='/api/export/contacts'; btn.textContent='↓ Exportar CSV';
    btn.addEventListener('click', async e => {
      e.preventDefault();
      try {
        const response = await fetch('/api/export/contacts',{headers:{Authorization:'Bearer '+(localStorage.getItem('ghost_token')||'')}});
        if(!response.ok) throw new Error('No se pudo exportar la lista.');
        const blob=await response.blob(), url=URL.createObjectURL(blob), a=document.createElement('a');
        a.href=url; a.download='ghostbots-contactos.csv'; a.click(); URL.revokeObjectURL(url);
      } catch(err){ if(window.toast) toast(err.message,'error'); }
    });
    contactToolbar.append(btn);
  }
  // Status dashboard and live clock.
  const clock = document.createElement('span');
  clock.className='live-clock'; clock.id='liveClock';
  document.querySelector('.top-actions')?.prepend(clock);
  const tick=()=>{if(byId('liveClock')) byId('liveClock').textContent=new Intl.DateTimeFormat('es-MX',{hour:'2-digit',minute:'2-digit'}).format(new Date())};
  tick(); setInterval(tick,15000);
  // Add API status refresh when entering integrations.
  const oldNavigate=window.navigate;
  if(oldNavigate) window.navigate=function(view){oldNavigate(view); if(view==='integrations') refreshSystemStatus();};
  async function refreshSystemStatus(){
    try {
      const token=localStorage.getItem('ghost_token')||'';
      const r=await fetch('/api/system/status',{headers:{Authorization:'Bearer '+token}});
      const d=await r.json();
      const node=byId('whatsappState');
      if(node){node.textContent=d.whatsapp?'WhatsApp configurado':'WhatsApp pendiente de configuración';node.classList.toggle('connected',d.whatsapp);}
      const apiNode=byId('statApi'); if(apiNode) apiNode.textContent=d.api.toUpperCase();
    } catch(e) {}
  }
  // Add quick command palette button and app version footer.
  const topbar=document.querySelector('.breadcrumb');
  if(topbar && !byId('buildTag')) {const tag=document.createElement('span');tag.id='buildTag';tag.className='build-tag';tag.textContent='PRO / 5.0';topbar.append(tag);}
})();
