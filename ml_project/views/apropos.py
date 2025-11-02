import streamlit as st
import os
import base64

def show_page():

    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style='text-align:center;'>
            <img src='data:image/png;base64,{logo_base64}' width='180'>
            <h1 style='color:#2ecc71; font-size:42px; font-weight:900;'>
                💡 À propos du projet DPE
            </h1>
            <p style='color:#bbbbbb; font-style:italic; font-size:17px;'>
                Application interactive de visualisation et simulation de la performance énergétique des logements.
            </p>
            <hr style='border:1px solid #333; width:80%; margin:auto; margin-bottom:25px;'>
        </div>
    """, unsafe_allow_html=True)

    # Présentation du projet

    st.markdown("""
        <p style='color:#cccccc; text-align:justify; max-width:900px; margin:auto; line-height:1.6;'>
            Ce projet a été développé dans le cadre du module <b>Machine Learning</b> du Master SISE — 
            Statistique et Informatique pour la Science des Données à l’Université Lumière Lyon 2.
            <br><br>
            L’objectif est de proposer une application complète permettant d’explorer et de comprendre la 
            <b>performance énergétique des logements (DPE)</b> à travers différentes analyses et visualisations.
        </p>

        <div style='text-align:center; margin-top:15px;'>
            <ul style='list-style-position: inside; text-align:left; display:inline-block; color:#ddd; font-size:16px; line-height:1.8;'>
                <li><b>Analyse descriptive :</b> exploration statistique des variables du dataset.</li>
                <li><b>Cartographie :</b> visualisation géographique des logements selon leur classe DPE.</li>
                <li><b>Prédiction :</b> simulation de la classe énergétique et de la consommation à partir de données saisies.</li>
                <li><b>À propos :</b> présentation du projet, de l’équipe et des outils utilisés.</li>
            </ul>
        </div>

        <p style='color:#cccccc; text-align:center; max-width:900px; margin:25px auto; line-height:1.6;'>
            Ce travail met en avant les compétences en <b>data science</b>, 
            <b>visualisation de données</b> et <b>développement d’interfaces interactives</b> avec Streamlit.
        </p>
    """, unsafe_allow_html=True)

    # ÉQUIPE DU PROJET 

    st.markdown("""
        <h2 style='color:#2ecc71; text-align:center; font-weight:900; margin-top:50px;'>Équipe du projet</h2>
        <hr style='width:50%; margin:auto; border:1px solid rgba(255,255,255,0.2); margin-bottom:40px;'>
        <style>
            .team-avatar {
                border-radius: 50%;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .team-avatar:hover {
                transform: scale(1.08);
                box-shadow: 0 0 20px rgba(241, 196, 15, 0.4);
            }
            .member-name {
                color:#f1c40f; 
                font-weight:900;
                font-size:20px;
                margin-top:10px;
            }
            .member-role {
                color:#ccc;
                font-size:15px;
                line-height:1.5;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div style='text-align:center;'>
                <img class='team-avatar' src='https://cdn-icons-png.flaticon.com/512/4140/4140048.png' width='120'>
                <div class='member-name'>Personne 1</div>
                <div class='member-role'>
                    Développeuse de l'application<br>
                    Interface & intégration Streamlit
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='text-align:center;'>
                <img class='team-avatar' src='https://cdn-icons-png.flaticon.com/512/4140/4140047.png' width='120'>
                <div class='member-name'>Personne 2</div>
                <div class='member-role'>
                    Cheffe de projet<br>
                    Coordination & gestion du planning
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style='text-align:center;'>
                <img class='team-avatar' src='https://cdn-icons-png.flaticon.com/512/4140/4140037.png' width='120'>
                <div class='member-name'>Personne 3</div>
                <div class='member-role'>
                    Data Scientist<br>
                    Préparation des données & modélisation
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Technologies utilisées
    st.markdown("""
        <h2 style='color:#f39c12; text-align:center; font-weight:900; margin-top:60px;'>⚙️ Technologies utilisées</h2>
        <div style='text-align:center; margin-top:20px;'>
            <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg' width='70'>
            <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg' width='70'>
            <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg' width='70'>
            <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/plotly/plotly-original.svg' width='70'>
            <img src='https://streamlit.io/images/brand/streamlit-mark-color.png' width='70'>
        </div>
        <p style='color:#cccccc; text-align:center; margin-top:15px;'>
            Python • Pandas • NumPy • Plotly • Streamlit
        </p>
    """, unsafe_allow_html=True)

    # Objectifs futurs
    
    st.markdown("""
        <h2 style='color:#f1c40f; text-align:center; font-weight:900; margin-top:50px;'>Objectifs futurs</h2>
        <p style='color:#cccccc; text-align:center; max-width:900px; margin:auto; line-height:1.6;'>
            Les prochaines étapes du projet sont encore à définir.<br>
            Plusieurs pistes sont envisageables : intégration d’un modèle prédictif réel, amélioration de l’expérience utilisateur,<br>
            ou extension des fonctionnalités de visualisation.<br><br>
            <b>... à voir</b>
        </p>
    """, unsafe_allow_html=True)

    # Liens utiles 
    
    st.markdown("""
        <h2 style='color:#3498db; text-align:center; font-weight:900; margin-top:50px;'>🌐 Liens utiles</h2>
        <div style='text-align:center;'>
            <a href='https://github.com/personne1' target='_blank' 
               style='color:#f1c40f; font-size:18px; text-decoration:none; font-weight:700;'>
               🔗 GitHub - Personne 1
            </a><br>
            <a href='https://github.com/personne2' target='_blank' 
               style='color:#f1c40f; font-size:18px; text-decoration:none; font-weight:700;'>
               🔗 GitHub - Personne 2
            </a><br>
            <a href='https://github.com/personne3' target='_blank' 
               style='color:#f1c40f; font-size:18px; text-decoration:none; font-weight:700;'>
               🔗 GitHub - Personne 3
            </a><br><br>
            <a href='https://www.streamlit.io' target='_blank'
               style='color:#2ecc71; font-size:17px; text-decoration:none;'>
               🌍 Framework : Streamlit
            </a>
        </div>

        <hr style='border:1px solid rgba(255,255,255,0.1); margin-top:50px;'>
        <p style='text-align:center; color:#999; font-size:14px; font-style:italic;'>
            Projet réalisé dans le cadre du module <b>Machine Learning</b> — Master SISE, Université Lumière Lyon 2 (2025)
        </p>
    """, unsafe_allow_html=True)
