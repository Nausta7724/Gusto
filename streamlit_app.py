import streamlit as st
import pandas as pd
import requests
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO PREMIUM", page_icon="👨‍🍳", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzBpkR8KzeCmPcZ_AJwWxuJWPNwcfgKcllipRoR1EIlmpys8PiVJsdI1SKy91io-osa/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN PREMIUM & MOBILE-FIRST ---
st.markdown("""
    <style>
    /* Masquer les éléments Streamlit qui buguent */
    header, [data-testid="stSidebar"], [data-testid="stHeader"] {display: none !important;}
    .main .block-container {padding-top: 2rem !important; background-color: #fdfdfd;}

    /* Titres stylisés */
    h1 { color: #2D3436; font-weight: 800; text-align: center; margin-bottom: 20px; }
    
    /* Cartes de recettes modernes */
    .recipe-card {
        background: white; 
        padding: 20px; 
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        border: 1px solid #f1f1f1;
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        width: 100%; 
        border-radius: 15px; 
        background: linear-gradient(135deg, #FF4B2B 0%, #FF416C 100%);
        color: white;
        font-weight: 700; 
        height: 3.8rem; 
        border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3);
    }
    
    /* Badges de catégories */
    .badge {
        background-color: #f0f2f6;
        color: #555;
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- SYSTÈME DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown("<h1>👨‍🍳 GUSTO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Votre grimoire culinaire sécurisé</p>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Identifiant", placeholder="Nom de chef...")
        p = st.text_input("Mot de passe", type="password", placeholder="Secret...")
        if st.button("ACCÉDER AU GRIMOIRE"):
            if u and p:
                res = requests.post(WEB_APP_URL, json={"action": "login", "values": [u, hashlib.sha256(p.encode()).hexdigest()]})
                if res.text in ["SUCCESS", "CREATED"]:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
            else: st.warning("Veuillez remplir les champs.")
    st.stop()

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        return df[df['Proprietaire'] == st.session_state.username] if 'Proprietaire' in df.columns else df
    except: return pd.DataFrame()

df = load_data()

# --- MENU DE NAVIGATION ---
st.markdown(f"<p style='text-align:right; color:#888;'>Chef: <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)
menu = st.selectbox("Navigation", ["🏠 Accueil", "📖 Mes Recettes", "⚙️ Gestion", "🛒 Ma Liste", "🚪 Déconnexion"])

if menu == "🚪 Déconnexion":
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# --- PAGES ---

if menu == "🏠 Accueil":
    st.markdown("<h1>Tableau de Bord</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Recettes", len(df))
    c2.metric("Chef", st.session_state.username)
    
    if not df.empty:
        st.markdown("### 🎲 Suggestion Aléatoire")
        r = df.sample(1).iloc[0]
        st.markdown(f"""
            <div class='recipe-card'>
                <h3>{r['Nom']}</h3>
                <p>⏱️ {r['Temps']} | 🏷️ {r['Categorie']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Actualiser les recettes"):
        st.cache_data.clear()
        st.rerun()

elif menu == "📖 Mes Recettes":
    st.markdown("<h1>Mon Grimoire</h1>", unsafe_allow_html=True)
    
    # Nouvelle fonctionnalité : Filtre par catégorie
    if not df.empty:
        categories = ["Toutes"] + sorted(df['Categorie'].unique().tolist())
        cat_filter = st.selectbox("Filtrer par type :", categories)
        search = st.text_input("🔍 Rechercher un ingrédient ou un nom...")
        
        filtered = df.copy()
        if cat_filter != "Toutes":
            filtered = filtered[filtered['Categorie'] == cat_filter]
        if search:
            filtered = filtered[filtered['Nom'].str.contains(search, case=False) | filtered['Ingredients'].str.contains(search, case=False)]

        for i, r in filtered.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='recipe-card'>
                    <span class='badge'>{r['Categorie']}</span>
                    <h2 style='margin-top:10px;'>{r['Nom']}</h2>
                    <p style='color:#666;'><b>Temps :</b> {r['Temps']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if pd.notna(r['Image']) and str(r['Image']).startswith('http'):
                    st.image(r['Image'], use_container_width=True)
                
                with st.expander("📖 Voir la préparation"):
                    st.write("**Ingrédients :**")
                    st.info(r['Ingredients'])
                    st.write("**Étapes :**")
                    st.write(r['Etapes'])
                st.divider()

elif menu == "⚙️ Gestion":
    st.markdown("<h1>Configuration</h1>", unsafe_allow_html=True)
    action = st.tabs(["➕ Ajouter", "✏️ Modifier", "🗑️ Supprimer"])
    
    with action[0]:
        with st.form("add"):
            n = st.text_input("Nom de la recette *")
            t = st.text_input("Temps (ex: 20 min)")
            c = st.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Apéro", "Petit Déjeuner"])
            i = st.text_area("Ingrédients (séparés par des virgules)")
            e = st.text_area("Préparation pas à pas")
            img = st.text_input("URL de l'image")
            if st.form_submit_button("SAUVEGARDER"):
                if n:
                    data = [n, t, 4, i, e, c, 5, "Moyen", "Non", img, st.session_state.username]
                    requests.post(WEB_APP_URL, json={"action": "add", "values": data})
                    st.success("Recette ajoutée !"); time.sleep(1); st.cache_data.clear(); st.rerun()
                else: st.error("Le nom est obligatoire.")

    with action[1]:
        if not df.empty:
            target = st.selectbox("Recette à modifier", df['Nom'].tolist())
            r = df[df['Nom'] == target].iloc[0]
            with st.form("edit"):
                un = st.text_input("Nom", value=r['Nom'])
                uc = st.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Apéro"], index=0)
                ui = st.text_area("Ingrédients", value=r['Ingredients'])
                ue = st.text_area("Étapes", value=r['Etapes'])
                uimg = st.text_input("Image", value=r['Image'] if pd.notna(r['Image']) else "")
                if st.form_submit_button("METTRE À JOUR"):
                    data = [un, r['Temps'], 4, ui, ue, uc, 5, "Moyen", "Non", uimg, st.session_state.username]
                    requests.post(WEB_APP_URL, json={"action": "edit", "values": data})
                    st.success("Modifié !"); time.sleep(1); st.cache_data.clear(); st.rerun()

    with action[2]:
        st.warning("Fonctionnalité bientôt disponible : La suppression se fait via Google Sheets pour le moment.")

elif menu == "🛒 Ma Liste":
    st.markdown("<h1>🛒 Liste de Courses</h1>", unsafe_allow_html=True)
    if not df.empty:
        choix = st.multiselect("Sélectionnez vos plats :", df['Nom'].tolist())
        if choix:
            st.markdown("---")
            all_ings = []
            for c in choix:
                all_ings.extend(str(df[df['Nom']==c]['Ingredients'].values[0]).split(','))
            
            for item in sorted(set(all_ings)):
                st.checkbox(item.strip(), key=f"shop_{item}")
            
            # Nouvelle fonctionnalité : Bouton de partage
            if st.button("📱 Copier la liste"):
                liste_texte = "\\n".join(all_ings)
                st.code(liste_texte)
                st.toast("Liste prête à être copiée !")
