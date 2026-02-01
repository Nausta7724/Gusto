import streamlit as st
import pandas as pd
import requests
import hashlib
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO", page_icon="🍳", layout="centered")

# Ton URL Google Script intégrée
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyU0SEgCs-GxgK7zTf958y1LkvyeCBGi5f5Ar1Mbtd6wEZtlJ9Uj2T8x10fgvQ2joRD/exec"
CSV_URL = "https://docs.google.com/spreadsheets/d/1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI/export?format=csv"

# --- DESIGN "GUSTO ÉLÉGANCE" (Lisible & Rempli) ---
st.markdown("""
    <style>
    /* Nettoyage de l'interface */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Titre */
    .main-title {
        color: #E63946;
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    /* Cartes Recettes */
    .recipe-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    
    /* Contraste des champs de saisie */
    input, textarea {
        background-color: white !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }
    
    /* Bouton Rouge GUSTO */
    .stButton>button {
        background-color: #E63946 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 3.5rem !important;
        font-weight: bold !important;
        width: 100%;
        font-size: 1.1rem !important;
    }
    
    .tag {
        background: #F1FAEE;
        color: #1D3557;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>GUSTO</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Connectez-vous pour accéder à vos recettes</p>", unsafe_allow_html=True)
    
    with st.container():
        u = st.text_input("Identifiant")
        p = st.text_input("Mot de passe", type="password")
        
        if st.button("ACCÉDER À MA CUISINE"):
            if u and p:
                # Hachage du mot de passe pour la sécurité
                hashed_p = hashlib.sha256(p.encode()).hexdigest()
                try:
                    res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashed_p]}, timeout=10)
                    
                    if res.text == "SUCCESS":
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.rerun()
                    elif res.text == "WRONG_PASS":
                        st.error("❌ Mot de passe incorrect. Réessayez.")
                    elif res.text == "CREATED":
                        st.success("✅ Nouveau compte créé ! Re-cliquez pour vous connecter.")
                    else:
                        st.error(f"Erreur serveur : {res.text}")
                except:
                    st.error("Impossible de contacter le serveur. Vérifiez votre connexion.")
            else:
                st.warning("Veuillez remplir tous les champs.")
    st.stop()

# --- INTERFACE PRINCIPALE ---
st.markdown("<div class='main-title'>GUSTO</div>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>Chef : <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)

# Barre de navigation par onglets (Claire et sans bug)
tabs = st.tabs(["🏠 Accueil", "📖 Mes Recettes", "➕ Ajouter", "🛒 Courses"])

# Chargement des données
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df[df['Proprietaire'] == st.session_state.username] if 'Proprietaire' in df.columns else df
    except: return pd.DataFrame()

df_user = load_data()

# --- ONGLET ACCUEIL ---
with tabs[0]:
    st.subheader("Tableau de bord")
    c1, c2 = st.columns(2)
    c1.metric("Vos recettes", len(df_user))
    if c2.button("Rafraîchir 🔄"):
        st.cache_data.clear()
        st.rerun()
    
    if not df_user.empty:
        st.markdown("---")
        st.markdown("### 🎲 Suggestion du Chef")
        r = df_user.sample(1).iloc[0]
        st.markdown(f"""
            <div class='recipe-card'>
                <span class='tag'>{r['Categorie']}</span>
                <h3 style='margin-top:10px;'>{r['Nom']}</h3>
                <p>⏱️ Temps : {r['Temps']}</p>
            </div>
        """, unsafe_allow_html=True)

# --- ONGLET MES RECETTES ---
with tabs[1]:
    search = st.text_input("🔍 Rechercher un plat ou un ingrédient...")
    if not df_user.empty:
        filtered = df_user[df_user['Nom'].str.contains(search, case=False, na=False) | 
                           df_user['Ingredients'].str.contains(search, case=False, na=False)]
        
        for i, r in filtered.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='recipe-card'>
                    <span class='tag'>{r['Categorie']}</span>
                    <h2>{r['Nom']}</h2>
                    <p><b>⏱️ Temps :</b> {r['Temps']}</p>
                """, unsafe_allow_html=True)
                
                if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                    st.image(r['Image'], use_container_width=True)
                
                with st.expander("📖 Voir les détails de la recette"):
                    st.markdown("#### 🛒 Ingrédients")
                    st.info(r['Ingredients'])
                    st.markdown("#### 👨‍🍳 Étapes de préparation")
                    st.write(r['Etapes'])
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Votre carnet est vide. Ajoutez votre première recette !")

# --- ONGLET AJOUTER ---
with tabs[2]:
    st.subheader("Ajouter une création")
    with st.form("add_form"):
        n = st.text_input("Nom de la recette *")
        t = st.text_input("Temps (ex: 15 min)")
        cat = st.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Apéro"])
        ing = st.text_area("Ingrédients (séparés par des virgules)")
        etp = st.text_area("Préparation pas à pas")
        img = st.text_input("URL de l'image (optionnel)")
        
        if st.form_submit_button("SAUVEGARDER DANS LE CLOUD"):
            if n:
                # Formatage des données pour Google Sheets
                new_data = [n, t, 4, ing, etp, cat, 5, "Moyen", "Non", img, st.session_state.username]
                requests.post(WEB_APP_URL, json={"action": "add", "values": new_data})
                st.success("✨ Recette ajoutée avec succès !")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Le nom est obligatoire.")

# --- ONGLET COURSES ---
with tabs[3]:
    st.subheader("Liste de courses intelligente")
    if not df_user.empty:
        selected = st.multiselect("Plats prévus pour la semaine :", df_user['Nom'].tolist())
        if selected:
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            ingredients_finaux = []
            for s in selected:
                ingredients_finaux.extend(str(df_user[df_user['Nom']==s]['Ingredients'].values[0]).split(','))
            
            for item in sorted(set(ingredients_finaux)):
                if item.strip():
                    st.checkbox(item.strip(), key=f"check_{item}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Ajoutez des recettes pour générer une liste.")

# --- DÉCONNEXION ---
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("🚪 QUITTER GUSTO"):
    st.session_state.logged_in = False
    st.rerun()
