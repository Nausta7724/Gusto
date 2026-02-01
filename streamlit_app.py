import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(
    page_title="GUSTO VAULT", 
    page_icon="🔐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# TON URL DE SCRIPT
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN : CORRECTION TOTALE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }

    /* SUPPRESSION DU TEXTE BUGGÉ EN HAUT DU MENU */
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarNavItems"] { padding-top: 0px !important; }
    button[kind="header"] { display: none !important; }
    
    /* FIX POUR LES MOTS QUI REMPLACENT LES FLÈCHES */
    .st-emotion-cache-15433f4, .st-emotion-cache-6qob1r {
        display: none !important;
    }

    .stApp { background-color: #F8FAFC; }

    /* CARTES RECETTES OPTIMISÉES MOBILE */
    .recipe-card {
        background: white; 
        padding: 12px; 
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
        border: 1px solid #EDF2F7;
        margin-bottom: 15px;
    }

    /* FORCER LE CADRAGE MOBILE */
    @media (max-width: 640px) {
        .stMarkdown, .stImage, .stButton {
            width: 100% !important;
        }
        .recipe-card {
            margin-left: 0px !important;
            margin-right: 0px !important;
        }
    }

    .stButton>button {
        width: 100%; border-radius: 12px; background-color: #FF4B4B; color: white;
        font-weight: 600; border: none; height: 3.5rem; margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS SÉCURITÉ ---
def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.05, 0.9, 0.05])
    with c2:
        st.markdown("<h1 style='text-align: center;'>👨‍🍳 GUSTO</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter / S'inscrire"):
                if u and p:
                    try:
                        res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hash_pw(p)]}, timeout=15)
                        if res.text in ["SUCCESS", "CREATED"]:
                            st.session_state.logged_in = True
                            st.session_state.username = u
                            st.rerun()
                        else:
                            st.error("Identifiants incorrects.")
                    except:
                        st.error("Erreur serveur.")
                else:
                    st.warning("Champs requis.")
    st.stop()

# --- CHARGEMENT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        if 'Proprietaire' in df.columns:
            return df[df['Proprietaire'] == st.session_state.username]
        return df
    except: return pd.DataFrame()

def send_to_google(values, action="add"):
    try:
        payload = {"action": action, "values": values}
        response = requests.post(WEB_APP_URL, json=payload, timeout=15)
        return response.status_code == 200
    except: return False

df = load_data()

# --- SIDEBAR (SANS LE TEXTE BUGGÉ) ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#FF4B4B;'>Chef {st.session_state.username}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVIGATION", ["🏠 Accueil", "📖 Mon Livre", "⚙️ Gestion", "🛒 Courses"])
    st.markdown("---")
    st.subheader("⏱️ Minuteur")
    t_min = st.number_input("Minutes", 1, 180, 10)
    if st.button("🔔 Lancer"):
        st.toast(f"Top chrono : {t_min}min", icon="⏳")
    st.markdown("---")
    if st.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🚪 Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGES ---
if menu == "🏠 Accueil":
    st.title("Salut Chef ! ✨")
    if not df.empty:
        st.metric("Mes Recettes", len(df))
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h4>Suggestion : {r['Nom']}</h4><p>⏱️ {r['Temps']}</p></div>", unsafe_allow_html=True)
    else:
        st.info("Ajoute ta première recette dans 'Gestion' !")

elif menu == "📖 Mon Livre":
    st.title("Mes Recettes")
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        filtered = df[df['Nom'].str.contains(search, case=False, na=False)]
        for i, r in filtered.iterrows():
            with st.container():
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = r['Image'] if pd.notna(r.get('Image')) and str(r['Image']).startswith('http') else "https://via.placeholder.com/400x250?text=Gusto"
                st.image(img, use_container_width=True)
                st.subheader(r['Nom'])
                st.caption(f"⏱️ {r['Temps']} | 🍽️ {r['Categorie']}")
                with st.expander("Voir la préparation"):
                    st.write("**Ingrédients :**", r['Ingredients'])
                    st.write("**Étapes :**", r['Etapes'])
                st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Gestion":
    st.title("Gestion")
    t1, t2 = st.tabs(["➕ Ajouter", "✏️ Modifier"])
    with t1:
        with st.form("add"):
            n_nom = st.text_input("Nom *")
            n_temps = st.text_input("Temps")
            n_ing = st.text_area("Ingrédients")
            n_steps = st.text_area("Préparation")
            n_img = st.text_input("URL Image")
            n_cat = st.selectbox("Type", ["Plat", "Entrée", "Dessert"])
            if st.form_submit_button("Sauvegarder"):
                if n_nom:
                    data = [n_nom, n_temps, 4, n_ing, n_steps, n_cat, 5, "Moyen", "Non", n_img, st.session_state.username]
                    if send_to_google(data, "add"):
                        st.success("Enregistré !"); st.cache_data.clear(); time.sleep(1); st.rerun()
    with t2:
        if not df.empty:
            target = st.selectbox("Recette à modifier", df['Nom'].tolist())
            r = df[df['Nom'] == target].iloc[0]
            with st.form("edit"):
                u_nom = st.text_input("Nom", value=r['Nom'])
                u_ing = st.text_area("Ingrédients", value=r['Ingredients'])
                u_steps = st.text_area("Étapes", value=r['Etapes'])
                u_img = st.text_input("URL Image", value=r['Image'] if pd.notna(r['Image']) else "")
                if st.form_submit_button("Mettre à jour"):
                    data = [u_nom, r['Temps'], 4, u_ing, u_steps, r['Categorie'], 5, "Moyen", "Non", u_img, st.session_state.username]
                    if send_to_google(data, "edit"):
                        st.success("Mis à jour !"); st.cache_data.clear(); time.sleep(1); st.rerun()

elif menu == "🛒 Courses":
    st.title("Courses")
    if not df.empty:
        selection = st.multiselect("Plats choisis :", df['Nom'].tolist())
        if selection:
            ings = []
            for s in selection:
                ings.extend(str(df[df['Nom']==s]['Ingredients'].values[0]).split(','))
            for i in sorted(set(ings)):
                st.checkbox(i.strip(), key=f"c_{i}")
