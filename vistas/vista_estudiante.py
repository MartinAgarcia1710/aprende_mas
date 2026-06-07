import streamlit as st
from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Inscripcion, Nota, ComisionActividad
from datos.conexion_nosql import get_mongo_db
from datetime import datetime
from bson import ObjectId  # Necesario para operar con los IDs de MongoDB

def vista_estudiante():
    id_estudiante_actual = st.session_state.id_estudiante
    db = SessionLocal()
    
    alumno = db.query(Estudiante).filter(Estudiante.id_estudiante == id_estudiante_actual).first()
    
    if not alumno:
        st.error("Error crítico: No se encontraron los datos del estudiante logueado.")
        db.close()
        return

    st.markdown(f"<h2 style='color: #4F46E5;'>🎓 Portal del Alumno: {alumno.nombre} {alumno.apellido}</h2>", unsafe_allow_html=True)
    st.write(f"**Legajo:** {alumno.legajo}  |  **DNI:** {alumno.dni}  |  **Email:** {alumno.e_mail}")
    st.write("---")
    
    st.markdown("### 📚 Mis Cursos e Historial Académico")
    st.write("Asignaturas del periodo actual, calificaciones parciales y estado de actas finales.")

    mis_inscripciones = db.query(Inscripcion).filter(
        Inscripcion.id_estudiante == id_estudiante_actual,
        Inscripcion.activo == 1
    ).all()

    if not mis_inscripciones:
        st.info("Actualmente no registrás inscripciones activas en ninguna comisión.")
        db.close()
    else:
        # 1. RENDERIZADO DE LAS NOTAS RELACIONALES (Mantiene el formato original)
        for insc in mis_inscripciones:
            comision = insc.comision
            curso = comision.curso
            
            with st.container(border=True):
                col_info, col_final = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"#### 📘 {curso.nombre}")
                    st.caption(f"**Comisión:** #{comision.id_comision}  |  **Año:** {comision.anio}  |  **Semestre:** {comision.semestre}° Semestre")
                    st.write("**Calificaciones Parciales:**")
                    
                    mis_notas = db.query(Nota).filter(Nota.id_inscripcion == insc.id_inscripcion).all()
                    
                    if not mis_notas:
                        st.markdown("<p style='color: #6B7280; font-style: italic; font-size: 14px;'>Aún no se han registrado calificaciones parciales.</p>", unsafe_allow_html=True)
                    else:
                        for nota in mis_notas:
                            actividad_info = nota.comision_actividad
                            nombre_evaluacion = actividad_info.actividad.nombre
                            ponderacion = actividad_info.ponderacion_porcentaje
                            obs_texto = f" *(Feedback: {nota.observaciones})*" if nota.observaciones else ""
                            
                            st.markdown(
                                f"* 📌 **{nombre_evaluacion}** ({ponderacion}%): "
                                f"<span style='background-color: #EEF2F6; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>{nota.calificacion}</span>"
                                f"{obs_texto}", 
                                unsafe_allow_html=True
                            )
                
                with col_final:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.markdown("**Estado de Cursada**")
                    
                    if insc.nota_final:
                        st.markdown(
                            f"<div style='background-color: #DEF7EC; color: #03543F; padding: 15px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #84E1BC;'>"
                            f"{insc.nota_final}"
                            f"<div style='font-size: 12px; font-weight: normal; margin-top: 5px;'>CONSOLIDADA</div>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div style='background-color: #FEF08A; color: #713F12; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #FDE047;'>"
                            "Cursando"
                            "<div style='font-size: 11px; font-weight: normal; margin-top: 5px;'>ACTA ABIERTA</div>"
                            "</div>", 
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
        
        db.close() # Cerramos la conexión SQL de forma segura

        # ====================================================
        # SECCIÓN NOSQL: SEPARACIÓN DE AULAS POR SOLAPAS
        # ====================================================
        st.write("---")
        st.markdown("### 💬 Aulas Virtuales Compartidas (Espacio NoSQL)")
        st.write("Seleccioná la pestaña de la materia correspondiente para interactuar en el foro de debates.")

        # Creamos los nombres dinámicos para las solapas según los cursos activos del alumno
        nombres_solapas = [f"💬 {ins.comision.curso.nombre} (#{ins.id_comision})" for ins in mis_inscripciones]
        solapas_foros = st.tabs(nombres_solapas)

        # Conexión única a la base de datos documental
        mongo_db = get_mongo_db()
        coleccion = mongo_db['aprende_mas']

        # Mapeamos cada solapa a su inscripción respectiva
        for idx, solapa in enumerate(solapas_foros):
            insc_actual = mis_inscripciones[idx]
            comision_id = insc_actual.comision.id_comision
            
            with solapa:
                st.markdown(f"#### Foro de Discusión: {insc_actual.comision.curso.nombre}")
                
                # Buscamos en MongoDB los documentos que correspondan al ID de la comisión
                hilos = list(coleccion.find({"id_comision": comision_id}))
                
                # --- SUBFORMS 1: APERTURA DE UN NUEVO DEBATE ---
                with st.form(f"nuevo_hilo_{comision_id}"):
                    st.markdown("##### ➕ Abrir nuevo debate principal")
                    titulo = st.text_input("Título del debate", key=f"input_tit_{comision_id}")
                    mensaje = st.text_area("Tu consulta o aporte", key=f"input_txt_{comision_id}")
                    
                    if st.form_submit_button("Publicar en foro"):
                        if titulo and mensaje:
                            nuevo_documento = {
                                "id_comision": comision_id,
                                "titulo_hilo": titulo,
                                "contenido_principal": mensaje,
                                "creador": {"nombre": alumno.nombre, "apellido": alumno.apellido},
                                "fecha_creacion": datetime.now(),
                                "respuestas": []
                            }
                            coleccion.insert_one(nuevo_documento)
                            st.success("¡Hilo de debate abierto exitosamente!")
                            st.rerun()
                        else:
                            st.warning("Completá título y mensaje.")

                # --- VISUALIZACIÓN Y RESPUESTAS A HILOS EXISTENTES ---
                st.write("")
                st.markdown("##### 📋 Debates activos en esta comisión")
                if not hilos:
                    st.caption("No hay debates abiertos en esta materia.")
                else:
                    for hilo in hilos:
                        hilo_id_str = str(hilo['_id']) # Convertimos el ID de objeto de Mongo a String para los widgets
                        
                        with st.container(border=True):
                            st.markdown(f"**📌 {hilo['titulo_hilo']}**")
                            st.markdown(f"<p style='font-size: 14px; color: #374151; margin-bottom:2px;'>{hilo['contenido_principal']}</p>", unsafe_allow_html=True)
                            st.caption(f"Iniciado por: {hilo['creador']['apellido']}, {hilo['creador']['nombre']}")
                            
                            # Renderizado del historial de respuestas guardadas en el JSON
                            if hilo.get('respuestas'):
                                st.markdown("<p style='font-size: 13px; font-weight: bold; color: #4F46E5; margin-top:10px;'>Respuestas:</p>", unsafe_allow_html=True)
                                for r in hilo['respuestas']:
                                    st.markdown(
                                        f"<div style='background-color: #F9FAFB; padding: 8px; border-radius: 4px; margin-bottom: 5px; border-left: 3px solid #6366F1;'>"
                                        f"<span style='font-size: 12px; font-weight: bold; color: #4B5563;'>{r['autor']}:</span> "
                                        f"<span style='font-size: 13px; color: #1F2937;'>{r['mensaje']}</span>"
                                        f"</div>", 
                                        unsafe_allow_html=True
                                    )
                            
                            # --- SUBFORMS 2: FORMULARIO INCRUSTADO PARA RESPONDER ---
                            with st.form(f"form_resp_{hilo_id_str}"):
                                txt_respuesta = st.text_input("Añadir un comentario al debate...", placeholder="Escribí tu respuesta acá...", key=f"r_txt_{hilo_id_str}")
                                if st.form_submit_button("Responder"):
                                    if txt_respuesta:
                                        # Estructura de la respuesta embebida
                                        nueva_respuesta = {
                                            "autor": f"{alumno.nombre} {alumno.apellido}",
                                            "mensaje": txt_respuesta,
                                            "fecha": datetime.now()
                                        }
                                        # Operación NoSQL: Inyectamos el objeto dentro del array 'respuestas' usando el ID del hilo
                                        coleccion.update_one(
                                            {"_id": ObjectId(hilo_id_str)},
                                            {"$push": {"respuestas": nueva_respuesta}}
                                        )
                                        st.success("Respuesta guardada.")
                                        st.rerun()
                                    else:
                                        st.warning("El mensaje no puede estar vacío.")