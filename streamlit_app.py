import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO VAULT", page_icon="🔐", layout="wide")

# TON URL DE SCRIPT MISE À JOUR
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN & POLICE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    .recipe-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #EDF2F7;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; background-color: #FF4B4B; color: white;
        font-weight: 600; border: none; height: 3rem;
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
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>👨‍🍳 GUSTO</h1>", unsafe_allow_html=True)
        st.info("Identifiez-vous pour accéder à vos recettes.")
        with st.form("login_form"):
            u = st.text_input("Identifiant (Pseudo)")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter / S'inscrire"):
                if u and p:
                    try:
                        # Test de connexion au script Google
                        res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hash_pw(p)]}, timeout=10)
                        if res.text in ["SUCCESS", "CREATED"]:
                            st.session_state.logged_in = True
                            st.session_state.username = u
                            st.success(f"Bienvenue Chef {u} !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Identifiants incorrects ou erreur serveur.")
                    except Exception as e:
                        st.error(f"Erreur de connexion : Vérifiez que le script Google est déployé sur 'Tout le monde'.")
                else:
                    st.warning("Remplissez tous les champs.")
    st.stop()

# --- SI CONNECTÉ : CHARGEMENT & FILTRAGE ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        # Filtrage par colonne K (Proprietaire)
        if 'Proprietaire' in df.columns:
            return df[df['Proprietaire'] == st.session_state.username]
        return df
    except: return pd.DataFrame()

def send_to_google(values, action="add"):
    try:
        payload = {"action": action, "values": values}
        response = requests.post(WEB_APP_URL, json=payload, timeout=10)
        return response.status_code == 200
    except: return False

df = load_data()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown(f"### 👨‍🍳 Chef : {st.session_state.username}")
    menu = st.radio("MENU", ["🏠 Accueil", "📖 Mon Livre", "⚙️ Gestion", "🛒 Courses"])
    st.markdown("---")
    st.subheader("⏱️ Minuteur")
    t_min = st.number_input("Minutes", 1, 180, 10)
    if st.button("🔔 Lancer"):
        st.toast(f"Chrono : {t_min}min", icon="⏳")
    if st.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🚪 Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGES ---

if menu == "🏠 Accueil":
    st.title("Tableau de bord")
    if not df.empty:
        st.metric("Mes Recettes", len(df))
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h3>Suggestion : {r['Nom']}</h3><p>⏱️ {r['Temps']}</p></div>", unsafe_allow_html=True)
    else:
        st.write("Votre livre est vide. Allez dans 'Gestion' pour ajouter votre première recette !")

elif menu == "📖 Mon Livre":
    st.title("Mes Recettes")
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        filtered = df[df['Nom'].str.contains(search, case=False, na=False)]
        for i, r in filtered.iterrows():
            with st.container():
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    img = r['Image'] if pd.notna(r.get('Image')) else "https://via.placeholder.com/300"
                    st.image(img, use_container_width=True)
                with c2:
                    st.header(r['Nom'])
                    st.write(f"⏱️ {r['Temps']} | 🍽️ {r['Categorie']}")
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
            n_ing = st.text_area("Ingrédients (séparés par des virgules)")
            n_steps = st.text_area("Préparation")
            n_img = st.text_input("URL Image")
            n_cat = st.selectbox("Type", ["Plat", "Entrée", "Dessert"])
            if st.form_submit_button("Enregistrer"):
                if n_nom:
                    # Colonnes A à K (11 colonnes)
                    data = [n_nom, n_temps, 4, n_ing, n_steps, n_cat, 5, "Moyen", "Non", n_img, st.session_state.username]
                    if send_to_google(data, "add"):
                        st.success("Recette enregistrée !"); st.cache_data.clear(); time.sleep(1); st.rerun()

    with t2:
        if not df.empty:
            target = st.selectbox("Choisir une recette", df['Nom'].tolist())
            r = df[df['Nom'] == target].iloc[0]
            with st.form("edit"):
                u_nom = st.text_input("Nom", value=r['Nom'])
                u_ing = st.text_area("Ingrédients", value=r['Ingredients'])
                u_steps = st.text_area("Préparation", value=r['Etapes'])
                u_img = st.text_input("URL Image", value=r['Image'] if pd.notna(r['Image']) else "")
                if st.form_submit_button("Mettre à jour"):
                    data = [u_nom, r['Temps'], 4, u_ing, u_steps, r['Categorie'], 5, "Moyen", "Non", u_img, st.session_state.username]
                    if send_to_google(data, "edit"):
                        st.success("Mise à jour réussie !"); st.cache_data.clear(); time.sleep(1); st.rerun()

elif menu == "🛒 Courses":
    st.title("Courses")
    if not df.empty:
        selection = st.multiselect("Recettes pour la liste :", df['Nom'].tolist())
        if selection:
            ings = []
            for s in selection:
                ings.extend(str(df[df['Nom']==s]['Ingredients'].values[0]).split(','))
            for i in sorted(set(ings)):
                st.checkbox(i.strip(), key=i)
