import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIG ---
st.set_page_config(page_title="GUSTO ULTIMATE", page_icon="🍳", layout="wide")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbylkx9BgPPzjq3X6sv4lYC1QpYLJOQTkPE-AhGZlapfi8tgk0qMrGCbtVrVANDqVPUL/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- STYLE ---
st.markdown("""
    <style>
    .recipe-card {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .img-container img { border-radius: 15px; object-fit: cover; }
    .stButton>button { background: #FF4B4B; color: white; border-radius: 12px; }
    .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- DATA ---
@st.cache_data(ttl=5)
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

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("👨‍🍳 GUSTO ULTIMATE")
    menu = st.radio("MENU", ["🏠 Dashboard", "📖 Mon Grimoire", "➕ Ajouter", "🛒 Liste de Courses"])
    st.markdown("---")
    if st.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Bienvenue, Chef !")
    if not df.empty:
        recette = df.sample(1).iloc[0]
        st.subheader("💡 Suggestion du moment")
        c1, c2 = st.columns([1, 2])
        with c1:
            img_url = recette['Image'] if pd.notna(recette.get('Image')) else "https://via.placeholder.com/400x300?text=Pas+d'image"
            st.image(img_url, use_container_width=True)
        with c2:
            st.markdown(f"### {recette['Nom']}")
            st.write(f"⏱️ {recette['Temps']} | 👥 {recette['Personnes']} pers.")
            if st.button("Voir la recette complète"):
                st.session_state.search = recette['Nom']
                # On simulerait ici un saut vers le livre

# --- MON GRIMOIRE ---
elif menu == "📖 Mon Grimoire":
    st.title("📖 Mes Recettes")
    search = st.text_input("🔍 Rechercher une recette ou un ingrédient...", key="search_bar")
    
    if not df.empty:
        filtered = df[df['Nom'].str.contains(search, case=False, na=False) | df['Ingredients'].str.contains(search, case=False, na=False)]
        
        for i, r in filtered.iterrows():
            with st.container():
                st.markdown(f'<div class="recipe-card">', unsafe_allow_html=True)
                col_img, col_txt = st.columns([1, 2])
                
                with col_img:
                    img_url = r['Image'] if pd.notna(r.get('Image')) else "https://via.placeholder.com/400x300?text=Gusto"
                    st.image(img_url, use_container_width=True)
                
                with col_txt:
                    st.header(r['Nom'])
                    st.write(f"**⏱️ Temps :** {r['Temps']} | **⚡ Difficulté :** {r.get('Difficulte', 'Moyen')}")
                    
                    t1, t2 = st.tabs(["🛒 Ingrédients", "👨‍🍳 Étapes"])
                    with t1:
                        for ing in str(r['Ingredients']).split(','):
                            st.checkbox(ing.strip(), key=f"{i}_{ing}")
                    with t2:
                        st.write(r['Etapes'])
                st.markdown('</div>', unsafe_allow_html=True)

# --- AJOUTER ---
elif menu == "➕ Ajouter":
    st.title("➕ Nouvelle Création")
    with st.form("add_form"):
        nom = st.text_input("Nom du plat *")
        c1, c2 = st.columns(2)
        temps = c1.text_input("Temps")
        pers = c2.number_input("Personnes", 1, 10, 2)
        
        ing = st.text_area("Ingrédients (séparés par des virgules)")
        steps = st.text_area("Préparation")
        
        # NOUVEAU : Champ Image
        img = st.text_input("URL de l'image (ex: lien Google Images ou Pinterest)")
        
        cat = st.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Sauce"])
        diff = st.selectbox("Difficulté", ["Facile", "Moyen", "Chef"])
        
        if st.form_submit_button("💾 SAUVEGARDER"):
            if nom and ing:
                # Payload pour Google (On ajoute 'img' à la fin)
                # Ordre: Nom, Temps, Personnes, Ingredients, Etapes, Categorie, Note, Difficulte, Favori, Image
                payload = [nom, temps, pers, ing, steps, cat, 5, diff, "Non", img]
                if save_to_google(payload):
                    st.success("C'est dans la boîte !")
                    st.balloons()
                    time.sleep(2)
                    st.cache_data.clear()
                    st.rerun()

# --- LISTE DE COURSES ---
elif menu == "🛒 Liste de Courses":
    st.title("🛒 Ma Liste de Courses")
    if not df.empty:
        choix = st.multiselect("Quelles recettes prévois-tu de cuisiner ?", df['Nom'].tolist())
        if choix:
            st.subheader("Articles à acheter :")
            all_ingredients = []
            for c in choix:
                ingredients = df[df['Nom'] == c]['Ingredients'].values[0]
                all_ingredients.extend(str(ingredients).split(','))
            
            for item in sorted(all_ingredients):
                st.checkbox(item.strip())
            
            if st.button("🗑️ Vider la liste"):
                st.rerun()
