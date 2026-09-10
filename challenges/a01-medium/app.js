const crypto = require('crypto');
const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT || 5000);
const FLAG = `FLAG{${crypto.randomUUID()}}`;
const reportName = `Q4_Layoff_List_${crypto.randomBytes(5).toString('hex')}.txt`;
const adminPassword = process.env.HR_ADMIN_PASSWORD || `MeridianHR-${crypto.randomBytes(18).toString('base64url')}`;

const users = new Map([
  ['alex.employee@meridianhr.local', { id: 'emp-1042', name: 'Alex Morgan', password: 'Password123', role: 'EMPLOYEE', department: 'Operations' }],
  ['hr.admin@meridianhr.local', { id: 'hr-0001', name: 'HR Administrator', password: adminPassword, role: 'HR_ADMIN', department: 'People Operations' }]
]);
const reports = new Map([[reportName, `MeridianHR Internal Memo — CONFIDENTIAL\n\nQ4 Restructuring Notes\nPrepared for authorized HR leadership only.\n\n${FLAG}\n`]]);

app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(session({
  secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, sameSite: 'lax', secure: process.env.COOKIE_SECURE === '1' }
}));
app.use('/static', express.static(path.join(__dirname, 'public')));

function page(title, body) {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} · MeridianHR</title><link rel="stylesheet" href="/static/app.css"></head><body><header><img src="/static/logo.webp" alt="RedTeam Hacker Academy"><span>MeridianHR · Internal Portal</span></header><main>${body}</main></body></html>`;
}
function requireLogin(req, res, next) { if (!req.session.user) return res.redirect('/login'); next(); }
function currentUser(req) { return req.session.user && users.get(req.session.user); }
function safe(value) { return String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c])); }

app.get('/healthz', (_req, res) => res.json({ status: 'ok' }));
app.get('/robots.txt', (_req, res) => res.type('text').send('User-agent: *\nDisallow: /internal/reports\nDisallow: /account/upgrade\n'));
app.get('/static/legacy.js', (_req, res) => res.type('application/javascript').send('// MeridianHR legacy navigation bundle\n// Internal reports path retained for old HR bookmarks: /internal/reports\n'));

app.get('/login', (req, res) => {
  if (req.session.user) return res.redirect('/');
  res.send(page('Sign in', `<section class="auth"><h1>Employee sign in</h1><p class="muted">Use your MeridianHR SSO credentials.</p>${req.query.error ? '<div class="error">Sign-in failed.</div>' : ''}<form method="post"><label>Work email<input name="email" type="email" required autofocus></label><label>Password<input name="password" type="password" required></label><button>Sign in</button></form><div class="demo"><strong>Training account</strong><br>alex.employee@meridianhr.local<br><code>Password123</code></div></section>`));
});
app.post('/login', (req, res) => {
  const user = users.get(String(req.body.email || '').toLowerCase());
  if (!user || user.password !== req.body.password) return res.redirect('/login?error=1');
  req.session.user = String(req.body.email).toLowerCase();
  res.redirect('/');
});
app.post('/logout', (req, res) => req.session.destroy(() => res.redirect('/login')));

app.get('/', requireLogin, (req, res) => {
  const user = currentUser(req);
  res.send(page('Employee dashboard', `<section class="hero"><div><p class="eyebrow">MERIDIANHR WORKFORCE SERVICES</p><h1>Good morning, ${safe(user.name)}</h1><p class="muted">Employee self-service portal · ${safe(user.department)}</p></div><form method="post" action="/logout"><button class="secondary">Sign out</button></form></section><div class="grid"><article><h2>Leave requests</h2><p class="muted">No pending requests.</p><a href="#">View leave history →</a></article><article><h2>Payroll</h2><p class="muted">Your next pay date is the 25th.</p><a href="#">View pay statements →</a></article><article><h2>Role review</h2><p class="muted">Annual access review available.</p><a href="/account/upgrade/start">Review account access →</a></article></div>`));
});

// Intentional hard-lab workflow flaw: every step requires a session, but no role/approval state is enforced.
app.get('/account/upgrade/start', requireLogin, (_req, res) => res.send(page('Role review', '<section class="card"><p class="eyebrow">ACCESS REVIEW · STEP 1 OF 3</p><h1>Confirm your employment details</h1><p class="muted">Your manager and department records are up to date.</p><a class="button" href="/account/upgrade/confirm">Continue review</a></section>')));
app.get('/account/upgrade/confirm', requireLogin, (_req, res) => res.send(page('Role review', '<section class="card"><p class="eyebrow">ACCESS REVIEW · STEP 2 OF 3</p><h1>Confirm elevated responsibilities</h1><p class="muted">This review is normally completed by HR.</p><a class="button" href="/account/upgrade/finalize">Submit review</a></section>')));
app.post('/account/upgrade/finalize', requireLogin, (req, res) => { const user = currentUser(req); user.role = 'HR_ADMIN'; req.session.role = 'HR_ADMIN'; res.redirect('/admin/dashboard'); });
app.get('/account/upgrade/finalize', requireLogin, (req, res) => { const user = currentUser(req); user.role = 'HR_ADMIN'; req.session.role = 'HR_ADMIN'; res.redirect('/admin/dashboard'); });

app.get('/admin/dashboard', requireLogin, (req, res) => { if (currentUser(req).role !== 'HR_ADMIN') return res.status(403).send(page('Forbidden', '<section class="card"><h1>403 — HR access required</h1></section>')); res.send(page('HR dashboard', '<section class="card"><p class="eyebrow">HR ADMINISTRATION</p><h1>People operations console</h1><p class="muted">Manage employee access, role reviews, and internal reports.</p><a class="button" href="/internal/reports">Open internal reports</a></section>')); });
app.get('/admin/deleteUser', requireLogin, (req, res) => { if (currentUser(req).role !== 'HR_ADMIN') return res.status(403).json({ error: 'HR_ADMIN role required' }); res.json({ success: true, message: 'GET deletion endpoint is protected.' }); });
// Intentional method-based bypass: legacy POST has no role check.
app.post('/admin/deleteUser', requireLogin, (req, res) => res.json({ success: true, message: 'Legacy employee deletion queued.', employee: req.body.employee || 'unknown' }));

app.get('/internal/reports', requireLogin, (req, res) => { if (!String(req.get('referer') || '').includes('/admin/dashboard')) return res.status(403).send(page('Forbidden', '<section class="card"><h1>Report access denied</h1></section>')); res.send(page('Internal reports', `<section class="card"><p class="eyebrow">CONFIDENTIAL HR REPORTS</p><h1>Internal reports</h1><ul><li><a href="/internal/reports/${encodeURIComponent(reportName)}">${safe(reportName)}</a></li></ul></section>`)); });
app.get('/internal/reports/:name', requireLogin, (req, res) => { if (!String(req.get('referer') || '').includes('/admin/dashboard')) return res.status(403).send('Report access denied'); const content = reports.get(req.params.name); if (!content) return res.status(404).send('Report not found'); res.type('text').send(content); });

app.listen(PORT, '0.0.0.0', () => { console.log(`MeridianHR listening on port ${PORT}`); if (process.env.SHOW_DEV_CREDENTIALS === '1') console.log(`DEV HR password: ${adminPassword}`); });
