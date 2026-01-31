import streamlit as st
import pandas as pd
import requests
import time
import random

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="GUSTO PRO", page_icon="👨‍🍳", layout="wide")

# --- PARAMÈTRES DE CONNEXION ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbylkx9BgPPzjq3X6sv4lYC1QpYLJOQTkPE-AhGZlapfi8tgk0qMrGCbtVrVANDqVPUL/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN CSS (MODERNE & REMPLI) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .main-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 5px solid #FF4B4B;
    }
    .stat-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #eee;
    }
    h1 { color: #1E1E1E; font-family: 'Trebuchet MS', sans-serif; font-weight: 800; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS ---
@st.cache_data(ttl=5) # Rafraîchissement ultra-rapide
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: return pd.DataFrame()

def save_to_google(data_list):
    try:
        response = requests.post(WEB_APP_URL, json=data_list)
        return response.status_code == 200
    except: return False

# Chargement des données
df = load_data()

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>👨‍🍳 GUSTO PRO</h1>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("TABLEAU DE BORD", ["🏠 Vue d'ensemble", "📖 Mon Livre", "➕ Créer une Recette", "⚖️ Outils & Conversion"])
    
    st.markdown("---")
    st.subheader("⏱️ Minuteur Rapide")
    m, s = st.columns(2)
    min_val = m.number_input("Min", 0, 180, 10)
    if st.button("Lancer Chrono"):
        st.toast(f"Chrono lancé pour {min_val} minutes !", icon="🔥")

# --- PAGE 1 : VUE D'ENSEMBLE (DASHBOARD) ---
if menu == "🏠 Vue d'ensemble":
    st.title("Bienvenue dans votre Cuisine digitale")
    
    # Ligne de Statistiques
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.markdown(f'<div class="stat-card"><h3>📚</h3><b>{len(df)} Recettes</b></div>', unsafe_allow_html=True)
    with s2: 
        fav_count = len(df[df['Favori'] == 'Oui']) if 'Favori' in df.columns else 0
        st.markdown(f'<div class="stat-card"><h3>❤️</h3><b>{fav_count} Favoris</b></div>', unsafe_allow_html=True)
    with s3:
        top_cat = df['Categorie'].mode()[0] if not df.empty else "N/A"
        st.markdown(f'<div class="stat-card"><h3>📂</h3><b>Top: {top_cat}</b></div>', unsafe_allow_html=True)
    with s4: st.markdown('<div class="stat-card"><h3>📅</h3><b>Janvier 2026</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("🎲 Suggestion du moment")
        if not df.empty:
            recette = df.sample(1).iloc[0]
            st.markdown(f"""
            <div class="main-card">
                <h2>{recette['Nom']}</h2>
                <p><b>Temps :</b> {recette['Temps']} | <b>Difficulté :</b> {recette.get('Difficulte', 'Moyen')}</p>
                <p><i>"{recette['Ingredients'][:100]}..."</i></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Ajoutez des recettes pour voir des suggestions ici !")
            
    with c2:
        st.subheader("🌟 Note du Chef")
        st.markdown("""
        <div class="main-card" style="border-left: 5px solid #f1c40f;">
            <p>"La cuisine, c'est un peu comme le code : un ingrédient oublié et tout change. Soyez précis !"</p>
            <hr>
            <p style='font-size: 0.8em;'>L'appli est connectée à votre Google Drive.</p>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2 : LE LIVRE ---
elif menu == "📖 Mon Livre":
    st.title("📖 Votre Répertoire Culinaire")
    
    col_search, col_filter = st.columns([3, 1])
    search = col_search.text_input("🔍 Rechercher par nom ou ingrédient...", "")
    cat_list = ["Toutes"] + (list(df['Categorie'].unique()) if not df.empty else [])
    filtre = col_filter.selectbox("Catégorie", cat_list)

    if not df.empty:
        # Logique de filtrage
        mask = df['Nom'].str.contains(search, case=False, na=False) | df['Ingredients'].str.contains(search, case=False, na=False)
        filtered_df = df[mask]
        if filtre != "Toutes":
            filtered_df = filtered_df[filtered_df['Categorie'] == filtre]

        for i, r in filtered_df.iterrows():
            with st.expander(f"🍽️ {r['Nom'].upper()} — {r['Temps']}"):
                t1, t2 = st.tabs(["🛒 Ingrédients & Infos", "👨‍🍳 Préparation"])
                with t1:
                    c1, c2 = st.columns(2)
                    c1.write(f"**👥 Portions :** {r['Personnes']}")
                    c1.write(f"**📂 Type :** {r['Categorie']}")
                    c2.write(f"**⚡ Difficulté :** {r.get('Difficulte', 'Moyen')}")
                    c2.write(f"**⭐ Note :** {r.get('Note', 5)}/5")
                    st.markdown("**Liste des ingrédients :**")
                    st.info(r['Ingredients'])
                with t2:
                    st.markdown("### Étapes à suivre :")
                    st.write(r['Etapes'])
    else:
        st.warning("Votre livre est vide.")

# --- PAGE 3 : CRÉATION (AUTO-SAVE) ---
elif menu == "➕ Créer une Recette":
    st.title("➕ Nouvelle Fiche Technique")
    st.markdown("Remplissez le formulaire, la sauvegarde est automatique.")
    
    with st.form("recipe_form", clear_on_submit=True):
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nom du plat *")
        cat = c2.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Sauce", "Boisson"])
        
        c3, c4, c5 = st.columns(3)
        temps = c3.text_input("Temps (ex: 45 min)")
        pers = c4.number_input("Nombre de personnes", 1, 50, 4)
        diff = c5.selectbox("Difficulté", ["Facile", "Moyen", "Chef", "Étoilé"])
        
        ing = st.text_area("🛒 Ingrédients (séparez par des virgules)")
        steps = st.text_area("👨‍🍳 Instructions de préparation")
        
        note = st.slider("Note personnelle", 1, 5, 5)
        fav = st.checkbox("Ajouter aux favoris ❤️")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("💾 ENREGISTRER DÉFINITIVEMENT")
        
        if submitted:
            if nom and ing:
                # Préparation des données (ordre du Google Sheet)
                payload = [nom, temps, pers, ing, steps, cat, note, diff, "Oui" if fav else "Non"]
                
                with st.spinner("📦 Envoi au coffre-fort Google Drive..."):
                    if save_to_google(payload):
                        st.success(f"🌟 Magnifique ! '{nom}' a été ajouté à votre livre.")
                        st.balloons()
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Erreur de connexion. Vérifiez votre script Google Apps.")
            else:
                st.error("Le nom et les ingrédients sont obligatoires !")

# --- PAGE 4 : OUTILS ---
elif menu == "⚖️ Outils & Conversion":
    st.title("⚖️ Labo de Conversion")
    st.write("Un doute sur les doses ? Utilisez l'outil ci-dessous.")
    
    col_u1, col_u2 = st.columns(2)
    valeur = col_u1.number_input("Quantité", value=1.0)
    unite = col_u2.selectbox("Conversion", ["Litre vers ml", "Grammes vers Oz", "Cuillère à soupe vers ml"])
    
    if unite == "Litre vers ml": res = valeur * 1000 ; u = "ml"
    elif unite == "Grammes vers Oz": res = valeur * 0.035 ; u = "oz"
    else: res = valeur * 15 ; u = "ml"
    
    st.metric("Résultat", f"{res} {u}")
