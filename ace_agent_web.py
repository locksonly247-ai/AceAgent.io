import streamlit as st
from datetime import datetime
import time
import random

# Page setup
st.set_page_config(page_title="ACE Agent v2 - Live Tennis", page_icon="🎾", layout="wide")
st.title("🎾 ACE Agent v2 - Live Tennis Scores")
st.markdown("**Real-time simulation** • Auto-refresh • Watch your favorite players")

# Sidebar
with st.sidebar:
    st.header("Controls")
    refresh_sec = st.slider("Refresh every (seconds)", 10, 60, 20)
    watch_input = st.text_input("Watchlist players (comma separated)", "Sinner, Alcaraz, Paul, Fils, Gauff, Zverev")
    watchlist = [p.strip().lower() for p in watch_input.split(",") if p.strip()]

# Persistent state
if "last_matches" not in st.session_state:
    st.session_state.last_matches = {}
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Realistic simulated matches (updates randomly)
def get_live_matches():
    base_matches = [
        {"id": "1", "p1": "T. Paul", "p2": "A. Fils", "s1": "6", "s2": "7", "status": "LIVE (Set 2)"},
        {"id": "2", "p1": "J. Lehecka", "p2": "M. Landaluce", "s1": "7", "s2": "5", "status": "LIVE (Set 2)"},
        {"id": "3", "p1": "J. Sinner", "p2": "F. Tiafoe", "s1": "6", "s2": "4", "status": "LIVE (Set 1)"},
        {"id": "4", "p1": "C. Gauff", "p2": "Opponent", "s1": "4", "s2": "6", "status": "LIVE (Set 2)"},
    ]
    
    # Add some random score changes
    for m in base_matches:
        if random.random() < 0.4:  # 40% chance to change score
            m["s1"] = str(int(m["s1"]) + random.randint(0,1))
            m["s2"] = str(int(m["s2"]) + random.randint(0,1))
    
    return base_matches

# Main update
placeholder = st.empty()
alert_col = st.empty()

if st.button("🚀 Start Live Monitoring", type="primary"):
    st.info(f"Monitoring started — refreshing every {refresh_sec} seconds")
    
    while True:
        matches = get_live_matches()
        new_alerts = []
        
        for m in matches:
            mid = m["id"]
            current = f"{m['p1']} {m['s1']}-{m['s2']} {m['status']}"
            
            if mid in st.session_state.last_matches:
                if st.session_state.last_matches[mid] != current:
                    new_alerts.append(f"🚨 **Score change!** {m['p1']} vs {m['p2']} → **{m['s1']}-{m['s2']}** ({m['status']})")
            
            st.session_state.last_matches[mid] = current
        
        # Show alerts
        with alert_col.container():
            if new_alerts or st.session_state.alerts:
                st.subheader("Recent Alerts")
                for a in new_alerts + st.session_state.alerts[:5]:
                    st.info(a)
                st.session_state.alerts = new_alerts + st.session_state.alerts[:5]
        
        # Show live table
        with placeholder.container():
            st.subheader(f"📊 Live Matches — {datetime.now().strftime('%H:%M:%S')}")
            for m in matches:
                is_watched = any(w in (m["p1"] + m["p2"]).lower() for w in watchlist)
                prefix = "⭐ " if is_watched else "• "
                st.markdown(f"{prefix}**{m['p1']}** vs **{m['p2']}** **{m['s1']} - {m['s2']}** {m['status']}")
        
        time.sleep(refresh_sec)
        st.rerun()

else:
    st.info("👆 Click **Start Live Monitoring** to begin tracking tennis matches.")

st.caption("ACE Agent v2 • Pure simulation mode (no external dependencies) • Built for ATP Picks")
