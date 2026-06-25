import streamlit as st
import time
from src.agents.agents import run_search, build_reader_agent, get_writer_chain, get_critic_chain

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Master CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Calibri:wght@300;400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&display=swap');

:root {
  --bg:        #07090f;
  --bg2:       #0d1117;
  --surface:   #111827;
  --surface2:  #1a2235;
  --border:    rgba(99,179,237,0.18);
  --border2:   rgba(99,179,237,0.35);
  --accent:    #38bdf8;
  --accent2:   #818cf8;
  --accent3:   #34d399;
  --accent4:   #f472b6;
  --text:      #e2e8f0;
  --muted:     #64748b;
  --muted2:    #94a3b8;
  --card-glow: 0 0 40px rgba(56,189,248,0.08);
  --radius:    16px;
  --font:      'DM Sans', 'Calibri', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: var(--font) !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 1.5rem 4rem !important; max-width: 860px !important; }

/* ── HEADER ─────────────────────────────────────────────────────────────── */
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: rgba(7,9,15,0.92);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  padding: 0.9rem 2rem;
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 0;
}
.header-brand {
  display: flex; flex-direction: column; gap: 2px;
}
.header-title {
  font-size: 1rem; font-weight: 700; color: #fff;
  letter-spacing: -0.01em; line-height: 1.2;
}
.header-sub {
  font-size: 0.68rem; color: var(--accent); letter-spacing: 0.12em;
  text-transform: uppercase; font-weight: 500;
}
.header-badges {
  display: flex; gap: 0.5rem; align-items: center;
}
.badge {
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.25);
  color: var(--accent); font-size: 0.68rem;
  padding: 0.28rem 0.7rem; border-radius: 20px;
  font-weight: 600; letter-spacing: 0.05em;
}
.badge.green { background: rgba(52,211,153,0.1); border-color: rgba(52,211,153,0.25); color: var(--accent3); }
.badge.purple { background: rgba(129,140,248,0.1); border-color: rgba(129,140,248,0.25); color: var(--accent2); }

/* ── HERO ────────────────────────────────────────────────────────────────── */
.hero {
  text-align: center;
  padding: 3.5rem 1rem 2.5rem;
  position: relative;
}
.hero::before {
  content: '';
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 300px;
  background: radial-gradient(ellipse at center top, rgba(56,189,248,0.12) 0%, transparent 70%);
  pointer-events: none;
}
.hero-kicker {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(56,189,248,0.08);
  border: 1px solid rgba(56,189,248,0.2);
  border-radius: 20px; padding: 0.35rem 1rem;
  font-size: 0.72rem; color: var(--accent);
  letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600;
  margin-bottom: 1.4rem;
}
.hero-kicker::before { content: '●'; font-size: 0.5rem; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.hero h1 {
  font-size: clamp(1.9rem, 6vw, 3rem);
  font-weight: 700; line-height: 1.15;
  letter-spacing: -0.03em; color: #fff;
  margin-bottom: 0.5rem;
}
.hero h1 em {
  font-style: normal;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 50%, var(--accent4) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-stack {
  font-size: 0.82rem; color: var(--muted2); margin-bottom: 0.4rem;
  letter-spacing: 0.04em;
}

/* ── TABS ────────────────────────────────────────────────────────────────── */
.tab-row {
  display: flex; gap: 0.5rem; justify-content: center;
  margin: 1.5rem 0 2rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.tab-btn {
  background: transparent;
  border: none; border-bottom: 2px solid transparent;
  color: var(--muted); font-family: var(--font);
  font-size: 0.85rem; font-weight: 600;
  padding: 0.7rem 1.4rem; cursor: pointer;
  letter-spacing: 0.04em; transition: all 0.2s ease;
  margin-bottom: -1px;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

/* ── INPUT CARD ──────────────────────────────────────────────────────────── */
.input-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.8rem 2rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--card-glow);
  transition: border-color 0.3s;
}
.input-wrap:hover { border-color: var(--border2); }
.input-label {
  font-size: 0.72rem; font-weight: 600; color: var(--accent);
  letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.7rem;
}

.stTextInput > div > div > input {
  background: var(--bg2) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  color: #fff !important;
  font-family: var(--font) !important;
  font-size: 1rem !important;
  padding: 0.85rem 1.2rem !important;
  transition: all 0.25s ease !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
  outline: none !important;
}
.stTextInput > label { display: none !important; }

/* ── EXAMPLE CHIPS ───────────────────────────────────────────────────────── */
.chips-row {
  display: flex; gap: 0.5rem; flex-wrap: wrap;
  margin-bottom: 1.8rem;
}
.chip-label {
  font-size: 0.68rem; color: var(--muted);
  padding: 0.4rem 0; letter-spacing: 0.06em;
  text-transform: uppercase; font-weight: 600;
  white-space: nowrap; align-self: center;
}
.chip {
  background: rgba(129,140,248,0.08);
  border: 1px solid rgba(129,140,248,0.22);
  border-radius: 20px; padding: 0.35rem 0.9rem;
  font-size: 0.78rem; color: #c7d2fe;
  cursor: default; transition: all 0.2s ease;
  font-family: var(--font);
}
.chip:hover {
  background: rgba(129,140,248,0.18);
  border-color: rgba(129,140,248,0.4);
  transform: translateY(-1px);
}

/* ── ALL BUTTONS ─────────────────────────────────────────────────────────── */
.stButton > button {
  background: transparent !important;
  border: 1.5px solid var(--border2) !important;
  color: var(--muted2) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important; font-size: 1.05rem !important;
  border-radius: 12px !important;
  padding: 0.75rem 1.5rem !important;
  cursor: pointer !important;
  transition: all 0.25s ease !important;
  width: 100% !important;
  box-shadow: none !important;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: rgba(56,189,248,0.06) !important;
  transform: none !important;
  box-shadow: none !important;
}
.stButton > button:active { transform: translateY(0) !important; }

[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 60%, #8b5cf6 100%) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 24px rgba(14,165,233,0.3) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 14px 36px rgba(14,165,233,0.45) !important;
  filter: brightness(1.08) !important;
  color: #fff !important;
  border: none !important;
}

/* ── PIPELINE CARDS ──────────────────────────────────────────────────────── */
.pipeline-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1.5rem; margin: 1.5rem 0;
}
@media (max-width: 600px) { .pipeline-grid { grid-template-columns: 1fr; } }

.p-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.5rem;
  position: relative; overflow: hidden;
  transition: all 0.3s ease;
  cursor: default;
}
.p-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0; transition: opacity 0.3s;
}
.p-card:hover { border-color: var(--border2); box-shadow: var(--card-glow); }
.p-card:hover::before { opacity: 1; }
.p-card.active {
  border-color: rgba(56,189,248,0.5);
  background: linear-gradient(135deg, rgba(56,189,248,0.08), var(--surface));
  box-shadow: 0 0 30px rgba(56,189,248,0.15);
  animation: cardPulse 1.5s ease infinite;
}
.p-card.active::before { opacity: 1; }
.p-card.done {
  border-color: rgba(52,211,153,0.4);
  background: linear-gradient(135deg, rgba(52,211,153,0.06), var(--surface));
}
.p-card.done::before {
  background: linear-gradient(90deg, transparent, var(--accent3), transparent);
  opacity: 1;
}
@keyframes cardPulse {
  0%,100% { box-shadow: 0 0 20px rgba(56,189,248,0.1); }
  50%      { box-shadow: 0 0 40px rgba(56,189,248,0.25); }
}

.p-card-top {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 0.8rem;
}
.p-icon {
  width: 2.6rem; height: 2.6rem;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.p-num {
  font-size: 0.65rem; font-weight: 700; color: var(--muted);
  letter-spacing: 0.12em; text-transform: uppercase;
}
.p-status {
  font-size: 0.65rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  padding: 0.2rem 0.6rem; border-radius: 20px;
}
.ps-wait  { color: var(--muted); background: rgba(100,116,139,0.12); }
.ps-run   { color: var(--accent); background: rgba(56,189,248,0.12); animation: blink 1s infinite; }
.ps-done  { color: var(--accent3); background: rgba(52,211,153,0.12); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.5} }

.p-title {
  font-size: 0.95rem; font-weight: 700; color: #fff;
  margin-bottom: 0.25rem;
}
.p-desc { font-size: 0.78rem; color: var(--muted2); line-height: 1.5; }

/* ── SECTION HEADING ─────────────────────────────────────────────────────── */
.sec-heading {
  font-size: 1.1rem; font-weight: 700; color: #fff;
  margin: 2rem 0 1rem;
  display: flex; align-items: center; gap: 0.6rem;
}
.sec-heading::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
}

/* ── RESULT EXPANDERS ────────────────────────────────────────────────────── */
details {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  margin-bottom: 0.8rem;
  overflow: hidden;
}
details[open] { border-color: var(--border2) !important; }
details summary {
  font-family: var(--font) !important;
  font-size: 0.85rem !important; font-weight: 600 !important;
  color: var(--muted2) !important;
  padding: 1rem 1.3rem !important;
  cursor: pointer; list-style: none;
  display: flex; align-items: center; gap: 0.5rem;
  transition: color 0.2s;
}
details summary:hover { color: var(--text) !important; }
details summary::-webkit-details-marker { display: none; }

.result-inner {
  padding: 1rem 1.3rem 1.3rem;
  font-size: 0.85rem; line-height: 1.85;
  color: var(--muted2); white-space: pre-wrap;
  border-top: 1px solid var(--border);
}

/* ── REPORT PANEL ────────────────────────────────────────────────────────── */
.report-panel {
  background: var(--surface);
  border: 1.5px solid rgba(129,140,248,0.35);
  border-radius: var(--radius);
  padding: 2rem 2.2rem;
  margin: 1rem 0;
  box-shadow: 0 0 40px rgba(129,140,248,0.08);
}
.report-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.report-label {
  font-size: 0.7rem; font-weight: 700; color: var(--accent2);
  letter-spacing: 0.14em; text-transform: uppercase;
}

/* ── DOWNLOAD BUTTON ─────────────────────────────────────────────────────── */
.stDownloadButton > button {
  background: transparent !important;
  border: 1.5px solid var(--accent2) !important;
  color: var(--accent2) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important; font-size: 0.85rem !important;
  border-radius: 10px !important;
  padding: 0.6rem 1.4rem !important;
  transition: all 0.25s ease !important;
  cursor: pointer !important;
}
.stDownloadButton > button:hover {
  background: rgba(129,140,248,0.12) !important;
  border-color: var(--accent2) !important;
  box-shadow: 0 0 20px rgba(129,140,248,0.2) !important;
  transform: translateY(-1px) !important;
}

/* ── FEEDBACK PANEL ──────────────────────────────────────────────────────── */
.feedback-panel {
  background: var(--surface);
  border: 1.5px solid rgba(52,211,153,0.3);
  border-radius: var(--radius);
  padding: 2rem 2.2rem;
  margin: 1rem 0;
  box-shadow: 0 0 40px rgba(52,211,153,0.06);
}
.feedback-label {
  font-size: 0.7rem; font-weight: 700; color: var(--accent3);
  letter-spacing: 0.14em; text-transform: uppercase;
  margin-bottom: 1.2rem; padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}

/* ── FLOW DIAGRAM PAGE ───────────────────────────────────────────────────── */
.flow-wrap {
  display: flex; flex-direction: column;
  align-items: center; gap: 0; padding: 2rem 1rem;
}
.flow-node {
  width: 220px;
  background: var(--surface);
  border: 1.5px solid var(--border2);
  border-radius: 14px;
  padding: 1.1rem 1.4rem;
  text-align: center;
  position: relative;
  transition: all 0.25s ease;
}
.flow-node:hover {
  border-color: var(--accent);
  box-shadow: 0 0 24px rgba(56,189,248,0.18);
  transform: scale(1.03);
}
.flow-node.user-node {
  border-color: rgba(244,114,182,0.4);
  background: rgba(244,114,182,0.07);
}
.flow-node.user-node:hover { border-color: var(--accent4); box-shadow: 0 0 24px rgba(244,114,182,0.18); }
.flow-node.output-node {
  border-color: rgba(52,211,153,0.4);
  background: rgba(52,211,153,0.07);
}
.flow-node.output-node:hover { border-color: var(--accent3); box-shadow: 0 0 24px rgba(52,211,153,0.18); }
.flow-node-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.flow-node-title { font-size: 0.9rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem; }
.flow-node-sub { font-size: 0.72rem; color: var(--muted2); line-height: 1.4; }
.flow-node-tag {
  display: inline-block; margin-top: 0.5rem;
  background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.2);
  color: var(--accent); font-size: 0.62rem;
  padding: 0.15rem 0.55rem; border-radius: 10px;
  font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
}

.flow-arrow {
  display: flex; flex-direction: column; align-items: center;
  gap: 0; padding: 0.3rem 0;
}
.flow-arrow-line {
  width: 2px; height: 28px;
  background: linear-gradient(180deg, var(--border2), var(--accent));
}
.flow-arrow-head {
  width: 0; height: 0;
  border-left: 7px solid transparent;
  border-right: 7px solid transparent;
  border-top: 10px solid var(--accent);
}
.flow-arrow-label {
  font-size: 0.65rem; color: var(--muted); letter-spacing: 0.08em;
  text-transform: uppercase; font-weight: 600; margin-top: 0.3rem;
}

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.site-footer {
  border-top: 1px solid var(--border);
  padding: 1.5rem 0 0.5rem;
  margin-top: 3rem;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 1rem;
}
.footer-left { font-size: 0.78rem; color: var(--muted2); line-height: 1.6; }
.footer-left strong { color: var(--accent); font-weight: 600; }
.footer-right {
  display: flex; gap: 0.5rem; flex-wrap: wrap;
}
.footer-tag {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 0.28rem 0.7rem;
  font-size: 0.68rem; color: var(--muted2);
  font-weight: 500; letter-spacing: 0.05em;
  transition: all 0.2s;
}
.footer-tag:hover { border-color: var(--border2); color: var(--text); }

/* ── DIVIDER ─────────────────────────────────────────────────────────────── */
.divider {
  height: 1px; margin: 1.5rem 0;
  background: linear-gradient(90deg, transparent, var(--border2), transparent);
}

/* ── SPINNER ─────────────────────────────────────────────────────────────── */
.stSpinner > div { color: var(--accent) !important; }

/* ── WARNING / INFO ──────────────────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; }

/* ── MOBILE ──────────────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .site-header { padding: 0.8rem 1rem; }
  .header-badges { display: none; }
  .hero { padding: 2rem 0.5rem 1.5rem; }
  .block-container { padding: 0 1rem 3rem !important; }
  .report-panel, .feedback-panel { padding: 1.3rem 1.2rem; }
  .site-footer { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for key in ("results", "running", "done", "active_tab"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else (False if key != "active_tab" else "research")

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-header">
  <div class="header-brand">
    <div class="header-title">🧠 Multi-Agent Research Assistant</div>
    <div class="header-sub">LangChain · LangGraph · Groq</div>
  </div>
  <div class="header-badges">
    <span class="badge">4 Agents</span>
    <span class="badge green">Completely Free</span>
    <span class="badge purple">LangGraph</span>
    <span class="badge purple">LangChain</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-kicker">Multi-Agent AI System · Live</div>
  <h1>Research at the speed<br>of <em>intelligence</em></h1>
  <p class="hero-stack">LangChain &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; Groq LLaMA 3.1 &nbsp;·&nbsp; DuckDuckGo</p>
</div>
""", unsafe_allow_html=True)

# ── TAB SWITCHER ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("Research Studio", use_container_width=True,
                 type="primary" if st.session_state.active_tab == "research" else "secondary"):
        st.session_state.active_tab = "research"
        st.rerun()
with col2:
    if st.button("Agent Flow Diagram", use_container_width=True,
                 type="primary" if st.session_state.active_tab == "flow" else "secondary"):
        st.session_state.active_tab = "flow"
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH ASSISTANCE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "research":

    # Input card
    st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:0.8rem;">📌 Write your research topic here</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "topic", label_visibility="collapsed",
        placeholder="e.g.  The future of renewable energy in 2030",
        key="topic_input"
    )

    # Example chips
    st.markdown("""
    <div class="chips-row">
      <span class="chip-label">Try:</span>
      <span class="chip">AI in Healthcare 2025</span>
      <span class="chip">Quantum Computing</span>
      <span class="chip">Pakistan Economy</span>
      <span class="chip">Space Exploration</span>
    </div>
    """, unsafe_allow_html=True)

    # Start button
    run_btn = st.button("Start Research Multi-Agent Pipeline", use_container_width=True)

    # ── Pipeline Cards ─────────────────────────────────────────────────────
    st.markdown('<div class="sec-heading">Multi-Agent Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results

    def card_state(step):
        if not r and not st.session_state.running:
            return "wait"
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "run" if k == step else "wait"
        return "wait"

    def render_card(num, icon, title, desc, step, key_name):
        cs = card_state(key_name)
        card_cls = {"run": "active", "done": "done"}.get(cs, "")
        status_html = {
            "wait": '<span class="p-status ps-wait">Waiting</span>',
            "run":  '<span class="p-status ps-run">● Running</span>',
            "done": '<span class="p-status ps-done">✓ Done</span>',
        }[cs]
        st.markdown(f"""
        <div class="p-card {card_cls}">
          <div class="p-card-top">
            <div style="display:flex;align-items:center;gap:0.6rem;">
              <div class="p-icon">{icon}</div>
              <span class="p-num">Agent {num}</span>
            </div>
            {status_html}
          </div>
          <div class="p-title">{title}</div>
          <div class="p-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        render_card("01", "🔍", "Search Agent",
                    "DuckDuckGo real-time web search - finds titles, URLs & snippets.", "search", "search")
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        render_card("03", "✍️", "Writer Agent",
                    "Drafts a structured report: Introduction, Findings, Conclusion & Sources.", "writer", "writer")
    with col_b:
        render_card("02", "📄", "Reader Agent",
                    "Selects the best URL and deep-scrapes full page content.", "reader", "reader")
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        render_card("04", "🧐", "Critic Agent",
                    "Reviews & scores the report out of 10, with strengths & improvements.", "critic", "critic")

    # ── Trigger pipeline ───────────────────────────────────────────────────
    if run_btn:
        if not topic.strip():
            st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
            st.warning("⚠️  Please enter a research topic first.")
        else:
            st.session_state.results = {}
            st.session_state.running = True
            st.session_state.done = False
            st.rerun()

    if st.session_state.running and not st.session_state.done:
        results = {}
        topic_val = st.session_state.topic_input
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

        with st.spinner("🔍  Agent 1 - Searching the web…"):
            # Direct tool call — no LLM loop, no waiting. Instant results.
            results["search"] = run_search(topic_val)
            st.session_state.results = dict(results)

        with st.spinner("📄  Agent 2 - Scraping top content…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    # FIX 1: Removed [:800] truncation — agent now sees ALL URLs
                    # FIX 2: Ask to scrape top 3 URLs, not just "the most relevant one"
                    f"Here are search results for the topic: '{topic_val}'\n\n"
                    f"Search Results:\n{results['search']}\n\n"
                    f"Please scrape the top 3 URLs from these results to get detailed content.")]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        with st.spinner("✍️  Agent 3 - Writing research report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = get_writer_chain().invoke({
                "topic": topic_val, "research": research_combined
            })
            st.session_state.results = dict(results)

        with st.spinner("🧐  Agent 4 - Reviewing & scoring…"):
            results["critic"] = get_critic_chain().invoke({"report": results["writer"]})
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    # ── Results ────────────────────────────────────────────────────────────
    r = st.session_state.results
    if r:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-heading">Results</div>', unsafe_allow_html=True)

        if "search" in r:
            with st.expander("🔍  Search Results  (Agent 1 output)", expanded=False):
                st.markdown(f'<div class="result-inner">{r["search"]}</div>', unsafe_allow_html=True)

        if "reader" in r:
            with st.expander("📄  Scraped Content  (Agent 2 output)", expanded=False):
                st.markdown(f'<div class="result-inner">{r["reader"]}</div>', unsafe_allow_html=True)

        if "writer" in r:
            st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:0.8rem;">Final Research Report</div>', unsafe_allow_html=True)
            st.markdown(r["writer"])

            st.download_button(
                label="Download Report (.md)",
                data=r["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        if "critic" in r:
            st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:0.8rem;">Critic Review & Score</div>', unsafe_allow_html=True)
            st.markdown(r["critic"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FLOW DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="sec-heading">Agent Pipeline - Flow Diagram</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.85rem;color:var(--muted2);margin-bottom:1.5rem;">Interactive diagram showing how the 4 agents collaborate to produce a research report. Hover over each node.</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="flow-wrap">

      <!-- USER -->
      <div class="flow-node user-node">
        <div class="flow-node-icon">👤</div>
        <div class="flow-node-title">User</div>
        <div class="flow-node-sub">Enters a research topic via the Streamlit interface</div>
      </div>

      <div class="flow-arrow">
        <div class="flow-arrow-line"></div>
        <div class="flow-arrow-head"></div>
        <div class="flow-arrow-label">topic query</div>
      </div>

      <!-- AGENT 1 -->
      <div class="flow-node">
        <div class="flow-node-icon">🔍</div>
        <div class="flow-node-title">Agent 1 - Search Agent</div>
        <div class="flow-node-sub">DuckDuckGo real-time web search<br>Returns titles, URLs & snippets</div>
        <span class="flow-node-tag">GROQ KEY 1 · LangGraph ReAct</span>
      </div>

      <div class="flow-arrow">
        <div class="flow-arrow-line"></div>
        <div class="flow-arrow-head"></div>
        <div class="flow-arrow-label">search results</div>
      </div>

      <!-- AGENT 2 -->
      <div class="flow-node">
        <div class="flow-node-icon">📄</div>
        <div class="flow-node-title">Agent 2 - Reader Agent</div>
        <div class="flow-node-sub">Picks best URL · Scrapes full page<br>trafilatura → readability → BS4</div>
        <span class="flow-node-tag">GROQ KEY 2 · LangGraph ReAct</span>
      </div>

      <div class="flow-arrow">
        <div class="flow-arrow-line"></div>
        <div class="flow-arrow-head"></div>
        <div class="flow-arrow-label">scraped content</div>
      </div>

      <!-- AGENT 3 -->
      <div class="flow-node">
        <div class="flow-node-icon">✍️</div>
        <div class="flow-node-title">Agent 3 - Writer Agent</div>
        <div class="flow-node-sub">Generates structured report<br>Introduction · Findings · Conclusion</div>
        <span class="flow-node-tag">GROQ KEY 3 · LangChain Chain</span>
      </div>

      <div class="flow-arrow">
        <div class="flow-arrow-line"></div>
        <div class="flow-arrow-head"></div>
        <div class="flow-arrow-label">draft report</div>
      </div>

      <!-- AGENT 4 -->
      <div class="flow-node">
        <div class="flow-node-icon">🧐</div>
        <div class="flow-node-title">Agent 4 - Critic Agent</div>
        <div class="flow-node-sub">Reviews · Scores out of 10<br>Strengths · Areas to improve</div>
        <span class="flow-node-tag">GROQ KEY 4 · LangChain Chain</span>
      </div>

      <div class="flow-arrow">
        <div class="flow-arrow-line"></div>
        <div class="flow-arrow-head"></div>
        <div class="flow-arrow-label">final output</div>
      </div>

      <!-- OUTPUT -->
      <div class="flow-node output-node">
        <div class="flow-node-icon">📊</div>
        <div class="flow-node-title">Final Output</div>
        <div class="flow-node-sub">Research Report + Score + Feedback<br>Downloadable as Markdown</div>
      </div>

    </div>

    <div style="margin-top:2rem;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.4rem 1.8rem;">
      <div style="font-size:0.72rem;font-weight:700;color:var(--accent);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem;">Tech Stack</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">LangGraph</span> -> ReAct agent execution loop</div>
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">LangChain</span> -> Prompts, tools & output parsers</div>
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">Groq</span> -> Free LLaMA 3.1 inference (4 keys)</div>
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">DuckDuckGo</span> -> Free real-time web search</div>
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">trafilatura</span> -> Primary content extractor</div>
        <div style="font-size:0.82rem;color:var(--muted2);"><span style="color:#fff;font-weight:600;">Streamlit</span> -> Interactive web interface</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
  <div class="footer-left">
    <strong>Multi-Agent Research Assistant</strong><br>
    Built with LangChain, LangGraph &amp; Groq · FAST-NUCES
  </div>
  <div class="footer-right">
    <span class="footer-tag">🔗 LangChain</span>
    <span class="footer-tag">🕸 LangGraph</span>
    <span class="footer-tag">⚡ Groq</span>
    <span class="footer-tag">🦆 DuckDuckGo</span>
    <span class="footer-tag">🐍 Python</span>
  </div>
</div>
""", unsafe_allow_html=True)