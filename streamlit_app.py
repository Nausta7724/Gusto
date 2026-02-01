import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ULTIME ---
st.set_page_config(page_title="GUSTO NOCTUA", page_icon="🔥", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN "GLASSMORPHISM DARK" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Poppins:wght@300;400;600&display=swap');

    /* Masquage total des éléments natifs */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    
    /* Fond animé dégradé */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #000000);
        color: #f8fafc;
        font-family: 'Poppins', sans-serif;
    }

    /* Titre Cyberpunk */
    .cyber-title {
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 30px;
        filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.5));
    }

    /* Cartes effet Verre */
    .recipe-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Boutons Néon */
    .stButton>button {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 15px !important;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(79, 172, 254, 0.7);
    }

    /* Inputs stylisés */
    input, textarea, .stSelectbox {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-size: 1.2rem;
    }
    .stTabs [aria-selected="true"] {
        color: #00f2fe !important;
        border-bottom-color: #00f2fe !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br><div class='cyber-title'>GUSTO</div>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("CHEF ID", placeholder="Votre pseudo...")
        p = st.text_input("ACCESS CODE", type="password", placeholder="Votre code...")
        if st.button("INITIALISER LA CONNEXION"):
            if u and p:
                res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashlib.sha256(p.encode()).hexdigest()]})
                if res.text in ["SUCCESS", "CREATED"]:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
    st.stop()

# --- DATA ENGINE ---
@st.cache_data(ttl=1)
def load():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df[df['Proprietaire'] == st.session_state.username] if 'Proprietaire' in df.columns else df
    except: return pd.DataFrame()

df = load()

# --- INTERFACE PRINCIPALE ---
st.markdown("<div class='cyber-title'>GUSTO</div>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#00f2fe; letter-spacing:2px;'>SESSION: {st.session_state.username.upper()}</p>", unsafe_allow_html=True)

tabs = st.tabs(["🔥 DASH", "💎 GRIMOIRE", "🛠 CONFIG", "🛒 LIST", "🔒"])

with tabs[0]:
    st.markdown("### 📊 STATS")
    c1, c2 = st.columns(2)
    c1.metric("RECETTES", len(df))
    if st.button("🔄 SYNC DATA"):
        st.cache_data.clear()
        st.rerun()
    
    if not df.empty:
        st.markdown("### ⚡ SUGGESTION")
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h2 style='color:#00f2fe;'>{r['Nom']}</h2><p>{r['Temps']} • {r['Categorie']}</p></div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### 💎 VOS RECETTES")
    search = st.text_input("🔍 FILTRE TEMPOREL OU NOMINAL")
    if not df.empty:
        f = df[df['Nom'].str.contains(search, case=False, na=False)]
        for i, r in f.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='recipe-card'>
                    <h2 style='margin:0; color:#4facfe;'>{r['Nom']}</h2>
                    <p style='color:#94a3b8;'>{r['Categorie']} | {r['Temps']}</p>
                </div>
                """, unsafe_allow_html=True)
                if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                    st.image(r['Image'], use_container_width=True)
                with st.expander("🔑 ACCÉDER AUX DÉTAILS"):
                    st.markdown(f"**COMPOSANTS :**\\n{r['Ingredients']}")
                    st.markdown(f"**PROTOCOLE :**\\n{r['Etapes']}")

with tabs[2]:
    st.markdown("### 🛠 INJECTER UNE RECETTE")
    with st.form("inject"):
        n = st.text_input("NOM DU PLAT")
        t = st.text_input("TEMPS ESTIMÉ")
        cat = st.selectbox("CATÉGORIE", ["PLAT", "ENTRÉE", "DESSERT", "DRINK"])
        ing = st.text_area("INGRÉDIENTS")
        etp = st.text_area("PROTOCOLE DE PRÉPARATION")
        url = st.text_input("URL VISUELLE")
        if st.form_submit_button("VALIDER L'INJECTION"):
            data = [n, t, 4, ing, etp, cat, 5, "MOYEN", "NON", url, st.session_state.username]
            requests.post(WEB_APP_URL, json={"action": "add", "values": data})
            st.success("INJECTION RÉUSSIE"); time.sleep(1); st.cache_data.clear(); st.rerun()

with tabs[3]:
    st.markdown("### 🛒 LOGISTIQUE")
    if not df.empty:
        choix = st.multiselect("SÉLECTIONNER POUR LA LISTE", df['Nom'].tolist())
        if choix:
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            liste = []
            for c in choix:
                liste.extend(str(df[df['Nom']==c]['Ingredients'].values[0]).split(','))
            for item in sorted(set(liste)):
                st.checkbox(item.strip().upper(), key=f"L_{item}")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    if st.button("💀 FERMER LA SESSION"):
        st.session_state.logged_in = False
        st.rerun()
