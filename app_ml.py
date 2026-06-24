import streamlit as st
import requests
from datetime import datetime, timezone

st.set_page_config(page_title="Painel ML", page_icon="🛒", layout="wide")

st.markdown("""
<style>
/* ── Fundo geral escuro ── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0d0d0d !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
    background-color: #0d0d0d !important;
}
header[data-testid="stHeader"] { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* ── Textos nativos do Streamlit ── */
.stApp p, .stApp label, .stApp span, .stApp div { color: #e0e0e0; }

/* ── Selectbox e inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input {
    background-color: #1e1e1e !important;
    border: 1px solid #333 !important;
    color: #e0e0e0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] svg { fill: #FFE600 !important; }
div[data-baseweb="popover"] { background-color: #1e1e1e !important; }
ul[data-testid="stSelectboxVirtualDropdown"] {
    background-color: #1e1e1e !important;
    border: 1px solid #333 !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover { background-color: #2a2a2a !important; }
ul[data-testid="stSelectboxVirtualDropdown"] li span { color: #e0e0e0 !important; }

/* ── Botão Sair ── */
.st-key-btn_sair button {
    background-color: #1e1e1e !important;
    color: #FFE600 !important;
    border: 1px solid #FFE600 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    height: auto !important;
    padding: 0.4rem 1rem !important;
    font-size: 14px !important;
    text-align: center !important;
    white-space: nowrap !important;
}
.st-key-btn_sair button:hover {
    background-color: #FFE600 !important;
    color: #0d0d0d !important;
}

/* ── Spinner e mensagens ── */
[data-testid="stStatusWidget"] { color: #FFE600 !important; }
.stSuccess { background-color: #0f2a0f !important; color: #4caf50 !important; border: 1px solid #2e7d32 !important; }

/* ── Tabela ── */
.ml-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
    background: #1a1a1a; border-radius: 12px; overflow: hidden; border: 1px solid #2e2e2e;
}
.ml-table th {
    padding: 11px 14px; text-align: left; font-weight: 600;
    font-size: 12px; color: #888; background: #111; border-bottom: 1px solid #2e2e2e;
}
.ml-table td {
    padding: 11px 14px; border-bottom: 1px solid #222;
    vertical-align: middle; color: #e0e0e0;
}
.ml-table tr:last-child td { border-bottom: none; }
.ml-table tr:hover td { background: #222; }
.tc { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }

/* ── Badges ── */
.badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.b-active  { background: #0f2a0f; color: #66bb6a; }
.b-paused  { background: #2a1f00; color: #ffa726; }
.b-closed  { background: #2a0a0a; color: #ef5350; }
.b-nosales { background: #2a0a0a; color: #ef5350; }
.b-sales   { background: #0f2a0f; color: #66bb6a; }
.b-old     { background: #2a1f00; color: #ffa726; }
a.ver { color: #FFE600; text-decoration: none; font-size: 12px; }
a.ver:hover { color: #fff; }

/* ── Login ── */
.login-box {
    max-width: 420px; margin: 6rem auto; background: #1a1a1a;
    border-radius: 16px; border: 1px solid #2e2e2e; padding: 2.5rem; text-align: center;
}
.login-box h2 { font-size: 20px; font-weight: 700; margin-bottom: 8px; color: #f0f0f0; }
.login-box p  { font-size: 13px; color: #888; margin-bottom: 2rem; }
.btn-login {
    display: inline-block; background: #FFE600; color: #0d0d0d;
    font-weight: 700; font-size: 15px; padding: 12px 32px;
    border-radius: 8px; text-decoration: none; border: none; cursor: pointer;
}
.btn-login:hover { background: #e6cf00; }

/* ══════════════════════════════════════════════════════════
   METRIC CARDS — blocos clicáveis em grid 3x2
   ══════════════════════════════════════════════════════════ */

/* Base: todos os card-buttons */
.st-key-card_total button,
.st-key-card_nosales button,
.st-key-card_wsales button,
.st-key-card_active button,
.st-key-card_paused button,
.st-key-card_closed button {
    background-color: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    border-radius: 14px !important;
    height: 90px !important;
    width: 100% !important;
    padding: 0.85rem 1.4rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    white-space: pre-line !important;
    line-height: 1.5 !important;
    font-size: 11px !important;
    color: #FFE600 !important;
    font-weight: 600 !important;
    transition: border-color .15s, background .15s !important;
    cursor: pointer !important;
}
.st-key-card_total button:hover,
.st-key-card_nosales button:hover,
.st-key-card_wsales button:hover,
.st-key-card_active button:hover,
.st-key-card_paused button:hover,
.st-key-card_closed button:hover {
    background-color: #222 !important;
    border-color: #FFE600 !important;
}

/* Número — segunda linha do label (texto maior) */
.st-key-card_total button p,
.st-key-card_nosales button p,
.st-key-card_wsales button p,
.st-key-card_active button p,
.st-key-card_paused button p,
.st-key-card_closed button p {
    font-size: 11px !important;
    color: #FFE600 !important;
    line-height: 1.5 !important;
}

/* Número (primeira linha) — maior e bold */
.st-key-card_total button p::first-line,
.st-key-card_nosales button p::first-line,
.st-key-card_wsales button p::first-line,
.st-key-card_active button p::first-line,
.st-key-card_paused button p::first-line,
.st-key-card_closed button p::first-line {
    font-size: 34px !important;
    font-weight: 800 !important;
    color: #FFE600 !important;
}

/* Parágrafo alinhado à esquerda */
.st-key-card_total button p,
.st-key-card_nosales button p,
.st-key-card_wsales button p,
.st-key-card_active button p,
.st-key-card_paused button p,
.st-key-card_closed button p {
    text-align: left !important;
    width: 100% !important;
}

/* Card SELECIONADO — borda destacada */
.st-key-card_total.selected-card button   { border-color: #FFE600 !important; background: #1e1c00 !important; }
.st-key-card_nosales.selected-card button { border-color: #ef5350 !important; background: #1e0808 !important; }
.st-key-card_wsales.selected-card button  { border-color: #66bb6a !important; background: #081e08 !important; }
.st-key-card_active.selected-card button  { border-color: #66bb6a !important; background: #081e08 !important; }
.st-key-card_paused.selected-card button  { border-color: #ffa726 !important; background: #1e1200 !important; }
.st-key-card_closed.selected-card button  { border-color: #ef5350 !important; background: #1e0808 !important; }

/* Painel de tabela abaixo do grid */
.table-panel {
    background: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-top: 4px;
}
.panel-title {
    font-size: 15px;
    font-weight: 700;
    color: #f0f0f0;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)

CLIENT_ID     = st.secrets["ML_CLIENT_ID"]
CLIENT_SECRET = st.secrets["ML_CLIENT_SECRET"]
REDIRECT_URI  = st.secrets["ML_REDIRECT_URI"]

# ── Helpers ────────────────────────────────────────────────
def age_days(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except:
        return 0

def fmt_age(days):
    if days < 30:  return f"{days} dias"
    if days < 365: return f"{days // 30} meses"
    return f"{days / 365:.1f} anos"

def fmt_price(p):
    return f"R$ {p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def status_label(s):
    return {"active": "ativo", "paused": "pausado", "closed": "fechado"}.get(s, s)

def status_badge(s):
    cls = {"active": "b-active", "paused": "b-paused", "closed": "b-closed"}.get(s, "b-paused")
    return f'<span class="badge {cls}">{status_label(s)}</span>'

def sales_badge(n):
    return f'<span class="badge {"b-nosales" if n == 0 else "b-sales"}">{n}</span>'

def age_badge(days):
    if days > 365:
        return f'<span class="badge b-old">{fmt_age(days)}</span>'
    return fmt_age(days)

SORT_OPTIONS = ["Mais vendidos", "Mais recentes", "Mais antigos", "Maior preço", "Menor preço"]

def sort_data(data, criterion):
    if criterion == "Mais vendidos":
        return sorted(data, key=lambda l: l.get("sold_quantity") or 0, reverse=True)
    elif criterion == "Mais recentes":
        return sorted(data, key=lambda l: l.get("date_created", ""), reverse=True)
    elif criterion == "Mais antigos":
        return sorted(data, key=lambda l: l.get("date_created", ""))
    elif criterion == "Maior preço":
        return sorted(data, key=lambda l: l.get("price") or 0, reverse=True)
    elif criterion == "Menor preço":
        return sorted(data, key=lambda l: l.get("price") or 0)
    return data

def exchange_code(code):
    r = requests.post("https://api.mercadolibre.com/oauth/token", data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }, timeout=15)
    r.raise_for_status()
    return r.json()

def refresh_token_fn(refresh_token):
    r = requests.post("https://api.mercadolibre.com/oauth/token", data={
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }, timeout=15)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=False)
def load_listings(token):
    headers = {"Authorization": f"Bearer {token}"}
    me = requests.get("https://api.mercadolibre.com/users/me", headers=headers, timeout=15)
    me.raise_for_status()
    user_id = me.json()["id"]
    nickname = me.json().get("nickname", str(user_id))
    all_ids = []
    offset = 0
    while True:
        r = requests.get(
            f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=50&offset={offset}",
            headers=headers, timeout=15
        )
        ids = r.json().get("results", [])
        all_ids.extend(ids)
        if len(ids) < 50: break
        offset += 50
    listings = []
    for i in range(0, len(all_ids), 20):
        chunk = all_ids[i:i+20]
        r = requests.get(
            f"https://api.mercadolibre.com/items?ids={','.join(chunk)}"
            f"&attributes=id,title,status,price,sold_quantity,date_created,permalink",
            headers=headers, timeout=15
        )
        for item in r.json():
            if item.get("code") == 200 and item.get("body"):
                listings.append(item["body"])
    return nickname, listings

def render_table(data):
    if not data:
        st.success("Nenhum anúncio nesta categoria!")
        return
    rows_html = ""
    for l in data:
        age = age_days(l.get("date_created", ""))
        title = l.get("title", "").replace('"', '&quot;').replace('<', '&lt;')
        rows_html += f"""<tr>
          <td><span class="tc" title="{title}">{title}</span></td>
          <td>{status_badge(l.get('status', ''))}</td>
          <td>{sales_badge(l.get('sold_quantity') or 0)}</td>
          <td>{fmt_price(l.get('price') or 0)}</td>
          <td>{age_badge(age)}</td>
          <td><a class="ver" href="{l.get('permalink', '#')}" target="_blank">ver ↗</a></td>
        </tr>"""
    st.markdown(f"""
    <table class="ml-table">
      <thead><tr><th>Título</th><th>Status</th><th>Vendas</th><th>Preço</th><th>Idade</th><th>Link</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table><br>
    """, unsafe_allow_html=True)

def section_sort(key, default_index=0):
    _, col_sort = st.columns([4, 1])
    with col_sort:
        return st.selectbox("Ordenar por", SORT_OPTIONS, index=default_index, key=key, label_visibility="collapsed")

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div style='background:#FFE600;padding:0.85rem 1.5rem;display:flex;align-items:center;gap:12px'>
  <div style='background:#0d0d0d;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center'>
    <span style='color:#FFE600;font-size:16px'>✔</span>
  </div>
  <span style='font-size:19px;font-weight:700;color:#0d0d0d'>Painel de Anúncios</span>
  <span style='font-size:13px;color:#555'>Mercado Livre Analytics</span>
</div>
""", unsafe_allow_html=True)

# ── OAuth flow ─────────────────────────────────────────────
params = st.query_params

if "code" in params and "access_token" not in st.session_state:
    with st.spinner("Autenticando..."):
        try:
            token_data = exchange_code(params["code"])
            st.session_state["access_token"]  = token_data["access_token"]
            st.session_state["refresh_token"] = token_data.get("refresh_token", "")
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erro na autenticação: {e}")
            st.stop()

if "access_token" not in st.session_state:
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )
    st.markdown(f"""
    <div class="login-box">
      <div style='font-size:48px;margin-bottom:1rem'>🛒</div>
      <h2>Painel de Anúncios</h2>
      <p>Faça login com sua conta do Mercado Livre<br>para visualizar e analisar seus anúncios.</p>
      <a href="{auth_url}" class="btn-login">🔑 Entrar com Mercado Livre</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Renovar token se necessário — verifica no máximo 1× a cada 5 min
import time as _time
access_token = st.session_state["access_token"]
_last_check  = st.session_state.get("_last_token_check", 0)

if _time.time() - _last_check > 300:          # só bate na API a cada 5 min
    test = requests.get(
        "https://api.mercadolibre.com/users/me",
        headers={"Authorization": f"Bearer {access_token}"}, timeout=10
    )
    st.session_state["_last_token_check"] = _time.time()
    if test.status_code == 401 and st.session_state.get("refresh_token"):
        try:
            new_tokens = refresh_token_fn(st.session_state["refresh_token"])
            st.session_state["access_token"]  = new_tokens["access_token"]
            st.session_state["refresh_token"] = new_tokens.get("refresh_token", st.session_state["refresh_token"])
            access_token = st.session_state["access_token"]
            st.cache_data.clear()
        except:
            del st.session_state["access_token"]
            st.rerun()

# ── Carregar dados ─────────────────────────────────────────
with st.spinner("Carregando seus anúncios..."):
    try:
        nickname, listings = load_listings(access_token)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

total    = len(listings)
no_sales = [l for l in listings if (l.get("sold_quantity") or 0) == 0]
w_sales  = [l for l in listings if (l.get("sold_quantity") or 0) > 0]
active   = [l for l in listings if l.get("status") == "active"]
paused   = [l for l in listings if l.get("status") == "paused"]
closed   = [l for l in listings if l.get("status") == "closed"]
now_str  = datetime.now().strftime("%d/%m/%Y %H:%M")

# ── Barra de usuário + botão sair ──────────────────────────
col_a, col_b = st.columns([6, 1])
with col_a:
    st.markdown(
        f"<div style='font-size:13px;color:#aaa;padding:0.4rem 0;background:#111;"
        f"border-bottom:1px solid #2e2e2e;padding-left:1rem'>"
        f"Conectado como <strong style='color:#FFE600'>{nickname}</strong> · {now_str}</div>",
        unsafe_allow_html=True
    )
with col_b:
    if st.button("🚪 Sair", key="btn_sair"):
        for k in ["access_token", "refresh_token"]:
            st.session_state.pop(k, None)
        st.cache_data.clear()
        st.rerun()

# ── Gráficos (topo) ─────────────────────────────────────────
age_bins = [0, 0, 0, 0]
for l in listings:
    d = age_days(l.get("date_created", ""))
    if d < 30:    age_bins[0] += 1
    elif d < 180: age_bins[1] += 1
    elif d < 365: age_bins[2] += 1
    else:         age_bins[3] += 1

st.components.v1.html(f"""
<div style="background:#0d0d0d;padding:4px 0 8px 0">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:0.5rem">
  <div style="background:#1a1a1a;border-radius:12px;border:1px solid #2e2e2e;padding:1.25rem">
    <div style="font-size:13px;color:#888;font-weight:600;margin-bottom:1rem">Status dos anúncios</div>
    <canvas id="cStatus" style="max-height:200px"></canvas>
  </div>
  <div style="background:#1a1a1a;border-radius:12px;border:1px solid #2e2e2e;padding:1.25rem">
    <div style="font-size:13px;color:#888;font-weight:600;margin-bottom:1rem">Anúncios por idade</div>
    <canvas id="cAge" style="max-height:200px"></canvas>
  </div>
</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
Chart.defaults.color = '#888';
new Chart(document.getElementById('cStatus'), {{
  type: 'doughnut',
  data: {{ labels: ['Ativos','Pausados','Fechados'], datasets: [{{ data: [{len(active)},{len(paused)},{len(closed)}], backgroundColor: ['#66bb6a','#ffa726','#ef5350'], borderWidth: 0 }}] }},
  options: {{ responsive: true, maintainAspectRatio: true, plugins: {{ legend: {{ position: 'right', labels: {{ color:'#bbb', font: {{ size: 12 }}, boxWidth: 12 }} }} }} }}
}});
new Chart(document.getElementById('cAge'), {{
  type: 'bar',
  data: {{ labels: ['< 1 mês','1-6 meses','6-12 meses','> 1 ano'], datasets: [{{ data: {age_bins}, backgroundColor: ['#FFE600','#c9b800','#9e8f00','#6e6300'], borderRadius: 6 }}] }},
  options: {{
    responsive: true, maintainAspectRatio: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ beginAtZero: true, ticks: {{ stepSize: 1, font: {{ size: 11 }}, color:'#888' }}, grid: {{ color:'#222' }} }},
      x: {{ ticks: {{ font: {{ size: 11 }}, color:'#888' }}, grid: {{ color:'#222' }} }}
    }}
  }}
}});
</script>
""", height=290)

# ══════════════════════════════════════════════════════════
# ── Grid de cards (3 × 2) + tabela abaixo ─────────────────
# ══════════════════════════════════════════════════════════

# Estado: qual seção está aberta
if "open_section" not in st.session_state:
    st.session_state["open_section"] = None

def toggle(name):
    st.session_state["open_section"] = name if st.session_state["open_section"] != name else None

# ── Linha 1 de cards ──────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    if st.button(
        f"{total}\nTotal de anúncios",
        key="card_total", use_container_width=True
    ):
        toggle("total")

with c2:
    if st.button(
        f"{len(no_sales)}\nSem nenhuma venda",
        key="card_nosales", use_container_width=True
    ):
        toggle("nosales")

with c3:
    if st.button(
        f"{len(w_sales)}\nCom vendas",
        key="card_wsales", use_container_width=True
    ):
        toggle("wsales")

# ── Linha 2 de cards ──────────────────────────────────────
c4, c5, c6 = st.columns(3)

with c4:
    if st.button(
        f"{len(active)}\nAtivos",
        key="card_active", use_container_width=True
    ):
        toggle("active")

with c5:
    if st.button(
        f"{len(paused)}\nPausados",
        key="card_paused", use_container_width=True
    ):
        toggle("paused")

with c6:
    if st.button(
        f"{len(closed)}\nFechados",
        key="card_closed", use_container_width=True
    ):
        toggle("closed")

# Lê o estado DEPOIS dos botões — captura o toggle do clique atual
open_sec = st.session_state.get("open_section")

# ── CSS dinâmico: destaca o card selecionado ──────────────
if open_sec:
    key_map = {
        "total":   ("card_total",   "#FFE600", "#1e1c00"),
        "nosales": ("card_nosales", "#ef5350", "#1e0808"),
        "wsales":  ("card_wsales",  "#66bb6a", "#081e08"),
        "active":  ("card_active",  "#66bb6a", "#081e08"),
        "paused":  ("card_paused",  "#ffa726", "#1e1200"),
        "closed":  ("card_closed",  "#ef5350", "#1e0808"),
    }
    css_key, bdr_color, bg_color = key_map[open_sec]
    st.markdown(f"""
    <style>
    .st-key-{css_key} button {{
        border-color: {bdr_color} !important;
        background-color: {bg_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ── Painel da tabela (largura total) ──────────────────────
PANEL_TITLES = {
    "total":   ("📋", "Total de anúncios"),
    "nosales": ("🔴", "Sem nenhuma venda"),
    "wsales":  ("🟢", "Com vendas"),
    "active":  ("✅", "Ativos"),
    "paused":  ("⏸️", "Pausados"),
    "closed":  ("🚫", "Fechados"),
}

if open_sec:
    icon, title = PANEL_TITLES[open_sec]

    st.markdown(f"""
    <div style="background:#1a1a1a;border:1px solid #2e2e2e;border-radius:14px;
                padding:1.2rem 1.4rem;margin-top:4px">
      <div style="font-size:15px;font-weight:700;color:#f0f0f0;
                  margin-bottom:1rem;display:flex;align-items:center;gap:8px">
        <span>{icon}</span> {title}
      </div>
    """, unsafe_allow_html=True)

    # Filtro extra para "Total"
    if open_sec == "total":
        f1, f2, f3 = st.columns([2, 3, 2])
        with f1:
            filtro = st.selectbox(
                "Status", ["Todos", "Ativos", "Pausados", "Fechados"],
                label_visibility="collapsed", key="filtro_todos"
            )
        with f2:
            busca = st.text_input(
                "Buscar", placeholder="🔍  Buscar por título...",
                label_visibility="collapsed", key="busca_todos"
            )
        with f3:
            ordem = st.selectbox(
                "Ordenar", SORT_OPTIONS,
                key="ord_todos", label_visibility="collapsed"
            )
        dados = listings
        if filtro == "Ativos":     dados = active
        elif filtro == "Pausados": dados = paused
        elif filtro == "Fechados": dados = closed
        if busca:
            dados = [l for l in dados if busca.lower() in l.get("title", "").lower()]
        render_table(sort_data(dados, ordem))

    else:
        sort_map = {
            "nosales": ("ord_nosales", 2),
            "wsales":  ("ord_wsales",  0),
            "active":  ("ord_active",  0),
            "paused":  ("ord_paused",  0),
            "closed":  ("ord_closed",  1),
        }
        sort_key, sort_def = sort_map[open_sec]
        data_map = {
            "nosales": no_sales,
            "wsales":  w_sales,
            "active":  active,
            "paused":  paused,
            "closed":  closed,
        }
        _, col_sort = st.columns([4, 1])
        with col_sort:
            ordem = st.selectbox(
                "Ordenar por", SORT_OPTIONS,
                index=sort_def, key=sort_key,
                label_visibility="collapsed"
            )
        render_table(sort_data(data_map[open_sec], ordem))

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"<div style='text-align:center;font-size:12px;color:#444;padding:1.5rem'>Painel ML · {now_str}</div>",
    unsafe_allow_html=True
)
