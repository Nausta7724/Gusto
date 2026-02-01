import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO", page_icon="🍳", layout="centered")

# LIENS (Ne pas modifier)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN PROFESSIONNEL ---
st.markdown("""
    <style>
    /* Suppression des éléments inutiles */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    
    /* Fond de l'écran */
    .stApp {
        background-color: #F4F7F9;
        color: #1A1A1A;
    }

    /* Titre Principal */
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #E63946;
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    /* Cartes Recettes */
    .recipe-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #EAEAEA;
    }

    /* Badges de couleur */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        background-color: #F1FAEE;
        color: #1D3557;
        margin-bottom: 10px;
    }

    /* Champs d'écriture (Correction contraste) */
    input, textarea {
        background-color: white !important;
        color: #1A1A1A !important;
        border: 1px solid #CCC !important;
        border-radius: 8px !important;
    }

    /* Bouton principal */
    .stButton>button {
        width: 100%;
        background-color: #E63946;
        color: white !important;
        border: none;
        border-radius: 10px;
        height: 3.5rem;
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>GUSTO</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Votre carnet de recettes personnel</p>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Nom d'utilisateur")
        p = st.text_input("Mot de passe", type="password")
        if st.button("SE CONNECTER"):
            if u and p:
                res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashlib.sha256(p.encode()).hexdigest()]})
                if res.text in ["SUCCESS", "CREATED"]:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
            else: st.warning("Veuillez remplir les deux cases.")
    st.stop()

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=1)
def charger_donnees():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df[df['Proprietaire'] == st.session_state.username] if 'Proprietaire' in df.columns else df
    except: return pd.DataFrame()

df = charger_donnees()

# --- INTERFACE PRINCIPALE ---
st.markdown("<div class='main-title'>GUSTO</div>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#457B9D;'>Chef : <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)

# Barre de navigation simple
menu = st.tabs(["🏠 Accueil", "📖 Mes Recettes", "➕ Ajouter", "🛒 Courses"])

# --- ONGLET ACCUEIL ---
with menu[0]:
    st.subheader("Résumé de votre cuisine")
    col1, col2 = st.columns(2)
    col1.metric("Recettes totales", len(df))
    if col2.button("Actualiser 🔄"):
        st.cache_data.clear()
        st.rerun()
    
    if not df.empty:
        st.markdown("---")
        st.write("💡 **Suggestion pour aujourd'hui :**")
        r = df.sample(1).iloc[0]
        st.markdown(f"""
        <div class='recipe-card'>
            <span class='tag'>{r['Categorie']}</span>
            <h3>{r['Nom']}</h3>
            <p>⏱️ Temps de préparation : {r['Temps']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- ONGLET MES RECETTES ---
with menu[1]:
    recherche = st.text_input("🔍 Rechercher une recette ou un ingrédient")
    if not df.empty:
        filtre = df[df['Nom'].str.contains(recherche, case=False, na=False) | df['Ingredients'].str.contains(recherche, case=False, na=False)]
        for i, r in filtre.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='recipe-card'>
                    <span class='tag'>{r['Categorie']}</span>
                    <h2>{r['Nom']}</h2>
                    <p><b>Temps :</b> {r['Temps']}</p>
                """, unsafe_allow_html=True)
                
                if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                    st.image(r['Image'], use_container_width=True)
                
                with st.expander("Voir la recette complète"):
                    st.markdown("#### 🛒 Ingrédients")
                    st.write(r['Ingredients'])
                    st.markdown("#### 👨‍🍳 Préparation")
                    st.write(r['Etapes'])
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Vous n'avez pas encore de recettes. Allez dans l'onglet 'Ajouter' !")

# --- ONGLET AJOUTER ---
with menu[2]:
    st.subheader("Créer une nouvelle fiche")
    with st.form("ajout_recette"):
        nom = st.text_input("Nom du plat *")
        temps = st.text_input("Temps (ex: 30 min)")
        cat = st.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Apéro"])
        ing = st.text_area("Liste des ingrédients")
        etp = st.text_area("Étapes de préparation")
        url = st.text_input("Lien d'une image (optionnel)")
        
        if st.form_submit_button("ENREGISTRER LA RECETTE"):
            if nom:
                data = [nom, temps, 4, ing, etp, cat, 5, "Moyen", "Non", url, st.session_state.username]
                requests.post(WEB_APP_URL, json={"action": "add", "values": data})
                st.success("Recette enregistrée !")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else: st.error("Le nom du plat est obligatoire.")

# --- ONGLET COURSES ---
with menu[3]:
    st.subheader("Votre liste de courses")
    if not df.empty:
        choix = st.multiselect("Sélectionnez les recettes à cuisiner :", df['Nom'].tolist())
        if choix:
            liste_totale = []
            for c in choix:
                liste_totale.extend(str(df[df['Nom']==c]['Ingredients'].values[0]).split(','))
            
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            for item in sorted(set(liste_totale)):
                if item.strip():
                    st.checkbox(item.strip(), key=item)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()
