import streamlit as st
import pandas as pd
import json
import os

# Configuration de la page
st.set_page_config(page_title="GUSTO - Fiches Techniques", layout="wide", page_icon="👨‍🍳")

# Style CSS personnalisé pour un look pro
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .recipe-card { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Initialisation de la base de données (Fichier JSON local)
DB_FILE = "gusto_recipes.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "Recettes": [
            {
                "nom": "Pâtes Carbonara (La Vraie)",
                "categorie": "Plat",
                "temps": "15 min",
                "personnes": 2,
                "ingredients": [{"nom": "Spaghetti", "quantite": 200, "unite": "g"}, {"nom": "Guanciale", "quantite": 100, "unite": "g"}, {"nom": "Jaunes d'œufs", "quantite": 4, "unite": "pcs"}, {"nom": "Pecorino Romano", "quantite": 50, "unite": "g"}],
                "etapes": ["Tailler le guanciale en dés.", "Mélanger œufs et fromage.", "Cuire les pâtes al dente.", "Mélanger hors du feu avec un peu d'eau de cuisson."]
            },
            {
                "nom": "Risotto aux Champignons",
                "categorie": "Plat",
                "temps": "30 min",
                "personnes": 4,
                "ingredients": [{"nom": "Riz Arborio", "quantite": 320, "unite": "g"}, {"nom": "Champignons", "quantite": 500, "unite": "g"}, {"nom": "Bouillon", "quantite": 1, "unite": "L"}],
                "etapes": ["Nacrer le riz avec des échalotes.", "Ajouter le bouillon louche après louche.", "Lier au beurre et parmesan en fin de cuisson."]
            },
            {
                "nom": "Gratin Dauphinois",
                "categorie": "Accompagnement",
                "temps": "1h15",
                "personnes": 6,
                "ingredients": [{"nom": "Pommes de terre", "quantite": 1.5, "unite": "kg"}, {"nom": "Crème liquide", "quantite": 50, "unite": "cl"}, {"nom": "Ail", "quantite": 2, "unite": "gousses"}],
                "etapes": ["Trancher les PDT finement à la mandoline.", "Frotter le plat avec l'ail.", "Disposer les tranches et verser la crème.", "Cuire à 160°C jusqu'à tendreté."]
            }
        ]
    }

if "db" not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f)

# --- INTERFACE ---
st.title("👨‍🍳 GUSTO")
st.subheader("Gestionnaire de Fiches Techniques")

menu = ["📖 Consulter le Livre", "➕ Ajouter une Recette", "⚙️ Paramètres"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "📖 Consulter le Livre":
    st.write("### Vos Recettes")
    search = st.text_input("Rechercher un plat ou un ingrédient...")
    
    for i, r in enumerate(st.session_state.db["Recettes"]):
        if search.lower() in r["nom"].lower():
            with st.expander(f"{r['nom']} ({r['categorie']})"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.info(f"⏳ {r['temps']} | 👥 {r['personnes']} pers.")
                    # Calculateur automatique
                    ratio = st.number_input(f"Ajuster pour (personnes) :", min_value=1, value=r['personnes'], key=f"nb_{i}") / r['personnes']
                    st.write("**Ingrédients :**")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing['nom']} : {round(ing['quantite'] * ratio, 2)} {ing['unite']}")
                
                with col2:
                    st.write("**Processus de réalisation :**")
                    for j, etape in enumerate(r["etapes"]):
                        st.write(f"{j+1}. {etape}")
                    st.camera_input(f"Photo finale du plat (Gusto Cam)", key=f"cam_{i}")

elif choice == "➕ Ajouter une Recette":
    st.write("### Créer une nouvelle fiche technique")
    with st.form("new_recipe"):
        nom = st.text_input("Nom du plat")
        cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Accompagnement", "Sauce"])
        col_t, col_p = st.columns(2)
        temps = col_t.text_input("Temps (ex: 45 min)")
        pers = col_p.number_input("Nombre de personnes", min_value=1, value=4)
        
        st.write("---")
        st.write("Ingrédients (Séparez par des virgules : Nom, Quantité, Unité)")
        ing_text = st.text_area("Exemple: Farine, 500, g \nOeufs, 4, pcs", height=100)
        
        st.write("Processus (Une étape par ligne)")
        steps_text = st.text_area("Décrivez les étapes ici...", height=150)
        
        submitted = st.form_submit_button("Enregistrer la recette dans GUSTO")
        
        if submitted:
            # Traitement des ingrédients
            new_ings = []
            for line in ing_text.split('\n'):
                if ',' in line:
                    parts = line.split(',')
                    new_ings.append({"nom": parts[0].strip(), "quantite": float(parts[1].strip()), "unite": parts[2].strip()})
            
            new_recipe = {
                "nom": nom,
                "categorie": cat,
                "temps": temps,
                "personnes": pers,
                "ingredients": new_ings,
                "etapes": steps_text.split('\n')
            }
            st.session_state.db["Recettes"].append(new_recipe)
            save_data()
            st.success("Recette enregistrée !")

elif choice == "⚙️ Paramètres":
    st.write("### Administration")
    if st.button("Exporter la base de données (JSON)"):
        st.download_button("Télécharger", data=json.dumps(st.session_state.db), file_name="gusto_backup.json")



Envoyé depuis Yahoo Mail pour iPhone

dylan audrin
À :  moi
 · 
ven. 30 janv. à 12:16
Corps du message
import streamlit as st
import pandas as pd
import json
import os

# Configuration de la page
st.set_page_config(page_title="GUSTO - Fiches Techniques", layout="wide", page_icon="👨‍🍳")

# Style CSS personnalisé pour un look pro
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .recipe-card { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Initialisation de la base de données (Fichier JSON local)
DB_FILE = "gusto_recipes.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "Recettes": [
            {
                "nom": "Pâtes Carbonara (La Vraie)",
                "categorie": "Plat",
                "temps": "15 min",
                "personnes": 2,
                "ingredients": [{"nom": "Spaghetti", "quantite": 200, "unite": "g"}, {"nom": "Guanciale", "quantite": 100, "unite": "g"}, {"nom": "Jaunes d'œufs", "quantite": 4, "unite": "pcs"}, {"nom": "Pecorino Romano", "quantite": 50, "unite": "g"}],
                "etapes": ["Tailler le guanciale en dés.", "Mélanger œufs et fromage.", "Cuire les pâtes al dente.", "Mélanger hors du feu avec un peu d'eau de cuisson."]
            },
            {
                "nom": "Risotto aux Champignons",
                "categorie": "Plat",
                "temps": "30 min",
                "personnes": 4,
                "ingredients": [{"nom": "Riz Arborio", "quantite": 320, "unite": "g"}, {"nom": "Champignons", "quantite": 500, "unite": "g"}, {"nom": "Bouillon", "quantite": 1, "unite": "L"}],
                "etapes": ["Nacrer le riz avec des échalotes.", "Ajouter le bouillon louche après louche.", "Lier au beurre et parmesan en fin de cuisson."]
            },
            {
                "nom": "Gratin Dauphinois",
                "categorie": "Accompagnement",
                "temps": "1h15",
                "personnes": 6,
                "ingredients": [{"nom": "Pommes de terre", "quantite": 1.5, "unite": "kg"}, {"nom": "Crème liquide", "quantite": 50, "unite": "cl"}, {"nom": "Ail", "quantite": 2, "unite": "gousses"}],
                "etapes": ["Trancher les PDT finement à la mandoline.", "Frotter le plat avec l'ail.", "Disposer les tranches et verser la crème.", "Cuire à 160°C jusqu'à tendreté."]
            }
        ]
    }

if "db" not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f)

# --- INTERFACE ---
st.title("👨‍🍳 GUSTO")
st.subheader("Gestionnaire de Fiches Techniques")

menu = ["📖 Consulter le Livre", "➕ Ajouter une Recette", "⚙️ Paramètres"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "📖 Consulter le Livre":
    st.write("### Vos Recettes")
    search = st.text_input("Rechercher un plat ou un ingrédient...")
    
    for i, r in enumerate(st.session_state.db["Recettes"]):
        if search.lower() in r["nom"].lower():
            with st.expander(f"{r['nom']} ({r['categorie']})"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.info(f"⏳ {r['temps']} | 👥 {r['personnes']} pers.")
                    # Calculateur automatique
                    ratio = st.number_input(f"Ajuster pour (personnes) :", min_value=1, value=r['personnes'], key=f"nb_{i}") / r['personnes']
                    st.write("**Ingrédients :**")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing['nom']} : {round(ing['quantite'] * ratio, 2)} {ing['unite']}")
                
                with col2:
                    st.write("**Processus de réalisation :**")
                    for j, etape in enumerate(r["etapes"]):
                        st.write(f"{j+1}. {etape}")
                    st.camera_input(f"Photo finale du plat (Gusto Cam)", key=f"cam_{i}")

elif choice == "➕ Ajouter une Recette":
    st.write("### Créer une nouvelle fiche technique")
    with st.form("new_recipe"):
        nom = st.text_input("Nom du plat")
        cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Accompagnement", "Sauce"])
        col_t, col_p = st.columns(2)
        temps = col_t.text_input("Temps (ex: 45 min)")
        pers = col_p.number_input("Nombre de personnes", min_value=1, value=4)
        
        st.write("---")
        st.write("Ingrédients (Séparez par des virgules : Nom, Quantité, Unité)")
        ing_text = st.text_area("Exemple: Farine, 500, g \nOeufs, 4, pcs", height=100)
        
        st.write("Processus (Une étape par ligne)")
        steps_text = st.text_area("Décrivez les étapes ici...", height=150)
        
        submitted = st.form_submit_button("Enregistrer la recette dans GUSTO")
        
        if submitted:
            # Traitement des ingrédients
            new_ings = []
            for line in ing_text.split('\n'):
                if ',' in line:
                    parts = line.split(',')
                    new_ings.append({"nom": parts[0].strip(), "quantite": float(parts[1].strip()), "unite": parts[2].strip()})
            
            new_recipe = {
                "nom": nom,
                "categorie": cat,
                "temps": temps,
                "personnes": pers,
                "ingredients": new_ings,
                "etapes": steps_text.split('\n')
            }
            st.session_state.db["Recettes"].append(new_recipe)
            save_data()
            st.success("Recette enregistrée !")

elif choice == "⚙️ Paramètres":
    st.write("### Administration")
    if st.button("Exporter la base de données (JSON)"):
        st.download_button("Télécharger", data=json.dumps(st.session_state.db), file_name="gusto_backup.json")
