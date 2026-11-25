// Minimal single-page client. No framework, so the whole flow is readable in one file.
// The session token lives in sessionStorage, which is per browser tab: two tabs can be
// signed in as two different users at the same time.

const $ = (id) => document.getElementById(id);
const state = {
  token: sessionStorage.getItem("token"),
  conversationId: sessionStorage.getItem("conversationId"),
  library: [],
  allCompanies: [],
};

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) { signOutLocal(); throw new Error("Session expired, please sign in again."); }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res;
}

const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Tiny markdown subset: **bold**, "- " bullets, paragraphs.
function render(md) {
  const lines = esc(md).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").split("\n");
  let html = "", inList = false;
  for (const line of lines) {
    if (line.startsWith("- ")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${line.slice(2)}</li>`; continue; }
    if (inList) { html += "</ul>"; inList = false; }
    if (line.trim()) html += `<p>${line}</p>`;
  }
  return html + (inList ? "</ul>" : "");
}

// ---------------- login ----------------
async function showLogin() {
  $("app-view").classList.add("hidden");
  $("login-view").classList.remove("hidden");
  const users = await (await fetch("/api/demo-users")).json();
  state.allCompanies = [...new Set(users.flatMap((u) => u.companies))];
  $("user-cards").innerHTML = users.map((u) => `
    <button class="user-card" data-email="${esc(u.email)}">
      <b>${esc(u.name)}</b><span>${esc(u.email)}</span><span>Access: ${esc(u.companies.join(", "))}</span>
    </button>`).join("");
  document.querySelectorAll(".user-card").forEach((b) => b.onclick = () => login(b.dataset.email));
}

async function login(email) {
  $("login-error").textContent = "";
  try {
    const data = await (await api("/api/login", { method: "POST", body: JSON.stringify({ email }) })).json();
    state.token = data.token;
    state.conversationId = data.conversation_id;
    sessionStorage.setItem("token", data.token);
    sessionStorage.setItem("conversationId", data.conversation_id);
    await showApp();
  } catch (e) { $("login-error").textContent = e.message; }
}

function signOutLocal() {
  sessionStorage.clear();
  state.token = state.conversationId = null;
  showLogin();
}

// ---------------- app ----------------
async function showApp() {
  const me = await (await api("/api/me")).json();
  if (!state.allCompanies.length) {
    const users = await (await fetch("/api/demo-users")).json();
    state.allCompanies = [...new Set(users.flatMap((u) => u.companies))];
  }
  state.library = me.library;
  $("login-view").classList.add("hidden");
  $("app-view").classList.remove("hidden");
  $("who-name").textContent = me.name;
  $("who-email").textContent = me.email;
  $("avatar").textContent = me.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  $("library").innerHTML = me.library.map((c) => `
    <div class="company"><b>${esc(c.company)}</b>
      ${c.documents.map((d) => `<a data-doc="${esc(d)}">${esc(d)}</a>`).join("")}
    </div>`).join("");
  document.querySelectorAll("#library a").forEach((a) => a.onclick = () => openDoc(a.dataset.doc));
  await loadHistory();
  renderSuggestions();
  $("question").focus();
}

async function openDoc(name) {
  // Documents are fetched with the user's token, so the server checks access for every file.
  const blob = await (await api(`/api/documents/${encodeURIComponent(name)}`)).blob();
  window.open(URL.createObjectURL(blob), "_blank");
}

function renderSuggestions() {
  const mine = state.library.map((c) => c.company);
  const other = state.allCompanies.find((c) => !mine.includes(c));
  const qs = [
    "What was the revenue reported in Q4?",
    "And the gross margin?",
    "How did that compare to last year?",
    "What guidance did they give for 2026?",
  ];
  if (mine.length > 1) qs.push(`What about ${mine[1]}?`);
  if (other) qs.push(`What was ${other}${other.endsWith("s") ? "'" : "'s"} revenue?`);
  $("suggestions").innerHTML = qs.map((q) => `<button type="button">${esc(q)}</button>`).join("");
  document.querySelectorAll("#suggestions button").forEach((b) => b.onclick = () => ask(b.textContent));
}

function emptyState() {
  $("messages").innerHTML = `<div class="empty"><h2>Ask about your companies</h2>
    <p>Answers come only from the documents listed on the left. Follow-up questions such as
    "and the gross margin?" reuse the context of the conversation.</p></div>`;
}

async function loadHistory() {
  if (!state.conversationId) return emptyState();
  try {
    const turns = await (await api(`/api/conversations/${state.conversationId}`)).json();
    if (!turns.length) return emptyState();
    $("messages").innerHTML = "";
    for (const t of turns) {
      addUser(t.question);
      addBot({ answer: t.answer, sources: t.sources, trace: { standalone_query: t.standalone_query } });
    }
  } catch { emptyState(); }
}

function addUser(text) {
  const empty = document.querySelector(".empty");
  if (empty) empty.remove();
  const div = document.createElement("div");
  div.className = "msg user";
  div.textContent = text;
  $("messages").appendChild(div);
}

function addBot(r) {
  const div = document.createElement("div");
  const denied = r.answer.startsWith("Access denied");
  div.className = "msg bot" + (denied ? " denied" : "");
  const t = r.trace || {};
  const pills = (xs, cls = "") => (xs || []).map((x) => `<span class="pill ${cls}">${esc(x)}</span>`).join("") || "none";
  const traceHtml = `
    <details><summary>How this answer was built</summary>
      <dl class="trace">
        <dt>Rewritten query</dt><dd>${esc(t.standalone_query || "")}</dd>
        ${t.is_followup !== undefined ? `<dt>Follow-up?</dt><dd>${t.is_followup ? "yes, context carried from the previous turn" : "no, new question"}</dd>` : ""}
        ${t.searched_companies ? `<dt>Searched</dt><dd>${pills(t.searched_companies, "ok")}</dd>` : ""}
        ${t.denied_companies && t.denied_companies.length ? `<dt>Blocked</dt><dd>${pills(t.denied_companies, "deny")}</dd>` : ""}
      </dl>
    </details>`;
  const sourcesHtml = (r.sources || []).length ? `
    <details><summary>Sources (${r.sources.length})</summary>
      ${r.sources.map((s) => `
        <div class="source"><div class="hdr">[${s.n}] ${esc(s.company)} · ${esc(s.title)} · page ${s.page}</div>
        <div class="ex">${esc(s.excerpt)}</div></div>`).join("")}
    </details>` : "";
  div.innerHTML = render(r.answer) + sourcesHtml + traceHtml;
  $("messages").appendChild(div);
  $("messages").scrollTop = $("messages").scrollHeight;
}

async function ask(question) {
  question = question.trim();
  if (!question) return;
  addUser(question);
  $("question").value = "";
  $("send").disabled = true;
  const typing = document.createElement("div");
  typing.className = "msg bot typing";
  typing.textContent = "Searching your documents...";
  $("messages").appendChild(typing);
  try {
    const r = await (await api("/api/chat", { method: "POST",
      body: JSON.stringify({ question, conversation_id: state.conversationId }) })).json();
    state.conversationId = r.conversation_id;
    sessionStorage.setItem("conversationId", r.conversation_id);
    typing.remove();
    addBot(r);
  } catch (e) {
    typing.textContent = "Error: " + e.message;
  } finally {
    $("send").disabled = false;
    $("question").focus();
  }
}

$("chat-form").onsubmit = (e) => { e.preventDefault(); ask($("question").value); };
$("login-form").onsubmit = (e) => { e.preventDefault(); login($("email-input").value); };
$("new-chat").onclick = async () => {
  const { conversation_id } = await (await api("/api/conversations", { method: "POST" })).json();
  state.conversationId = conversation_id;
  sessionStorage.setItem("conversationId", conversation_id);
  emptyState();
};
$("logout").onclick = async () => { try { await api("/api/logout", { method: "POST" }); } catch {} signOutLocal(); };

(state.token ? showApp().catch(showLogin) : showLogin());
