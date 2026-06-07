import streamlit as st
from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Inscripcion, Nota, ComisionActividad

def vista_estudiante():
    # Recuperamos el ID del estudiante logueado desde el estado de la sesión
    id_estudiante_actual = st.session_state.id_estudiante

    db = SessionLocal()
    
    # Traemos los datos personales del alumno
    alumno = db.query(Estudiante).filter(Estudiante.id_estudiante == id_estudiante_actual).first()
    
    if not alumno:
        st.error("Error crítico: No se encontraron los datos del estudiante logueado.")
        db.close()
        return

    # Encabezado personalizado y vanguardista
    st.markdown(f"<h2 style='color: #4F46E5;'>🎓 Portal del Alumno: {alumno.nombre} {alumno.apellido}</h2>", unsafe_allow_html=True)
    st.write(f"**Legajo:** {alumno.legajo}  |  **DNI:** {alumno.dni}  |  **Email:** {alumno.e_mail}")
    st.write("---")
    
    st.markdown("### 📚 Mis Cursos e Historial Académico")
    st.write("A continuación se detallan las asignaturas en las que te encontrás inscrito para el periodo actual, junto con tus calificaciones parciales y el estado de tu nota final.")

    # Buscamos todas las inscripciones activas del estudiante
    mis_inscripciones = db.query(Inscripcion).filter(
        Inscripcion.id_estudiante == id_estudiante_actual,
        Inscripcion.activo == 1
    ).all()

    if not mis_inscripciones:
        st.info("Actualmente no registrás inscripciones activas en ninguna comisión.")
    else:
        # Iteramos por cada materia/comisión en la que está anotado
        for insc in mis_inscripciones:
            comision = insc.comision
            curso = comision.curso
            
            # Contenedor estético para separar las materias
            with st.container(border=True):
                col_info, col_final = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"#### 📘 {curso.nombre}")
                    st.caption(f"**Comisión:** #{comision.id_comision}  |  **Año:** {comision.anio}  |  **Semestre:** {comision.semestre}° Semestre")
                    
                    st.write("**Calificaciones Parciales:**")
                    
                    # Buscamos las notas parciales cargadas para esta inscripción
                    mis_notas = db.query(Nota).filter(Nota.id_inscripcion == insc.id_inscripcion).all()
                    
                    if not mis_notas:
                        st.markdown("<p style='color: #6B7280; font-style: italic; font-size: 14px;'>Aún no se han registrado calificaciones parciales para esta asignatura.</p>", unsafe_allow_html=True)
                    else:
                        # Mostramos las notas en un formato de lista limpio con su feedback si existe
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
                
                # Sección derecha con el estado de la Nota Final (Cierre de Acta)
                with col_final:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.markdown("**Estado de Cursada**")
                    
                    if insc.nota_final:
                        # Si el acta ya fue cerrada por el Administrador/Docente
                        st.markdown(
                            f"<div style='background-color: #DEF7EC; color: #03543F; padding: 15px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #84E1BC;'>"
                            f"{insc.nota_final}"
                            f"<div style='font-size: 12px; font-weight: normal; margin-top: 5px;'>CONSOLIDADA</div>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                        
                        # Mensaje opcional según la nota (aprobado / desaprobado)
                        if float(insc.nota_final) >= 4.0:
                            st.markdown("<p style='color: #03543F; font-size: 12px; text-align: center; font-weight: bold; margin-top: 5px;'>🎉 ¡Asignatura Aprobada!</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='color: #9B1C1C; font-size: 12px; text-align: center; font-weight: bold; margin-top: 5px;'>❌ Condición: Recursar</p>", unsafe_allow_html=True)
                    else:
                        # Si todavía está cursando y no se ejecutó la transacción de cierre
                        st.markdown(
                            "<div style='background-color: #FEF08A; color: #713F12; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #FDE047;'>"
                            "Cursando"
                            "<div style='font-size: 11px; font-weight: normal; margin-top: 5px;'>ACTA ABIERTA</div>"
                            "</div>", 
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

    db.close()