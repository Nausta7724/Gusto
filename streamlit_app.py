import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO NOCTUA", page_icon="🔥", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN CORRIGÉ (TEXTE VISIBLE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Poppins:wght@300;400;600&display=swap');

    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #000000);
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }

    .cyber-title {
        font-family: 'Syncopate', sans-serif;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.6));
    }

    /* --- CORRECTION DES INPUTS (L'ENFER DU BLANC SUR BLANC) --- */
    input, textarea {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #4facfe !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    
    /* Pour le texte à l'intérieur des cases d'écriture */
    div[data-baseweb="input"] {
        background-color: #000000 !important;
        border-radius: 10px !important;
    }
    
    /* Correction de la couleur du texte saisi */
    input[type="text"], input[type="password"], textarea {
        -webkit-text-fill-color: #ffffff !important;
    }

    .recipe-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .stButton>button {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        height: 3.5rem;
        width: 100%;
        border: none;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<br><br><div class='cyber-title'>GUSTO</div>", unsafe_allow_html=True)
    u = st.text_input("CHEF ID")
    p = st.text_input("ACCESS CODE", type="password")
    if st.button("INITIALISER LA CONNEXION"):
        if u and p:
            res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashlib.sha256(p.encode()).hexdigest()]})
            if res.text in ["SUCCESS", "CREATED"]:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
    st.stop()

# --- DATA ---
@st.cache_data(ttl=1)
def load():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df[df['Proprietaire'] == st.session_state.username] if 'Proprietaire' in df.columns else df
    except: return pd.DataFrame()

df = load()

# --- MAIN APP ---
st.markdown("<div class='cyber-title'>GUSTO</div>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#00f2fe;'>SESSION ACTIVE: {st.session_state.username.upper()}</p>", unsafe_allow_html=True)

tabs = st.tabs(["📊 DASH", "💎 GRIMOIRE", "🛠 CONFIG", "🛒 LIST"])

with tabs[0]:
    st.metric("RECETTES ENREGISTRÉES", len(df))
    if st.button("🔄 SYNCHRONISATION"):
        st.cache_data.clear()
        st.rerun()
    if not df.empty:
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h3>Suggestion: {r['Nom']}</h3><p>{r['Temps']}</p></div>", unsafe_allow_html=True)

with tabs[1]:
    search = st.text_input("🔍 RECHERCHER")
    if not df.empty:
        for i, r in df[df['Nom'].str.contains(search, case=False, na=False)].iterrows():
            st.markdown(f"<div class='recipe-card'><h2>{r['Nom']}</h2><p>{r['Categorie']} | {r['Temps']}</p></div>", unsafe_allow_html=True)
            if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                st.image(r['Image'], use_container_width=True)
            with st.expander("OUVRIR LE PROTOCOLE"):
                st.write(r['Ingredients'])
                st.write(r['Etapes'])

with tabs[2]:
    with st.form("add_new"):
        n = st.text_input("NOM DU PLAT")
        t = st.text_input("TEMPS")
        i = st.text_area("INGRÉDIENTS")
        e = st.text_area("ÉTAPES")
        img = st.text_input("URL IMAGE")
        if st.form_submit_button("INJECTER DANS LE CLOUD"):
            data = [n, t, 4, i, e, "PLAT", 5, "MOYEN", "NON", img, st.session_state.username]
            requests.post(WEB_APP_URL, json={"action": "add", "values": data})
            st.success("INJECTION TERMINÉE"); time.sleep(1); st.cache_data.clear(); st.rerun()

with tabs[3]:
    if not df.empty:
        choix = st.multiselect("SÉLECTIONNER", df['Nom'].tolist())
        if choix:
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            for c in choix:
                st.write(f"🛒 **{c}**")
                st.write(df[df['Nom']==c]['Ingredients'].values[0])
            st.markdown("</div>", unsafe_allow_html=True)

if st.button("🚪 DÉCONNEXION"):
    st.session_state.logged_in = False
    st.rerun()
