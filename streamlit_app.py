import streamlit as st
import json
import os

# Configuration de la page pour mobile et PC
st.set_page_config(page_title="GUSTO", layout="wide", page_icon="👨‍🍳")

# Style pour rendre l'interface plus "Pro"
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Gestion de la base de données
DB_FILE = "gusto_recipes.json"

def charger_donnees():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"Recettes": []}

if "db" not in st.session_state:
    st.session_state.db = charger_donnees()

def sauvegarder():
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(st.session_state.db, f, indent=4)

# --- NAVIGATION ---
st.title("👨‍🍳 GUSTO")
menu = ["📖 Livre de Recettes", "➕ Ajouter une Recette", "📊 Exporter"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "📖 Livre de Recettes":
    st.subheader("Vos fiches techniques")
    recherche = st.text_input("🔍 Rechercher un plat...")
    
    if not st.session_state.db["Recettes"]:
        st.info("Le livre est vide. Ajoutez votre première recette !")
    else:
        for i, r in enumerate(st.session_state.db["Recettes"]):
            if recherche.lower() in r["nom"].lower():
                with st.expander(f"🍴 {r['nom'].upper()} - {r['categorie']}"):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.write(f"⏱️ **Temps :** {r['temps']}")
                        # Calculateur de portions
                        nb_base = r.get('personnes', 1)
                        portions = st.number_input("Ajuster pour X personnes", min_value=1, value=int(nb_base), key=f"p_{i}")
                        ratio = portions / nb_base
                        
                        st.write("**Ingrédients :**")
                        for ing in r["ingredients"]:
                            q = float(ing['quantite']) * ratio
                            st.write(f"- {ing['nom']} : {round(q, 2)} {ing['unite']}")
                    
                    with c2:
                        st.write("**Processus & Étapes :**")
                        for n, etape in enumerate(r["etapes"]):
                            st.write(f"{n+1}. {etape}")
                        
                        st.camera_input("Prendre une photo du plat", key=f"cam_{i}")

elif choix == "➕ Ajouter une Recette":
    st.subheader("Nouvelle Fiche Technique")
    with st.form("form_recette", clear_on_submit=True):
        nom = st.text_input("Nom du plat (ex: Risotto au Safran)")
        cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Sauce", "Autre"])
        col1, col2 = st.columns(2)
        temps = col1.text_input("Temps de réalisation")
        pers = col2.number_input("Nombre de personnes (base)", min_value=1, value=1)
        
        st.write("**Ingrédients** (Format : Nom, Quantité, Unité)")
        st.caption("Exemple : Farine, 500, g (une ligne par ingrédient)")
        ing_bruts = st.text_area("Liste des ingrédients")
        
        st.write("**Processus** (Décrivez les étapes)")
        etapes_brutes = st.text_area("Une étape par ligne")
        
        valider = st.form_submit_button("Enregistrer dans GUSTO")
        
        if valider:
            liste_ing = []
            for ligne in ing_bruts.split('\n'):
                if ',' in ligne:
                    parts = ligne.split(',')
                    liste_ing.append({"nom": parts[0].strip(), "quantite": parts[1].strip(), "unite": parts[2].strip()})
            
            nouvelle_recette = {
                "nom": nom,
                "categorie": cat,
                "temps": temps,
                "personnes": pers,
                "ingredients": liste_ing,
                "etapes": [e.strip() for e in etapes_brutes.split('\n') if e.strip()]
            }
            
            st.session_state.db["Recettes"].append(nouvelle_recette)
            sauvegarder()
            st.success("Recette enregistrée avec succès !")

elif choix == "📊 Exporter":
    st.subheader("Sauvegarde des données")
    data_str = json.dumps(st.session_state.db, indent=4)
    st.download_button("Télécharger le fichier GUSTO.json", data=data_str, file_name="gusto_backup.json")
