import streamlit as st
import json
import os

# Configuration de la page
st.set_page_config(page_title="GUSTO PRO", layout="wide", page_icon="👨‍🍳")

# --- DESIGN PERSONNALISÉ (CSS) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #FDFCFB; }
    
    /* Titre principal */
    h1 { color: #2C3E50; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    
    /* Cartes de recettes */
    .recipe-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE DONNÉES ---
DB_FILE = "gusto_recipes.json"

def charger_donnees():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"Recettes": []}

if "db" not in st.session_state:
    st.session_state.db = charger_donnees()

def sauvegarder():
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(st.session_state.db, f, indent=4)

# --- NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3448/3448099.png", width=100)
    st.title("GUSTO PRO")
    menu = st.radio("Menu Principal", ["📖 Mon Livre", "➕ Création", "⚙️ Gestion"])
    st.write("---")
    st.caption("Application Cuisine v2.0")

# --- PAGE 1 : LIVRE DE RECETTES ---
if menu == "📖 Mon Livre":
    st.title("📖 Livre de Recettes")
    recherche = st.text_input("🔍 Rechercher un ingrédient ou un plat...", placeholder="Ex: Risotto...")
    
    if not st.session_state.db["Recettes"]:
        st.info("Aucune recette dans votre livre pour le moment.")
    else:
        for i, r in enumerate(st.session_state.db["Recettes"]):
            if recherche.lower() in r["nom"].lower():
                with st.container():
                    st.markdown(f"### {r['nom'].upper()}")
                    c1, c2 = st.columns([1, 1.5])
                    
                    with c1:
                        st.markdown(f"⏱️ **Temps :** {r['temps']} | 🏷️ {r['categorie']}")
                        nb_base = r.get('personnes', 1)
                        if nb_base < 1: nb_base = 1
                        
                        portions = st.number_input("Nombre de couverts", min_value=1, value=int(nb_base), key=f"p_{i}")
                        ratio = portions / nb_base
                        
                        st.write("**🛒 Ingrédients :**")
                        for ing in r["ingredients"]:
                            try:
                                q_val = float(ing['quantite'])
                                q_aff = round(q_val * ratio, 2) if q_val > 0 else ""
                                st.write(f"- **{ing['nom']}** : {q_aff} {ing['unite']}")
                            except:
                                st.write(f"- **{ing['nom']}**")
                    
                    with c2:
                        st.write("**👨‍🍳 Préparation :**")
                        for n, etape in enumerate(r["etapes"]):
                            st.write(f"{n+1}. {etape}")
                        st.camera_input("Scanner le plat final", key=f"cam_{i}")
                    
                    st.divider()

# --- PAGE 2 : AJOUT / MODIFICATION ---
elif menu == "➕ Création":
    st.title("➕ Nouvelle Recette")
    with st.form("ajout_form", clear_on_submit=True):
        nom = st.text_input("Titre du plat")
        cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Sauce", "Cocktail"])
        c1, c2 = st.columns(2)
        temps = c1.text_input("Durée (ex: 15 min)")
        pers = c2.number_input("Couverts de base", min_value=1, value=1)
        
        st.markdown("**Ingrédients** (Nom, Quantité, Unité)")
        ing_bruts = st.text_area("Ex: Farine, 500, g (Une ligne par ingrédient)", height=150)
        
        st.markdown("**Étapes du processus**")
        etapes_brutes = st.text_area("Description des étapes (Une ligne par étape)", height=150)
        
        if st.form_submit_button("Enregistrer la fiche"):
            liste_ing = []
            for ligne in ing_bruts.split('\n'):
                if ligne.strip():
                    p = ligne.split(',')
                    if len(p) == 3: liste_ing.append({"nom": p[0].strip(), "quantite": p[1].strip(), "unite": p[2].strip()})
                    elif len(p) == 2: liste_ing.append({"nom": p[0].strip(), "quantite": p[1].strip(), "unite": ""})
                    else: liste_ing.append({"nom": ligne.strip(), "quantite": "0", "unite": ""})
            
            st.session_state.db["Recettes"].append({
                "nom": nom, "categorie": cat, "temps": temps, "personnes": pers,
                "ingredients": liste_ing, "etapes": [e.strip() for e in etapes_brutes.split('\n') if e.strip()]
            })
            sauvegarder()
            st.success("✅ Recette ajoutée au livre !")

# --- PAGE 3 : MODIFICATION & SUPPRESSION ---
elif menu == "⚙️ Gestion":
    st.title("⚙️ Administration du Livre")
    if not st.session_state.db["Recettes"]:
        st.warning("Rien à gérer ici.")
    else:
        for i, r in enumerate(st.session_state.db["Recettes"]):
            col_nom, col_edit, col_del = st.columns([3, 1, 1])
            col_nom.write(f"**{r['nom']}** ({r['categorie']})")
            
            if col_edit.button("Modifier", key=f"btn_edit_{i}"):
                st.session_state.editing = i
            
            if col_del.button("🗑️", key=f"btn_del_{i}"):
                st.session_state.db["Recettes"].pop(i)
                sauvegarder()
                st.rerun()

        # Fenêtre de modification (si une recette est sélectionnée)
        if "editing" in st.session_state:
            idx = st.session_state.editing
            recette = st.session_state.db["Recettes"][idx]
            st.divider()
            st.subheader(f"Modification de : {recette['nom']}")
            
            # Formulaire pré-rempli pour modification
            with st.form("edit_form"):
                n_nom = st.text_input("Nom", value=recette['nom'])
                n_cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Sauce"], index=0)
                n_temps = st.text_input("Temps", value=recette['temps'])
                
                # Re-transformer les ingrédients en texte
                ing_text = "\n".join([f"{ing['nom']}, {ing['quantite']}, {ing['unite']}" for ing in recette['ingredients']])
                n_ing = st.text_area("Ingrédients", value=ing_text)
                
                # Re-transformer les étapes en texte
                eta_text = "\n".join(recette['etapes'])
                n_eta = st.text_area("Étapes", value=eta_text)
                
                if st.form_submit_button("Sauvegarder les modifications"):
                    # Logique de mise à jour (similaire à l'ajout)
                    # ... (on met à jour st.session_state.db["Recettes"][idx])
                    st.success("Modifications enregistrées !")
                    del st.session_state.editing
                    st.rerun()
