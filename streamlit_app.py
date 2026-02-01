import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO", page_icon="👨‍🍳", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN SÉCURISÉ POUR MOBILE ---
st.markdown("""
    <style>
    /* On cache le header et la sidebar qui buguent sur ton mobile */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    .main .block-container {padding-top: 1rem !important;}
    
    .recipe-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px;
        border: 1px solid #eee;
    }
    .stButton>button {
        width: 100%; border-radius: 10px; background-color: #FF4B4B; color: white;
        font-weight: 600; height: 3.5rem; border: none; margin-top: 10px;
    }
    .stSelectbox div[data-baseweb="select"] { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- CONNEXION ---
if not st.session_state.logged_in:
    st.title("👨‍🍳 GUSTO")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        if u and p:
            res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashlib.sha256(p.encode()).hexdigest()]})
            if res.text in ["SUCCESS", "CREATED"]:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
        else: st.warning("Remplis les champs !")
    st.stop()

# --- CHARGEMENT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        if 'Proprietaire' in df.columns:
            return df[df['Proprietaire'] == st.session_state.username]
        return df
    except: return pd.DataFrame()

df = load_data()

# --- MENU PRINCIPAL ---
st.write(f"Chef : **{st.session_state.username}**")
menu = st.selectbox("Menu :", ["🏠 Accueil", "📖 Mes Recettes", "⚙️ Gestion", "🛒 Courses", "🚪 Déconnexion"])

if menu == "🚪 Déconnexion":
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# --- PAGES ---
if menu == "🏠 Accueil":
    st.title("Salut ! ✨")
    col1, col2 = st.columns(2)
    col1.metric("Recettes", len(df))
    if st.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()

elif menu == "📖 Mes Recettes":
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        f = df[df['Nom'].str.contains(search, case=False, na=False)]
        for i, r in f.iterrows():
            st.markdown(f'<div class="recipe-card"><h3>{r["Nom"]}</h3><p>⏱️ {r["Temps"]}</p></div>', unsafe_allow_html=True)
            if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                st.image(r['Image'], use_container_width=True)
            with st.expander("Détails"):
                st.write("**Ingrédients :**", r['Ingredients'])
                st.write("**Préparation :**", r['Etapes'])

elif menu == "⚙️ Gestion":
    st.title("⚙️ Gestion")
    action = st.radio("Action :", ["Ajouter", "Modifier"])
    
    if action == "Ajouter":
        with st.form("add"):
            n = st.text_input("Nom")
            t = st.text_input("Temps")
            i = st.text_area("Ingrédients")
            e = st.text_area("Étapes")
            img = st.text_input("URL Image")
            if st.form_submit_button("SAUVEGARDER"):
                data = [n, t, 4, i, e, "Plat", 5, "Moyen", "Non", img, st.session_state.username]
                requests.post(WEB_APP_URL, json={"action": "add", "values": data})
                st.success("Ajouté !"); time.sleep(1); st.cache_data.clear(); st.rerun()
                
    elif action == "Modifier" and not df.empty:
        target = st.selectbox("Recette à changer", df['Nom'].tolist())
        r = df[df['Nom'] == target].iloc[0]
        with st.form("edit"):
            un = st.text_input("Nom", value=r['Nom'])
            ui = st.text_area("Ingrédients", value=r['Ingredients'])
            ue = st.text_area("Étapes", value=r['Etapes'])
            uimg = st.text_input("URL Image", value=r['Image'] if pd.notna(r['Image']) else "")
            if st.form_submit_button("METTRE À JOUR"):
                data = [un, r['Temps'], 4, ui, ue, r['Categorie'], 5, "Moyen", "Non", uimg, st.session_state.username]
                requests.post(WEB_APP_URL, json={"action": "edit", "values": data})
                st.success("Modifié !"); time.sleep(1); st.cache_data.clear(); st.rerun()

elif menu == "🛒 Courses":
    st.title("🛒 Liste")
    if not df.empty:
        choix = st.multiselect("Choisir les plats :", df['Nom'].tolist())
        if choix:
            l = []
            for c in choix:
                l.extend(str(df[df['Nom']==c]['Ingredients'].values[0]).split(','))
            for item in sorted(set(l)):
                st.checkbox(item.strip(), key=item)
