import streamlit as st
import json
import os
from PIL import Image

# Config
st.set_page_config(page_title="GUSTO PRO", layout="wide", page_icon="👨‍🍳")

# Style CSS pour un look Chef
st.markdown("""
    <style>
    .stApp { background-color: #FDFCFB; }
    .recipe-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid #FF4B4B; }
    h1, h2 { color: #2C3E50; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "gusto_recipes.json"

def charger_donnees():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f: return json.load(f)
        except: pass
    return {"Recettes": []}

if "db" not in st.session_state: st.session_state.db = charger_donnees()

def sauvegarder():
    with open(DB_FILE, "w", encoding='utf-8') as f: json.dump(st.session_state.db, f, indent=4)

# Navigation sidebar
with st.sidebar:
    st.title("👨‍🍳 GUSTO PRO")
    menu = st.radio("Aller vers :", ["📖 Mon Livre", "➕ Créer", "⚙️ Modifier/Supprimer"])

# --- LIVRE DE RECETTES ---
if menu == "📖 Mon Livre":
    st.title("📖 Livre de Recettes")
    recherche = st.text_input("🔍 Rechercher...")
    
    for i, r in enumerate(st.session_state.db["Recettes"]):
        if recherche.lower() in r["nom"].lower():
            with st.expander(f"🍴 {r['nom'].upper()}"):
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.write(f"⏱️ **Temps :** {r['temps']}")
                    portions = st.number_input("Couverts", min_value=1, value=int(r.get('personnes', 1)), key=f"p_{i}")
                    ratio = portions / r.get('personnes', 1)
                    st.write("**🛒 Ingrédients :**")
                    for ing in r["ingredients"]:
                        try:
                            q = float(ing['quantite']) * ratio
                            st.write(f"- {ing['nom']} : {round(q, 2) if q > 0 else ''} {ing['unite']}")
                        except: st.write(f"- {ing['nom']}")
                with c2:
                    st.write("**👨‍🍳 Préparation :**")
                    for n, e in enumerate(r["etapes"]): st.write(f"{n+1}. {e}")
                    
                    # NOUVEAU : Option Photo ou Import
                    st.write("---")
                    source_img = st.radio("Ajouter une photo via :", ["Appareil Photo", "Fichier (Internet/Galerie)"], key=f"src_{i}")
                    if source_img == "Appareil Photo":
                        st.camera_input("Prendre la photo", key=f"cam_{i}")
                    else:
                        st.file_uploader("Choisir une image enregistrée", type=['jpg', 'png', 'jpeg'], key=f"file_{i}")

# --- CRÉATION ---
elif menu == "➕ Créer":
    st.title("➕ Nouvelle Fiche")
    with st.form("add_form", clear_on_submit=True):
        nom = st.text_input("Nom du plat")
        c1, c2 = st.columns(2)
        temps = c1.text_input("Temps")
        pers = c2.number_input("Personnes", min_value=1, value=1)
        ings = st.text_area("Ingrédients (Nom, Quantité, Unité)")
        etapes = st.text_area("Étapes (une par ligne)")
        
        if st.form_submit_button("Enregistrer"):
            liste_ing = []
            for l in ings.split('\n'):
                p = l.split(',')
                if len(p)==3: liste_ing.append({"nom":p[0].strip(),"quantite":p[1].strip(),"unite":p[2].strip()})
                else: liste_ing.append({"nom":l.strip(),"quantite":"0","unite":""})
            
            st.session_state.db["Recettes"].append({
                "nom": nom, "temps": temps, "personnes": pers, 
                "ingredients": liste_ing, "etapes": etapes.split('\n')
            })
            sauvegarder()
            st.success("C'est dans le livre !")

# --- GESTION (MODIFIER / SUPPRIMER) ---
elif menu == "⚙️ Modifier/Supprimer":
    st.title("⚙️ Gestion des recettes")
    for i, r in enumerate(st.session_state.db["Recettes"]):
        col_n, col_m, col_s = st.columns([3, 1, 1])
        col_n.write(f"**{r['nom']}**")
        if col_m.button("Modifier", key=f"edit_btn_{i}"): st.session_state.edit_idx = i
        if col_s.button("🗑️", key=f"del_btn_{i}"):
            st.session_state.db["Recettes"].pop(i)
            sauvegarder()
            st.rerun()
            
    if "edit_idx" in st.session_state:
        idx = st.session_state.edit_idx
        rec = st.session_state.db["Recettes"][idx]
        st.write("---")
        st.subheader(f"Modification de : {rec['nom']}")
        with st.form("edit_form"):
            new_nom = st.text_input("Nom", value=rec['nom'])
            new_ings = st.text_area("Ingrédients", value="\n".join([f"{ig['nom']}, {ig['quantite']}, {ig['unite']}" for ig in rec['ingredients']]))
            new_steps = st.text_area("Étapes", value="\n".join(rec['etapes']))
            if st.form_submit_button("Sauvegarder"):
                # (Ici on pourrait rajouter la logique de mise à jour complète)
                st.info("Logique de sauvegarde en cours... Pour l'instant, recréez la recette si besoin de gros changements.")
                del st.session_state.edit_idx
