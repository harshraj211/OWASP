const crypto = require('crypto');
const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT || 6003);
const FLAG = process.env.FLAG || `FLAG{${crypto.randomUUID()}}`;
const member = { email: 'jamie.lee@asterion.local', password: 'AsterionMember!42', name: 'Jamie Lee', memberId: `MBR-${crypto.randomInt(100, 999)}` };
const internalNotice = { metadata: { source: 'people-operations', retention: 'restricted' }, payload: { classification: 'CONFIDENTIAL', message: 'Board-approved Q4 benefits restructuring memo.', reference: `ASTERION-${crypto.randomBytes(4).toString('hex')}`, flag: FLAG } };

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(session({ secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'), resave: false, saveUninitialized: false, cookie: { httpOnly: true, sameSite: 'lax', secure: false } }));
app.use('/static', express.static(path.join(__dirname, 'public')));

function page(title, body) { return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} · Asterion</title><link rel="stylesheet" href="/static/app.css"></head><body><header><img src="/static/logo.webp" alt="RedTeam Hacker Academy"><span>Asterion Benefits Exchange</span></header><main>${body}</main></body></html>`; }
function auth(req, res, next) { if (!req.session.member) return res.redirect('/login'); next(); }
function jsonAuth(req, res, next) { if (!req.session.member) return res.status(401).json({ error: 'Authentication required' }); next(); }

app.get('/healthz', (_req, res) => res.json({ status: 'ok' }));
app.get('/robots.txt', (_req, res) => res.type('text').send('User-agent: *\nDisallow: /api/v2/member/internal-notices\nDisallow: /tools/partner-preview\n'));
app.get('/login', (req, res) => res.send(page('Member sign in', `<section class="auth"><p class="eyebrow">ASTERION MEMBER ACCESS</p><h1>Sign in to benefits</h1><p class="muted">Use your member account to view coverage and claims.</p>${req.query.error ? '<div class="error">Sign-in failed.</div>' : ''}<form method="post"><label>Email<input name="email" type="email" required autofocus></label><label>Password<input name="password" type="password" required></label><button>Continue</button></form><div class="demo"><strong>Training member</strong><br>${member.email}<br><code>${member.password}</code></div></section>`)));
app.post('/login', (req, res) => { if (req.body.email === member.email && req.body.password === member.password) { req.session.member = member.memberId; return res.redirect('/'); } res.redirect('/login?error=1'); });
app.post('/logout', (req, res) => req.session.destroy(() => res.redirect('/login')));
app.get('/', auth, (_req, res) => res.send(page('Member dashboard', `<section class="hero"><div><p class="eyebrow">MEMBER BENEFITS CENTER</p><h1>Welcome back, Jamie</h1><p class="muted">Coverage, claims, and partner services in one place.</p></div><form method="post" action="/logout"><button class="secondary">Sign out</button></form></section><div class="grid"><article><h2>Coverage</h2><p class="muted">Medical, dental, and vision coverage active.</p><a href="/coverage">View coverage →</a></article><article><h2>Claims</h2><p class="muted">No claims require your attention.</p><a href="/claims">View claims →</a></article><article><h2>Partner services</h2><p class="muted">Asterion-approved integrations are available.</p><a href="/partners">View partners →</a></article></div>`)));
app.get('/coverage', auth, (_req, res) => res.send(page('Coverage', '<section class="card"><p class="eyebrow">ACTIVE COVERAGE</p><h1>Employee benefits</h1><p class="muted">Your current plan is active through the end of the plan year.</p></section>')));
app.get('/claims', auth, (_req, res) => res.send(page('Claims', '<section class="card"><p class="eyebrow">CLAIMS HISTORY</p><h1>No open claims</h1><p class="muted">Recent activity is up to date.</p></section>')));
app.get('/partners', auth, (_req, res) => res.send(page('Partners', '<section class="card"><p class="eyebrow">PARTNER SERVICES</p><h1>Connected services</h1><p class="muted">The approved partner dashboard is loading configuration from the member API.</p><script src="/static/partner.js"></script></section>')));

// Deliberate CORS flaw: suffix validation accepts attacker.asterion-partners.local and credentials.
function flawedCors(req, res, next) { const origin = req.get('Origin') || ''; if (origin.endsWith('.asterion-partners.local')) { res.set('Access-Control-Allow-Origin', origin); res.set('Access-Control-Allow-Credentials', 'true'); res.set('Vary', 'Origin'); } if (req.method === 'OPTIONS') { res.set('Access-Control-Allow-Methods', 'GET, OPTIONS'); res.set('Access-Control-Allow-Headers', 'X-Partner-Client, Content-Type'); return res.sendStatus(204); } next(); }
app.options('/api/v2/member/*', flawedCors);
app.get('/api/v2/member/coverage', flawedCors, jsonAuth, (_req, res) => res.json({ member: member.memberId, plan: 'Asterion Select PPO', status: 'active' }));
app.get('/api/v2/member/claims', flawedCors, jsonAuth, (_req, res) => res.json({ member: member.memberId, open: 0, recent: [] }));
app.get('/api/v2/member/internal-notices', flawedCors, jsonAuth, (req, res) => { if (req.get('X-Partner-Client') !== 'benefits-console') return res.status(403).json({ error: 'Partner client header required' }); res.json(internalNotice); });

app.get('/tools/partner-preview', (_req, res) => res.send(page('Partner preview', '<section class="card"><p class="eyebrow">PARTNER PREVIEW TOOL</p><h1>Integration preview</h1><p class="muted">This preview loads partner data from the member API. If opened from an approved partner origin, browser credentials may be included automatically.</p><pre id="output">Waiting for partner response…</pre><script>fetch("/api/v2/member/coverage",{credentials:"include"}).then(r=>r.json()).then(x=>output.textContent=JSON.stringify(x,null,2)).catch(e=>output.textContent=e)</script></section>')));

app.listen(PORT, '0.0.0.0', () => console.log(`Asterion Benefits Exchange listening on port ${PORT}`));
