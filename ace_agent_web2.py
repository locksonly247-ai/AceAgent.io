import streamlit as st
from datetime import datetime
import time
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Page config & styling (Claude-inspired clean & premium look)
st.set_page_config(page_title="ACE Agent v2", page_icon="🎾", layout="wide")

st.markdown("""
<style>
    .big-title { font-size: 2.2em; font-weight: bold; color: #00ff9d; }
    .match-card {
        background-color: #1f1f1f;
        padding: 18px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 6px solid #00ff9d;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .alert-box {
        background-color: #2a1f1f;
        padding: 14px;
        border-radius: 10px;
        border-left: 5px solid #ff5555;
        margin: 10px 0;
    }
    .watch-star { color: #ffd700; font-size: 1.4em; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🎾 ACE Agent v2 — Live Tennis Tracker</p>', unsafe_allow_html=True)
st.caption("Real scraping from Flashscore + smart fallback • Miami Open 2026 focus")

# Sidebar
with st.sidebar:
    st.header("Controls")
    refresh_sec = st.slider("Refresh interval (seconds)", 15, 60, 20)
    watch_input = st.text_input("Watchlist (comma-separated)", "Sinner, Alcaraz, Paul, Fils, Gauff, Zverev, Draper, Tiafoe, Sabalenka, Rybakina")
    watchlist = [p.strip().lower() for p in watch_input.split(",") if p.strip()]

if "last_scores" not in st.session_state:
    st.session_state.last_scores = {}
if "alerts" not in st.session_state:
    st.session_state.alerts = []

async def fetch_real_scores():
    """Try real scraping from Flashscore"""
    url = "https://www.flashscore.com/tennis/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    return parse_flashscore(html)
    except:
        return None

def parse_flashscore(html):
    soup = BeautifulSoup(html, "html.parser")
    matches = []
    for item in soup.select("div.event__match, div.event__item"):
        try:
            players = item.select("div.event__participant")
            if len(players) < 2: continue
            p1 = players[0].get_text(strip=True)
            p2 = players[1].get_text(strip=True)
            
            scores = item.select("div.event__score")
            s1 = scores[0].get_text(strip=True) if scores else "–"
            s2 = scores[1].get_text(strip=True) if len(scores) > 1 else "–"
            
            status_elem = item.select_one("div.event__time, div.event__status")
            status = status_elem.get_text(strip=True) if status_elem else "LIVE"
            
            mid = f"{p1[:12]}-{p2[:12]}"
            matches.append({
                "match_id": mid,
                "tournament": "Miami Open 2026",
                "player1": p1,
                "player2": p2,
                "score1": s1,
                "score2": s2,
                "status": status,
                "live": any(x in status.upper() for x in ["LIVE", "SET", "•"])
            })
        except:
            continue
    return matches[:12]

def get_fallback_matches():
    """Realistic simulation with slight random updates (Claude-style data feel)"""
    base = [
        {"id": "1", "p1": "F. Tiafoe", "p2": "J. Sinner", "s1": "4", "s2": "6", "status": "LIVE (Set 1)"},
        {"id": "2", "p1": "F. Cerundolo", "p2": "A. Zverev", "s1": "6", "s2": "7", "status": "LIVE (Set 2)"},
        {"id": "3", "p1": "C. Gauff", "p2": "K. Muchova", "s1": "3", "s2": "6", "status": "LIVE (Set 1)"},
        {"id": "4", "p1": "A. Sabalenka", "p2": "E. Rybakina", "s1": "6", "s2": "4", "status": "LIVE (Set 1)"},
    ]
    for m in base:
        if random.random() < 0.45:
            m["s1"] = str(int(m["s1"]) + random.randint(0, 1))
            m["s2"] = str(int(m["s2"]) + random.randint(0, 1))
    return base

placeholder = st.empty()
alert_placeholder = st.empty()

if st.button("🚀 Start Live Monitoring", type="primary"):
    st.success("ACE Agent active — attempting real Flashscore data + fallback simulation")
    
    while True:
        # Try real data first
        real_data = None
        try:
            real_data = asyncio.run(fetch_real_scores())
        except:
            pass
        
        matches = real_data if real_data and len(real_data) > 0 else get_fallback_matches()
        
        new_alerts = []
        for m in matches:
            mid = m.get("match_id") or m.get("id")
            key = f"{m.get('player1','')} vs {m.get('player2','')}"
            current = f"{m.get('score1','')}–{m.get('score2','')} | {m.get('status','')}"
            
            if mid in st.session_state.last_scores and st.session_state.last_scores[mid] != current:
                new_alerts.append(f"🚨 SCORE CHANGE — {key} → **{current}**")
            
            st.session_state.last_scores[mid] = current
        
        # Alerts section
        with alert_placeholder.container():
            if new_alerts or st.session_state.alerts:
                st.subheader("🛎️ Score Change Alerts")
                for alert in new_alerts + st.session_state.alerts[:8]:
                    st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)
                st.session_state.alerts = new_alerts + st.session_state.alerts[:8]
        
        # Main live display (clean cards like Claude summary)
        with placeholder.container():
            st.subheader(f"📊 LIVE MATCHES — {datetime.now().strftime('%H:%M:%S')} | Miami Open 2026")
            for m in matches:
                watched = any(w in (m.get("player1","") + m.get("player2","")).lower() for w in watchlist)
                prefix = '<span class="watch-star">⭐</span> ' if watched else "• "
                st.markdown(f"""
                <div class="match-card">
                    {prefix}<strong>{m.get('player1','')}</strong> vs <strong>{m.get('player2','')}</strong><br>
                    <strong>Score:</strong> {m.get('score1','')} – {m.get('score2','')} | {m.get('status','')}
                </div>
                """, unsafe_allow_html=True)
        
        time.sleep(refresh_sec)
        st.rerun()

else:
    st.info("👆 Click **Start Live Monitoring** to begin. Real scraping runs first; realistic simulation kicks in automatically if needed.")

st.caption("ACE Agent v2 • Real scraping + smart fallback • Enhanced visuals inspired by original Claude artifact")
