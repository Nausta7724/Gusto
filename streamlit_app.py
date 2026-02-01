import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO OVERDRIVE", page_icon="⚡", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN "OVERDRIVE" (INTERFACE REMPLIE & DYNAMIQUE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');

    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0f0f1b 100%);
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }

    .glitch-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.4));
    }

    /* Cartes Statistiques */
    .stat-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Grille de Recettes */
    .recipe-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .recipe-header {
        border-left: 4px solid #00d2ff;
        padding-left: 15px;
        margin-bottom: 15px;
    }

    /* Inputs High-Contrast */
    input, textarea, .stSelectbox {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #3a7bd5 !important;
        border-radius: 8px !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        height: 3.5rem;
        transition: 0.3s;
    }
    
    /* Etiquettes Ingrédients */
    .ing-tag {
        display: inline-block;
        background: rgba(0, 210, 255, 0.1);
        color: #00d2ff;
        padding: 4px 10px;
        border-radius: 5px;
        margin: 3px;
        font-size: 0.9rem;
        border: 1px solid rgba(0, 210, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<br><div class='glitch-title'>GUSTO</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>SYSTEM LOGIN REQUIRED</p>", unsafe_allow_html=True)
    u = st.text_input("USER_ID")
    p = st.text_input("PASSWORD", type="password")
    if st.button("EXECUTE"):
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

# --- UI PRINCIPALE ---
st.markdown("<div class='glitch-title'>GUSTO</div>", unsafe_allow_html=True)

tabs = st.tabs(["📡 HUB", "📂 ARCHIVES", "⚙️ CORE", "📦 CARGO"])

with tabs[0]:
    st.markdown("### 🖥️ DASHBOARD STATUS")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='stat-box'><small>RECETTES</small><br><b style='color:#00d2ff; font-size:1.5rem;'>{len(df)}</b></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='stat-box'><small>CHEF</small><br><b style='color:#00d2ff; font-size:1.2rem;'>{st.session_state.username[:8]}</b></div>", unsafe_allow_html=True)
    if c3.button("SYNC"):
        st.cache_data.clear()
        st.rerun()

    if not df.empty:
        st.markdown("---")
        st.markdown("### 🎯 SUGGESTION DU JOUR")
        r = df.sample(1).iloc[0]
        st.markdown(f"""
        <div class='recipe-card'>
            <div class='recipe-header'>
                <h2 style='margin:0; color:#00d2ff;'>{r['Nom']}</h2>
                <span>⏱️ {r['Temps']} | 💠 {r['Categorie']}</span>
            </div>
            <p style='color:#888;'>Prêt pour une nouvelle expérience culinaire ?</p>
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### 📂 BASE DE DONNÉES")
    search = st.text_input("🔍 FILTRER L'ARCHIVE...")
    
    if not df.empty:
        f = df[df['Nom'].str.contains(search, case=False, na=False)]
        for i, r in f.iterrows():
            st.markdown(f"""
            <div class='recipe-card'>
                <div class='recipe-header'>
                    <h2 style='margin:0; color:#00d2ff;'>{r['Nom']}</h2>
                    <span style='font-size:0.8rem; color:#aaa;'>ID: {i} | {r['Categorie']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                st.image(r['Image'], use_container_width=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**🧪 INGRÉDIENTS**")
                for ing in str(r['Ingredients']).split(','):
                    st.markdown(f"<span class='ing-tag'>{ing.strip()}</span>", unsafe_allow_html=True)
            with col_b:
                st.markdown("**📜 PROTOCOLE**")
                st.write(r['Etapes'][:100] + "...")
            
            with st.expander("DÉPLOYER LA FICHE COMPLÈTE"):
                st.write(r['Etapes'])
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("### ⚙️ UNITÉ DE PRODUCTION")
    action = st.radio("OPÉRATION", ["AJOUTER", "MODIFIER"], horizontal=True)
    
    with st.container():
        if action == "AJOUTER":
            with st.form("add_form"):
                n = st.text_input("NOM DU PRODUIT")
                t = st.text_input("TEMPS DE CYCLE")
                cat = st.selectbox("CLASSE", ["Plat", "Entrée", "Dessert", "Boisson"])
                i = st.text_area("COMPOSANTS (séparés par des virgules)")
                e = st.text_area("INSTRUCTIONS DE MONTAGE")
                img = st.text_input("URL VISUELLE (JPG/PNG)")
                if st.form_submit_button("INJECTER DANS LE SYSTÈME"):
                    if n:
                        data = [n, t, 4, i, e, cat, 5, "Moyen", "Non", img, st.session_state.username]
                        requests.post(WEB_APP_URL, json={"action": "add", "values": data})
                        st.success("INJECTION TERMINÉE"); time.sleep(1); st.cache_data.clear(); st.rerun()
        
        elif action == "MODIFIER" and not df.empty:
            target = st.selectbox("CHOISIR L'UNITÉ", df['Nom'].tolist())
            r = df[df['Nom'] == target].iloc[0]
            with st.form("edit_form"):
                un = st.text_input("NOM", value=r['Nom'])
                ui = st.text_area("INGRÉDIENTS", value=r['Ingredients'])
                ue = st.text_area("ÉTAPES", value=r['Etapes'])
                uimg = st.text_input("URL IMAGE", value=r['Image'] if pd.notna(r['Image']) else "")
                if st.form_submit_button("MISE À JOUR DU CORE"):
                    data = [un, r['Temps'], 4, ui, ue, r['Categorie'], 5, "Moyen", "Non", uimg, st.session_state.username]
                    requests.post(WEB_APP_URL, json={"action": "edit", "values": data})
                    st.success("CORE UPDATED"); time.sleep(1); st.cache_data.clear(); st.rerun()

with tabs[3]:
    st.markdown("### 📦 CARGO / LOGISTIQUE")
    if not df.empty:
        choix = st.multiselect("SÉLECTIONNER LES UNITÉS", df['Nom'].tolist())
        if choix:
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            for c in choix:
                st.markdown(f"**⚡ SOURCE : {c}**")
                ings = str(df[df['Nom']==c]['Ingredients'].values[0]).split(',')
                for item in ings:
                    st.checkbox(item.strip(), key=f"{c}_{item}")
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.button("EXIT SYSTEM"):
    st.session_state.logged_in = False
    st.rerun()
