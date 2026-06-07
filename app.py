import streamlit as st
from vistas.vista_login import vista_login
from vistas.vista_administrador import vista_administrador
from vistas.vista_estudiante import vista_estudiante
from datos.conexion import engine
from datos.base import Base
import datos.tablas_sql 
from utils.semilla import poblar_base_de_datos

Base.metadata.create_all(bind=engine)
poblar_base_de_datos() # Se ejecuta e ignora si ya tiene datos

st.set_page_config(page_title="Universidad Aprende Más", page_icon="🎓", layout="wide")

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None
if "id_estudiante" not in st.session_state:
    st.session_state.id_estudiante = None

if not st.session_state.usuario_autenticado:
    vista_login()
else:
    col_user, col_logout = st.columns([0.85, 0.15])
    with col_logout:
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_autenticado = False
            st.session_state.rol_usuario = None
            st.session_state.id_estudiante = None
            st.rerun()
            
    if st.session_state.rol_usuario == "administrador":
        vista_administrador()
    elif st.session_state.rol_usuario == "estudiante":
        vista_estudiante()