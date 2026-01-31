import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO VAULT", page_icon="🔐", layout="wide")

# TON NOUVEAU LIEN SCRIPT (Mis à jour)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN ---
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
    .login-box {
        max-width: 400px; margin: auto; padding: 40px;
        background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
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
    with st.container():
        st.markdown("<h1 style='text-align: center;'>👨‍🍳 GUSTO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Connectez-vous pour accéder à votre grimoire personnel</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.form("login_form"):
                u = st.text_input("Identifiant")
                p = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter / S'inscrire")
                
                if submit:
                    if u and p:
                        with st.spinner("Vérification..."):
                            try:
                                res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hash_pw(p)]})
                                if res.text in ["SUCCESS", "CREATED"]:
                                    st.session_state.logged_in = True
                                    st.session_state.username = u
                                    st.success(f"Bienvenue Chef {u} !")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Identifiants incorrects.")
                            except:
                                st.error("Erreur de connexion au serveur.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")
    st.stop()

# --- SI CONNECTÉ : CHARGEMENT & FILTRAGE ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        # On ne garde que les recettes de l'utilisateur (Colonne K / 'Proprietaire')
        if 'Proprietaire' in df.columns:
            return df[df['Proprietaire'] == st.session_state.username]
        return df
    except: return pd.DataFrame()

def send_to_google(values, action="add"):
    try:
        payload = {"action": action, "values": values}
        response = requests.post(WEB_APP_URL, json=payload)
        return response.status_code == 200
    except: return False

df = load_data()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown(f"### 👨‍🍳 Chef : {st.session_state.username}")
    menu = st.radio("NAVIGATION", ["🏠 Accueil", "📖 Mon Livre", "⚙️ Gestion", "🛒 Courses"])
    
    st.markdown("---")
    st.subheader("⏱️ Minuteur")
    t_min = st.number_input("Minutes", 1, 180, 10)
    if st.button("🔔 Lancer"):
        st.toast(f"Chrono lancé : {t_min}min", icon="⏳")
    
    if st.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()
        
    if st.button("🚪 Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGES ---

if menu == "🏠 Accueil":
    st.title(f"Bienvenue, {st.session_state.username} ! ✨")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mes Recettes", len(df))
    if not df.empty:
        st.markdown("### 💡 Idée du jour")
        r = df.sample(1).iloc[0]
        st.markdown(f"<div class='recipe-card'><h2>{r['Nom']}</h2><p>⏱️ {r['Temps']}</p></div>", unsafe_allow_html=True)

elif menu == "📖 Mon Livre":
    st.title("📖 Mon Grimoire")
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
                    st.write(f"**Temps :** {r['Temps']} | **Catégorie :** {r['Categorie']}")
                    with st.expander("Détails"):
                        st.write("**Ingrédients :**", r['Ingredients'])
                        st.write("**Préparation :**", r['Etapes'])
                st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Gestion":
    st.title("⚙️ Gérer mes Recettes")
    t1, t2 = st.tabs(["➕ Ajouter", "✏️ Modifier"])
    
    with t1:
        with st.form("add"):
            n_nom = st.text_input("Nom *")
            n_temps = st.text_input("Temps")
            n_ing = st.text_area("Ingrédients")
            n_steps = st.text_area("Préparation")
            n_img = st.text_input("Lien Image")
            n_cat = st.selectbox("Type", ["Plat", "Entrée", "Dessert"])
            if st.form_submit_button("Sauvegarder"):
                if n_nom and n_ing:
                    # Ordre Colonnes: Nom, Temps, Pers, Ing, Steps, Cat, Note, Diff, Fav, Img, Proprietaire
                    data = [n_nom, n_temps, 4, n_ing, n_steps, n_cat, 5, "Moyen", "Non", n_img, st.session_state.username]
                    if send_to_google(data, "add"):
                        st.success("Ajouté !"); st.cache_data.clear(); time.sleep(1); st.rerun()

    with t2:
        if not df.empty:
            target = st.selectbox("Recette à modifier", df['Nom'].tolist())
            r = df[df['Nom'] == target].iloc[0]
            with st.form("edit"):
                u_nom = st.text_input("Nom", value=r['Nom'])
                u_ing = st.text_area("Ingrédients", value=r['Ingredients'])
                u_steps = st.text_area("Préparation", value=r['Etapes'])
                u_img = st.text_input("Image", value=r['Image'] if pd.notna(r['Image']) else "")
                if st.form_submit_button("Mettre à jour"):
                    data = [u_nom, r['Temps'], 4, u_ing, u_steps, r['Categorie'], 5, "Moyen", "Non", u_img, st.session_state.username]
                    if send_to_google(data, "edit"):
                        st.success("Modifié !"); st.cache_data.clear(); time.sleep(1); st.rerun()

elif menu == "🛒 Courses":
    st.title("🛒 Ma Liste")
    if not df.empty:
        selection = st.multiselect("Recettes :", df['Nom'].tolist())
        if selection:
            ings = []
            for s in selection:
                ings.extend(str(df[df['Nom']==s]['Ingredients'].values[0]).split(','))
            for i in sorted(set(ings)):
                st.checkbox(i.strip())
