import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO ARTISAN", page_icon="🥘", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN CUSTOM "HIGH-COLOR" ---
st.markdown("""
    <style>
    /* Masquage des éléments par défaut */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    
    /* Fond de l'application */
    .stApp {
        background: linear-gradient(180deg, #FFF5F0 0%, #FFFFFF 100%);
    }

    /* Carte de recette stylisée */
    .recipe-card {
        background: white;
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 25px;
        border: none;
        box-shadow: 0 15px 35px rgba(255, 75, 43, 0.08);
        border-left: 8px solid #FF4B2B;
    }

    /* Style des titres */
    h1 {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #FF4B2B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3rem !important;
        text-align: center;
    }

    /* Boutons de navigation (Tabs personnalisés) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: white;
        border-radius: 12px;
        border: 1px solid #FF4B2B;
        color: #FF4B2B;
        font-weight: 600;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B2B !important;
        color: white !important;
    }

    /* Bouton d'action principal */
    .stButton>button {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF8E53 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 15px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 20px rgba(255, 75, 43, 0.2);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(255, 75, 43, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<br><br><h1>GUSTO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Entrez dans votre atelier culinaire</p>", unsafe_allow_html=True)
    u = st.text_input("Identifiant", key="user_in")
    p = st.text_input("Mot de passe", type="password", key="pass_in")
    if st.button("DÉMARRER LA CUISINE"):
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

# --- HEADER ---
st.markdown(f"<h1>GUSTO</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>Chef : <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)

# --- NAVIGATION PAR ONGLETS (VRAIE APP) ---
tab_home, tab_book, tab_add, tab_shop, tab_out = st.tabs(["🏠", "📖 Recettes", "➕ Créer", "🛒 Courses", "🚪"])

with tab_home:
    st.markdown("### 🌟 Tableau de Bord")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div style='background:white; padding:20px; border-radius:20px; text-align:center; border:1px solid #eee;'><h3>{len(df)}</h3>Recettes</div>", unsafe_allow_html=True)
    with c2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    if not df.empty:
        st.markdown("### 👨‍🍳 Inspiration")
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h3>{r['Nom']}</h3><p>{r['Temps']} • {r['Categorie']}</p></div>", unsafe_allow_html=True)

with tab_book:
    st.markdown("### 📖 Mon Grimoire")
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        for i, r in df[df['Nom'].str.contains(search, case=False, na=False)].iterrows():
            st.markdown(f"""
            <div class='recipe-card'>
                <h2 style='color:#2D3436; margin:0;'>{r['Nom']}</h2>
                <p style='color:#FF4B2B; font-weight:bold;'>{r['Categorie']} • {r['Temps']}</p>
            </div>
            """, unsafe_allow_html=True)
            if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                st.image(r['Image'], use_container_width=True)
            with st.expander("📝 Voir la méthode"):
                st.markdown(f"**Ingrédients :**\\n{r['Ingredients']}")
                st.markdown(f"**Préparation :**\\n{r['Etapes']}")

with tab_add:
    st.markdown("### ➕ Nouvelle Création")
    with st.form("new_artisan"):
        n = st.text_input("Nom du plat")
        t = st.text_input("Temps")
        cat = st.selectbox("Type", ["Plat", "Entrée", "Dessert", "Boisson"])
        ing = st.text_area("Ingrédients (virgules entre chaque)")
        etp = st.text_area("Préparation")
        url = st.text_input("Lien Image")
        if st.form_submit_button("PUBLIER LA RECETTE"):
            data = [n, t, 4, ing, etp, cat, 5, "Moyen", "Non", url, st.session_state.username]
            requests.post(WEB_APP_URL, json={"action": "add", "values": data})
            st.success("Enregistré avec succès !"); time.sleep(1); st.cache_data.clear(); st.rerun()

with tab_shop:
    st.markdown("### 🛒 Liste Automatique")
    if not df.empty:
        choix = st.multiselect("Qu'est-ce qu'on mange ?", df['Nom'].tolist())
        if choix:
            liste = []
            for c in choix:
                liste.extend(str(df[df['Nom']==c]['Ingredients'].values[0]).split(','))
            st.markdown("<div style='background:white; padding:15px; border-radius:15px;'>", unsafe_allow_html=True)
            for item in sorted(set(liste)):
                st.checkbox(item.strip(), key=f"s_{item}")
            st.markdown("</div>", unsafe_allow_html=True)

with tab_out:
    st.markdown("### 🚪 Quitter")
    if st.button("DÉCONNEXION"):
        st.session_state.logged_in = False
        st.rerun()
