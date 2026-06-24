import streamlit as st
import requests
import json
from datetime import datetime, timezone
from urllib.parse import urlencode

st.set_page_config(page_title="Painel ML", page_icon="🛒", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none; }
section[data-testid="stSidebar"] { display: none; }
.metric-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin: 1.5rem 0; }
.metric-card { background: #fff; border-radius: 12px; padding: 1.1rem 1rem; border: 1px solid #e0e0e0; }
.metric-label { font-size: 12px; color: #888; margin-bottom: 6px; }
.metric-value { font-size: 30px; font-weight: 700; }
.v-blue { color: #3483FA; } .v-red { color: #e53935; } .v-green { color: #1E8C45; } .v-yellow { color: #f5a623; }
.section-title { font-size: 18px; font-weight: 700; margin: 1.5rem 0 0.75rem; display: flex; align-items: center; gap: 8px; }
.section-title span { border-bottom: 3px solid #FFE600; padding-bottom: 2px; }
.ml-table { width: 100%; border-collapse: collapse; font-size: 13px; background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0; }
.ml-table th { padding: 11px 14px; text-align: left; font-weight: 600; font-size: 12px; color: #888; background: #fafafa; border-bottom: 1px solid #eee; }
.ml-table td { padding: 11px 14px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; color: #1a1a1a; }
.ml-table tr:last-child td { border-bottom: none; }
.ml-table tr:hover td { background: #fafafa; }
.tc { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }
.badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.b-active { background: #E8F5E9; color: #1E8C45; }
.b-paused { background: #FFF8E1; color: #f5a623; }
.b-closed { background: #FFEBEE; color: #e53935; }
.b-nosales { background: #FFEBEE; color: #e53935; }
.b-sales { background: #E8F5E9; color: #1E8C45; }
.b-old { background: #FFF8E1; color: #f5a623; }
a.ver { color: #3483FA; text-decoration: none; font-size: 12px; }
.login-box { max-width: 420px; margin: 6rem auto; background: #fff; border-radius: 16px; border: 1px solid #e0e0e0; padding: 2.5rem; text-align: center; }
.login-box h2 { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.login-box p { font-size: 13px; color: #888; margin-bottom: 2rem; }
.btn-login { display: inline-block; background: #FFE600; color: #1a1a1a; font-weight: 700; font-size: 15px; padding: 12px 32px; border-radius: 8px; text-decoration: none; border: none; cursor: pointer; }
.btn-login:hover { background: #e6cf00; }
</style>
""", unsafe_allow_html=True)

CLIENT_ID     = st.secrets["ML_CLIENT_ID"]
CLIENT_SECRET = st.secrets["ML_CLIENT_SECRET"]
REDIRECT_URI  = st.secrets["ML_REDIRECT_URI"]

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
        r = requests.get(f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=50&offset={offset}", headers=headers, timeout=15)
        ids = r.json().get("results", [])
        all_ids.extend(ids)
        if len(ids) < 50: break
        offset += 50
    listings = []
    for i in range(0, len(all_ids), 20):
        chunk = all_ids[i:i+20]
        r = requests.get(f"https://api.mercadolibre.com/items?ids={','.join(chunk)}&attributes=id,title,status,price,sold_quantity,date_created,permalink", headers=headers, timeout=15)
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
        title = l.get("title","").replace('"','&quot;').replace('<','&lt;')
        rows_html += f"""<tr>
          <td><span class="tc" title="{title}">{title}</span></td>
          <td>{status_badge(l.get('status',''))}</td>
          <td>{sales_badge(l.get('sold_quantity') or 0)}</td>
          <td>{fmt_price(l.get('price') or 0)}</td>
          <td>{age_badge(age)}</td>
          <td><a class="ver" href="{l.get('permalink','#')}" target="_blank">ver ↗</a></td>
        </tr>"""
    st.markdown(f"""
    <table class="ml-table">
      <thead><tr><th>Título</th><th>Status</th><th>Vendas</th><th>Preço</th><th>Idade</th><th>Link</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table><br>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.markdown("""
<div style='background:#FFE600;padding:0.85rem 1.5rem;display:flex;align-items:center;justify-content:space-between'>
  <div style='display:flex;align-items:center;gap:12px'>
    <div style='background:#3483FA;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center'>
      <span style='color:#fff;font-size:16px'>✔</span>
    </div>
    <span style='font-size:19px;font-weight:700;color:#1a1a1a'>Painel de Anúncios</span>
    <span style='font-size:13px;color:#555'>Mercado Livre Analytics</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── OAuth flow ────────────────────────────────────────────
params = st.query_params

# Recebeu o code do ML após login
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

# Não autenticado — mostra tela de login
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

# Renovar token se necessário
access_token = st.session_state["access_token"]
test = requests.get("https://api.mercadolibre.com/users/me", headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
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

# ── Carregar dados ────────────────────────────────────────
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

# Subtítulo + botão sair
col_a, col_b = st.columns([6,1])
with col_a:
    st.markdown(f"<div style='font-size:13px;color:#555;padding:0.4rem 0;background:#fffde7;border-bottom:1px solid #e0e0e0;padding-left:1rem'>Conectado como <strong>{nickname}</strong> · {now_str}</div>", unsafe_allow_html=True)
with col_b:
    if st.button("🚪 Sair"):
        for k in ["access_token","refresh_token"]:
            st.session_state.pop(k, None)
        st.cache_data.clear()
        st.rerun()

# Métricas
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card"><div class="metric-label">Total de anúncios</div><div class="metric-value v-blue">{total}</div></div>
  <div class="metric-card"><div class="metric-label">Sem nenhuma venda</div><div class="metric-value v-red">{len(no_sales)}</div></div>
  <div class="metric-card"><div class="metric-label">Com vendas</div><div class="metric-value v-green">{len(w_sales)}</div></div>
  <div class="metric-card"><div class="metric-label">Ativos</div><div class="metric-value v-green">{len(active)}</div></div>
  <div class="metric-card"><div class="metric-label">Pausados</div><div class="metric-value v-yellow">{len(paused)}</div></div>
  <div class="metric-card"><div class="metric-label">Fechados</div><div class="metric-value v-red">{len(closed)}</div></div>
</div>
""", unsafe_allow_html=True)

# Gráficos
age_bins = [0, 0, 0, 0]
for l in listings:
    d = age_days(l.get("date_created", ""))
    if d < 30:    age_bins[0] += 1
    elif d < 180: age_bins[1] += 1
    elif d < 365: age_bins[2] += 1
    else:         age_bins[3] += 1

st.components.v1.html(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:1.5rem">
  <div style="background:#fff;border-radius:12px;border:1px solid #e0e0e0;padding:1.25rem">
    <div style="font-size:13px;color:#888;font-weight:600;margin-bottom:1rem">Status dos anúncios</div>
    <canvas id="cStatus" role="img" aria-label="Status" style="max-height:200px"></canvas>
  </div>
  <div style="background:#fff;border-radius:12px;border:1px solid #e0e0e0;padding:1.25rem">
    <div style="font-size:13px;color:#888;font-weight:600;margin-bottom:1rem">Anúncios por idade</div>
    <canvas id="cAge" role="img" aria-label="Idade" style="max-height:200px"></canvas>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
new Chart(document.getElementById('cStatus'), {{
  type: 'doughnut',
  data: {{ labels: ['Ativos','Pausados','Fechados'], datasets: [{{ data: [{len(active)},{len(paused)},{len(closed)}], backgroundColor: ['#1E8C45','#f5a623','#e53935'], borderWidth: 0 }}] }},
  options: {{ responsive: true, maintainAspectRatio: true, plugins: {{ legend: {{ position: 'right', labels: {{ font: {{ size: 12 }}, boxWidth: 12 }} }} }} }}
}});
new Chart(document.getElementById('cAge'), {{
  type: 'bar',
  data: {{ labels: ['< 1 mês','1-6 meses','6-12 meses','> 1 ano'], datasets: [{{ data: {age_bins}, backgroundColor: ['#3483FA','#5ba4fb','#89c0fc','#c4dffd'], borderRadius: 6 }}] }},
  options: {{ responsive: true, maintainAspectRatio: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1, font: {{ size: 11 }} }} }}, x: {{ ticks: {{ font: {{ size: 11 }} }} }} }} }}
}});
</script>
""", height=280)

# Tabelas
st.markdown(f'<div class="section-title">🔴 <span>Anúncios sem nenhuma venda ({len(no_sales)})</span></div>', unsafe_allow_html=True)
render_table(sorted(no_sales, key=lambda l: age_days(l.get("date_created","")), reverse=True))

oldest = sorted(listings, key=lambda l: l.get("date_created",""))[:10]
st.markdown('<div class="section-title" style="margin-top:1.5rem">📅 <span>Anúncios mais antigos (top 10)</span></div>', unsafe_allow_html=True)
render_table(oldest)

st.markdown(f'<div class="section-title" style="margin-top:1.5rem">📋 <span>Todos os anúncios ({total})</span></div>', unsafe_allow_html=True)
col1, col2 = st.columns([2, 3])
with col1:
    filtro = st.selectbox("Status", ["Todos", "Ativos", "Pausados", "Fechados"], label_visibility="collapsed")
with col2:
    busca = st.text_input("Buscar", placeholder="Buscar por título...", label_visibility="collapsed")

dados = listings
if filtro == "Ativos":     dados = active
elif filtro == "Pausados": dados = paused
elif filtro == "Fechados": dados = closed
if busca:
    dados = [l for l in dados if busca.lower() in l.get("title","").lower()]
dados = sorted(dados, key=lambda l: age_days(l.get("date_created","")), reverse=True)
render_table(dados)

st.markdown(f"<div style='text-align:center;font-size:12px;color:#aaa;padding:1.5rem'>Painel ML · {now_str}</div>", unsafe_allow_html=True)
