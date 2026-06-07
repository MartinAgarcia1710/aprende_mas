'''
import streamlit as st
from datos.conexion import SessionLocal
from datos.tablas_sql import UsuarioSistema

def vista_login():
    # Centrar el contenedor del login estéticamente
    _, col_centro, _ = st.columns([1, 1.2, 1])
    
    with col_centro:
        st.markdown("<h1 style='text-align: center; color: #4F46E5;'>🎓 Universidad Aprende Más</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Portal de Gestión Académica - MVP</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("Iniciar Sesión")
            
            username = st.text_input("Usuario", placeholder="Ej: admin o alumno")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            if st.button("Ingresar", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Por favor, completa todos los campos.")
                else:
                    # Validar credenciales contra SQLite
                    db = SessionLocal()
                    usuario = db.query(UsuarioSistema).filter(
                        UsuarioSistema.username == username,
                        UsuarioSistema.password_hash == password # Manejo lineal para el MVP
                    ).first()
                    db.close()
                    
                    if usuario:
                        # Guardar el estado de la sesión
                        st.session_state.usuario_autenticado = True
                        st.session_state.rol_usuario = usuario.rol
                        st.session_state.id_estudiante = usuario.id_estudiante
                        st.success(f"¡Bienvenido, {username}!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
'''

import streamlit as st
from datos.conexion import SessionLocal
from datos.tablas_sql import UsuarioSistema
from utils.seguridad import generar_hash

def vista_login():
    # Centrar el contenedor del login estéticamente
    _, col_centro, _ = st.columns([1, 1.2, 1])
    
    with col_centro:
        st.markdown("<h1 style='text-align: center; color: #4F46E5;'>🎓 Universidad Aprende Más</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Portal de Gestión Académica - MVP</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("Iniciar Sesión")
            
            username = st.text_input("Usuario", placeholder="Ej: admin o ricardo")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            if st.button("Ingresar", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Por favor, completa todos los campos.")
                else:
                    db = SessionLocal()
                    
                    # --- AQUÍ ESTÁ LA CLAVE: Ciframos la contraseña ingresada en el input ---
                    password_hasheada = generar_hash(password)
                    
                    # Consultamos comparando el hash calculado contra el guardado por la semilla
                    usuario = db.query(UsuarioSistema).filter(
                        UsuarioSistema.username == username,
                        UsuarioSistema.password_hash == password_hasheada
                    ).first()
                    db.close()
                    
                    if usuario:
                        # Guardar el estado seguro en la sesión de Streamlit
                        st.session_state.usuario_autenticado = True
                        st.session_state.rol_usuario = usuario.rol
                        st.session_state.id_estudiante = usuario.id_estudiante
                        st.success(f"¡Bienvenido, {username}!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")