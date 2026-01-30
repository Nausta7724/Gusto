import streamlit as st
import json
import os

st.set_page_config(page_title="GUSTO", layout="wide", page_icon="👨‍🍳")

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

st.title("👨‍🍳 GUSTO")
menu = ["📖 Livre de Recettes", "➕ Ajouter une Recette"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "📖 Livre de Recettes":
    recherche = st.text_input("🔍 Rechercher...")
    if not st.session_state.db["Recettes"]:
        st.info("Le livre est vide.")
    else:
        for i, r in enumerate(st.session_state.db["Recettes"]):
            if recherche.lower() in r["nom"].lower():
                with st.expander(f"🍴 {r['nom'].upper()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"⏱️ **Temps :** {r['temps']}")
                        # Gestion du nombre de personnes par défaut si absent
                        nb_pers_base = r.get('personnes', 1)
                        if nb_pers_base < 1: nb_pers_base = 1
                        
                        portions = st.number_input("Portions", min_value=1, value=int(nb_pers_base), key=f"p_{i}")
                        ratio = portions / nb_pers_base
                        
                        st.write("**Ingrédients :**")
                        for ing in r["ingredients"]:
                            try:
                                # On essaie de calculer si c'est un chiffre, sinon on affiche tel quel
                                q_val = float(ing['quantite'])
                                q_aff = round(q_val * ratio, 2) if q_val > 0 else ""
                                unite_aff = ing['unite'] if ing['unite'] else ""
                                st.write(f"- {ing['nom']} : {q_aff} {unite_aff}")
                            except:
                                st.write(f"- {ing['nom']} {ing['quantite']} {ing['unite']}")
                    
                    with col2:
                        st.write("**Processus :**")
                        for n, etape in enumerate(r["etapes"]):
                            st.write(f"{n+1}. {etape}")
                        st.camera_input("Photo", key=f"cam_{i}")
                    
                    if st.button("Supprimer cette recette", key=f"del_{i}"):
                        st.session_state.db["Recettes"].pop(i)
                        sauvegarder()
                        st.rerun()

elif choix == "➕ Ajouter une Recette":
    with st.form("form_recette", clear_on_submit=True):
        nom = st.text_input("Nom du plat")
        cat = st.selectbox("Catégorie", ["Entrée", "Plat", "Dessert", "Autre"])
        col1, col2 = st.columns(2)
        temps = col1.text_input("Temps (ex: 20 min)")
        pers = col2.number_input("Nombre de personnes", min_value=1, value=1)
        
        st.write("**Ingrédients**")
        st.caption("Astuce : Vous pouvez écrire 'Sel' ou 'Farine, 500, g'")
        ing_bruts = st.text_area("Liste des ingrédients (un par ligne)")
        
        st.write("**Processus**")
        etapes_brutes = st.text_area("Étapes de la recette")
        
        if st.form_submit_button("Enregistrer dans GUSTO"):
            liste_ing = []
            for ligne in ing_bruts.split('\n'):
                if ligne.strip():
                    parts = ligne.split(',')
                    if len(parts) == 3:
                        liste_ing.append({"nom": parts[0].strip(), "quantite": parts[1].strip(), "unite": parts[2].strip()})
                    elif len(parts) == 2:
                        liste_ing.append({"nom": parts[0].strip(), "quantite": parts[1].strip(), "unite": ""})
                    else:
                        # Si aucune virgule, on met tout dans le nom
                        liste_ing.append({"nom": ligne.strip(), "quantite": "0", "unite": ""})
            
            st.session_state.db["Recettes"].append({
                "nom": nom, "categorie": cat, "temps": temps, "personnes": pers,
                "ingredients": liste_ing, "etapes": [e.strip() for e in etapes_brutes.split('\n') if e.strip()]
            })
            sauvegarder()
            st.success("Recette enregistrée !")
