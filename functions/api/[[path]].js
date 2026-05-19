const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", ...headers } });

async function sha256(text) {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function sign(value, secret) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

async function makeSession(user, secret) {
  const payload = btoa(JSON.stringify({ id: user.id, role: user.role, email: user.email, ts: Date.now() }));
  const sig = await sign(payload, secret);
  return `${payload}.${sig}`;
}

async function readSession(req, secret) {
  const cookie = req.headers.get("cookie") || "";
  const match = cookie.match(/(?:^|; )session=([^;]+)/);
  if (!match) return null;
  const token = decodeURIComponent(match[1]);
  const [payload, sig] = token.split(".");
  if (!payload || !sig) return null;
  const expected = await sign(payload, secret);
  if (expected !== sig) return null;
  return JSON.parse(atob(payload));
}

function setSessionCookie(token) {
  return `session=${encodeURIComponent(token)}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=604800`;
}
function clearSessionCookie() {
  return "session=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0";
}

async function body(req) {
  try { return await req.json(); } catch { return {}; }
}

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const method = request.method;
  const path = url.pathname.replace(/^\/api/, "") || "/";
  const session = await readSession(request, env.SESSION_SECRET || "dev-secret");

  if (path === "/auth/register" && method === "POST") {
    const b = await body(request);
    if (!b.email || !b.password || !b.full_name) return json({ error: "Dati mancanti" }, 400);
    const email = String(b.email).toLowerCase().trim();
    const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
    if (existing) return json({ error: "Email già registrata" }, 409);
    const hash = await sha256(`${b.password}:${env.PASSWORD_PEPPER || "pepper"}`);
    const res = await env.DB.prepare("INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'user')")
      .bind(String(b.full_name).trim(), email, hash).run();
    return json({ ok: true, id: res.meta.last_row_id }, 201);
  }

  if (path === "/auth/login" && method === "POST") {
    const b = await body(request);
    const email = String(b.email || "").toLowerCase().trim();
    const hash = await sha256(`${String(b.password || "")}:${env.PASSWORD_PEPPER || "pepper"}`);
    const user = await env.DB.prepare("SELECT id,email,role FROM users WHERE email = ? AND password_hash = ?").bind(email, hash).first();
    if (!user) return json({ error: "Credenziali non valide" }, 401);
    const token = await makeSession(user, env.SESSION_SECRET || "dev-secret");
    return json({ ok: true, user }, 200, { "set-cookie": setSessionCookie(token) });
  }

  if (path === "/auth/logout" && method === "POST") {
    return json({ ok: true }, 200, { "set-cookie": clearSessionCookie() });
  }

  if (!session) return json({ error: "Non autenticato" }, 401);

  if (path === "/dashboard" && method === "GET") {
    const totals = await env.DB.prepare(
      "SELECT COALESCE(SUM(production_kwh),0) total_prod, COALESCE(SUM(consumption_kwh),0) total_cons, COALESCE(SUM(km_travelled),0) total_km FROM measurements WHERE user_id = ?"
    ).bind(session.id).first();
    const measurements = await env.DB.prepare("SELECT * FROM measurements WHERE user_id=? ORDER BY day DESC LIMIT 10").bind(session.id).all();
    return json({ totals, measurements: measurements.results || [] });
  }

  if (path === "/plants" && method === "GET") {
    const rows = await env.DB.prepare("SELECT * FROM plants WHERE user_id=? ORDER BY install_date DESC").bind(session.id).all();
    return json(rows.results || []);
  }
  if (path === "/plants" && method === "POST") {
    const b = await body(request);
    await env.DB.prepare("INSERT INTO plants (user_id,name,plant_type,installed_kw,install_date) VALUES (?,?,?,?,?)")
      .bind(session.id, b.name, b.plant_type, Number(b.installed_kw || 0), b.install_date).run();
    return json({ ok: true }, 201);
  }
  if (path.startsWith("/plants/") && method === "DELETE") {
    const id = Number(path.split("/")[2]);
    await env.DB.prepare("DELETE FROM plants WHERE id=? AND user_id=?").bind(id, session.id).run();
    return json({ ok: true });
  }

  if (path === "/vehicles" && method === "GET") {
    const rows = await env.DB.prepare("SELECT * FROM vehicles WHERE user_id=? ORDER BY id DESC").bind(session.id).all();
    return json(rows.results || []);
  }
  if (path === "/vehicles" && method === "POST") {
    const b = await body(request);
    await env.DB.prepare("INSERT INTO vehicles (user_id,model,battery_kwh) VALUES (?,?,?)")
      .bind(session.id, b.model, Number(b.battery_kwh || 0)).run();
    return json({ ok: true }, 201);
  }
  if (path.startsWith("/vehicles/") && method === "DELETE") {
    const id = Number(path.split("/")[2]);
    await env.DB.prepare("DELETE FROM vehicles WHERE id=? AND user_id=?").bind(id, session.id).run();
    return json({ ok: true });
  }

  if (path === "/measurements" && method === "GET") {
    const rows = await env.DB.prepare("SELECT * FROM measurements WHERE user_id=? ORDER BY day DESC").bind(session.id).all();
    return json(rows.results || []);
  }
  if (path === "/measurements" && method === "POST") {
    const b = await body(request);
    await env.DB.prepare("INSERT INTO measurements (user_id,day,production_kwh,consumption_kwh,km_travelled) VALUES (?,?,?,?,?)")
      .bind(session.id, b.day, Number(b.production_kwh || 0), Number(b.consumption_kwh || 0), Number(b.km_travelled || 0)).run();
    return json({ ok: true }, 201);
  }
  if (path.startsWith("/measurements/") && method === "DELETE") {
    const id = Number(path.split("/")[2]);
    await env.DB.prepare("DELETE FROM measurements WHERE id=? AND user_id=?").bind(id, session.id).run();
    return json({ ok: true });
  }

  if (!session.role || session.role !== "admin") return json({ error: "Forbidden" }, 403);

  if (path === "/admin/stats" && method === "GET") {
    const [u, p, v, m] = await Promise.all([
      env.DB.prepare("SELECT COUNT(*) c FROM users").first(),
      env.DB.prepare("SELECT COUNT(*) c FROM plants").first(),
      env.DB.prepare("SELECT COUNT(*) c FROM vehicles").first(),
      env.DB.prepare("SELECT COUNT(*) c FROM measurements").first(),
    ]);
    return json({ users: u.c, plants: p.c, vehicles: v.c, measurements: m.c });
  }

  if (path === "/admin/promote" && method === "POST") {
    const b = await body(request);
    await env.DB.prepare("UPDATE users SET role='admin' WHERE id=?").bind(Number(b.user_id)).run();
    return json({ ok: true });
  }

  if (path === "/admin/export.csv" && method === "GET") {
    const rows = await env.DB.prepare("SELECT u.email,m.day,m.production_kwh,m.consumption_kwh,m.km_travelled FROM measurements m JOIN users u ON u.id=m.user_id ORDER BY m.day DESC").all();
    const lines = ["user_email,date,production_kwh,consumption_kwh,km_travelled"];
    for (const r of rows.results || []) lines.push(`${r.email},${r.day},${r.production_kwh},${r.consumption_kwh},${r.km_travelled}`);
    return new Response(lines.join("\n"), { headers: { "content-type": "text/csv; charset=utf-8" } });
  }

  return json({ error: "Not found" }, 404);
}
