# --- LAYOUT PRINCIPAL ---
st.title("🎧 Campus Relation Client")
st.write("Bienvenue dans le simulateur pédagogique CRCD.")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Où voulez-vous aller ?",
        ["Accueil", "Simulateur", "Glossaire"]
    )
    st.session_state.page = page.lower()

# --- ROUTAGE DES PAGES ---
if st.session_state.page == "accueil":
    st.subheader("Page d'accueil")
    st.markdown(
        "Commencez par choisir un scénario dans la barre latérale "
        "ou ouvrez le guide rapide."
    )

    if st.button("📘 Afficher le guide rapide"):
        afficher_notice()

elif st.session_state.page == "simulateur":
    st.subheader("Simulateur d'appel (prototype)")
    st.info(
        "L'interface de simulation vocale (micro, client, analyse CRCD) "
        "sera intégrée ici."
    )

elif st.session_state.page == "glossaire":
    st.subheader("Glossaire")
    if 'GLOSSAIRE' in globals():
        for terme, definition in GLOSSAIRE.items():
            st.markdown(f"**{terme}** : {definition}")
    else:
        st.warning("Le glossaire n'est pas disponible.")

# --- FOOTER ---
afficher_footer()
