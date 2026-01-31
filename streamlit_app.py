import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="GUSTO ELITE", page_icon="💎", layout="wide")

# TON NOUVEAU LIEN SCRIPT
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwE9VyFCzQHwuyY3W21Drr5KNZIQ1bnPIX8vHRZTuXkNF2Ljm-fanlbeQAd9xD3owQx/exec"
SHEET_ID = "1mMLxy0heVZp0QmBjB1bzhcXL8ZiIjgjBxvcAIyM-6pI"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN PREMIUM & ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
    
    .stApp { background-color: #F7F9FC; }
    
    /* Cartes de recettes */
    .recipe-card {
        background: white; 
        padding: 20px; 
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #E0E6ED;
        margin-bottom: 20px;
    }
    
    /* Titres */
    h1 { color: #1A1C1E; font-weight: 700; }
    
    /* Boutons */
    .stButton>button {
        border-radius: 12px;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE DONNÉES ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
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
    st.markdown("<h1 style='text-align: center;'>👨‍🍳 GUSTO</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVIGATION", ["🏠 Accueil", "📖 Mon Livre", "⚙️ Gérer / Modifier", "🛒 Courses"])
    
    st.markdown("---")
    st.subheader("⏱️ Minuteur")
    t_min = st.number_input("Minutes", 1, 180, 10)
    if st.button("🔔 Lancer"):
        st.toast(f"Top chrono ! {t_min} min.", icon="⏳")
    
    if st.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()

# --- PAGES ---

# 1. ACCUEIL (DASHBOARD)
if menu == "🏠 Accueil":
    st.title("Bonjour Chef ! ✨")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Recettes", len(df) if not df.empty else 0)
    c2.metric("Favoris", "---")
    c3.metric("Statut", "Connecté 🟢")
    
    if not df.empty:
        st.markdown("### 💡 Inspiration du moment")
        r = df.sample(1).iloc[0]
        with st.container():
            st.markdown(f"""<div class='recipe-card'>
                <div style='display: flex; gap: 20px;'>
                    <div style='flex: 1;'>
                        <h2>{r['Nom']}</h2>
                        <p>🕒 {r['Temps']} | 👥 {r['Personnes']} pers.</p>
                        <p style='color: #666;'><i>"{str(r['Ingredients'])[:100]}..."</i></p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# 2. LE LIVRE (GRIMOIRE)
elif menu == "📖 Mon Livre":
    st.title("📖 Mon Grimoire")
    search = st.text_input("🔍 Rechercher un plat ou un ingrédient...")
    
    if not df.empty:
        mask = df['Nom'].str.contains(search, case=False, na=False) | df['Ingredients'].str.contains(search, case=False, na=False)
        filtered = df[mask]
        
        for i, r in filtered.iterrows():
            with st.container():
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                col_img, col_txt = st.columns([1, 2])
                with col_img:
                    img = r['Image'] if pd.notna(r.get('Image')) else "https://via.placeholder.com/400x300?text=Gusto"
                    st.image(img, use_container_width=True)
                with col_txt:
                    st.subheader(r['Nom'])
                    st.write(f"⏱️ {r['Temps']} | 👥 {r['Personnes']} pers.")
                    with st.expander("Voir les ingrédients & étapes"):
                        st.markdown("**🛒 Ingrédients :**")
                        st.write(r['Ingredients'])
                        st.markdown("**👨‍🍳 Préparation :**")
                        st.write(r['Etapes'])
                st.markdown('</div>', unsafe_allow_html=True)

# 3. GÉRER / MODIFIER (LA NOUVEAUTÉ)
elif menu == "⚙️ Gérer / Modifier":
    st.title("⚙️ Gestionnaire de Recettes")
    tab_add, tab_edit = st.tabs(["➕ Ajouter une recette", "✏️ Modifier une recette"])
    
    with tab_add:
        with st.form("form_add", clear_on_submit=True):
            nom = st.text_input("Nom de la recette *")
            c1, c2 = st.columns(2)
            temps = c1.text_input("Temps (ex: 30 min)")
            cat = c2.selectbox("Catégorie", ["Plat", "Entrée", "Dessert", "Sauce"])
            ing = st.text_area("Ingrédients (séparez par des virgules)")
            steps = st.text_area("Préparation")
            img = st.text_input("URL de l'image")
            
            if st.form_submit_button("Enregistrer la recette"):
                if nom and ing:
                    res = send_to_google([nom, temps, 4, ing, steps, cat, 5, "Moyen", "Non", img], "add")
                    if res: 
                        st.success(f"Bravo ! {nom} a été ajouté.")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()

    with tab_edit:
        if not df.empty:
            recette_a_modifier = st.selectbox("Sélectionnez la recette à modifier", df['Nom'].tolist())
            old_data = df[df['Nom'] == recette_a_modifier].iloc[0]
            
            with st.form("form_edit"):
                u_nom = st.text_input("Nom (ne pas modifier pour garder la liaison)", value=old_data['Nom'])
                u_temps = st.text_input("Temps", value=old_data['Temps'])
                u_ing = st.text_area("Ingrédients", value=old_data['Ingredients'])
                u_steps = st.text_area("Étapes", value=old_data['Etapes'])
                u_img = st.text_input("Lien Image", value=old_data['Image'] if pd.notna(old_data['Image']) else "")
                
                if st.form_submit_button("Mettre à jour sur Google Sheets"):
                    # On garde les mêmes colonnes
                    res = send_to_google([u_nom, u_temps, 4, u_ing, u_steps, "Plat", 5, "Moyen", "Non", u_img], "edit")
                    if res:
                        st.success("Modifications enregistrées !")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("Aucune recette à modifier pour le moment.")

# 4. COURSES
elif menu == "🛒 Courses":
    st.title("🛒 Liste de Courses")
    if not df.empty:
        choix = st.multiselect("Choisir les plats de la semaine :", df['Nom'].tolist())
        if choix:
            st.markdown("---")
            all_ing = []
            for c in choix:
                ing_list = df[df['Nom'] == c]['Ingredients'].values[0]
                all_ing.extend(str(ing_list).split(','))
            
            for item in sorted(set(all_ing)):
                st.checkbox(item.strip(), key=f"shop_{item}")
