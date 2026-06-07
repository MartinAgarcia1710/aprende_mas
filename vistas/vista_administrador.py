import streamlit as st
from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Curso, ActividadEvaluativa, Comision, ComisionActividad, Inscripcion, Nota, UsuarioSistema
from datetime import date

def vista_administrador():
    st.markdown("<h2 style='color: #4F46E5;'>💼 Panel de Control Administrativo (Senior)</h2>", unsafe_allow_html=True)
    st.write("Ecosistema modular de gestión académica de la Universidad Aprende Más.")
    st.write("---")

    tab_cursos, tab_actividades, tab_estudiantes, tab_inscripciones, tab_notas = st.tabs([
        "📚 Oferta Académica", 
        "⚙️ Catálogo Actividades",
        "👨‍🎓 Alumnos", 
        "📝 Inscripciones", 
        "📊 Gestión de Actas"
    ])

    # ====================================================
    # PESTAÑA 1: GESTIÓN DE CURSOS Y COMISIONES (CRUD)
    # ====================================================
    with tab_cursos:
        db = SessionLocal()
        st.subheader("Administración de Materias y Comisiones")
        
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("➕ Dar de Alta Curso", expanded=False):
                n_nom = st.text_input("Nombre de la Materia", key="c_n_nom")
                if st.button("Guardar Curso Petición", type="primary"):
                    if n_nom:
                        try:
                            db.add(Curso(nombre=n_nom, activo=1))
                            db.commit()
                            st.success(f"Curso '{n_nom}' creado.")
                            st.rerun()
                        except:
                            db.rollback()
                            st.error("Ya existe o hubo un error.")
            
            st.markdown("#### Listado de Cursos")
            todos_cursos = db.query(Curso).all()
            for c in todos_cursos:
                estado = "🟢 Activo" if c.activo == 1 else "🔴 Inactivo"
                col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
                col_c1.write(f"**{c.nombre}** ({estado})")
                
                # Modificar Estado (Baja Lógica)
                if c.activo == 1:
                    if col_c2.button("Desactivar", key=f"bl_c_{c.id_curso}", use_container_width=True):
                        c.activo = 2
                        db.commit()
                        st.rerun()
                else:
                    if col_c2.button("Activar", key=f"al_c_{c.id_curso}", use_container_width=True):
                        c.activo = 1
                        db.commit()
                        st.rerun()
                
                # Baja Física
                if col_c3.button("🗑️ Borrar", key=f"bf_c_{c.id_curso}", use_container_width=True):
                    try:
                        db.delete(c)
                        db.commit()
                        st.rerun()
                    except:
                        db.rollback()
                        st.error("No se puede borrar (Tiene relaciones activas).")

        with c2:
            with st.expander("➕ Abrir Nueva Comisión", expanded=False):
                cursos_ok = db.query(Curso).filter(Curso.activo == 1).all()
                dict_c = {cc.nombre: cc.id_curso for cc in cursos_ok}
                if dict_c:
                    m_sel = st.selectbox("Asignatura", list(dict_c.keys()), key="com_m_sel")
                    anio = st.number_input("Año", value=2026, key="com_anio")
                    sem = st.selectbox("Semestre", [1, 2], key="com_sem")
                    cupo = st.number_input("Cupo", value=30, key="com_cupo")
                    f_i = st.date_input("Inicio", date.today(), key="com_fi")
                    f_f = st.date_input("Fin", date.today(), key="com_ff")
                    
                    # --- CONFIGURACIÓN DINÁMICA DE ACTIVIDADES AL CREAR LA COMISIÓN ---
                    st.markdown("##### Planificación de Ponderaciones")
                    activs = db.query(ActividadEvaluativa).filter(ActividadEvaluativa.activo == 1).all()
                    
                    valores_ponderacion = {}
                    for act in activs:
                        valores_ponderacion[act.id_actividad] = st.number_input(
                            f"Porcentaje para: {act.nombre}", min_value=0.0, max_value=100.0, step=5.0, value=0.0, key=f"p_inst_{act.id_actividad}"
                        )
                    
                    if st.button("Crear Comisión y Planificar", type="primary"):
                        suma_p = sum(valores_ponderacion.values())
                        if suma_p != 100.0:
                            st.error(f"La suma de ponderaciones debe ser exactamente 100%. Actual: {suma_p}%")
                        else:
                            try:
                                nueva_com = Comision(fecha_inicio=f_i, fecha_fin=f_f, anio=anio, semestre=sem, cantidad_maxima=cupo, id_curso=dict_c[m_sel])
                                db.add(nueva_com)
                                db.flush()
                                
                                # Guardar ponderaciones planificadas
                                for id_act, porc in valores_ponderacion.items():
                                    if porc > 0:
                                        db.add(ComisionActividad(id_comision=nueva_com.id_comision, id_actividad=id_act, ponderacion_porcentaje=porc))
                                db.commit()
                                st.success("Comisión creada y planificada de forma consistente.")
                                st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"Error: {e}")
                else:
                    st.info("No hay asignaturas activas.")
            
            st.markdown("#### Comisiones Existentes")
            todas_com = db.query(Comision).all()
            for co in todas_com:
                col_co1, col_co2 = st.columns([3, 1])
                col_co1.write(f"**ID #{co.id_comision}** - {co.curso.nombre} ({co.anio}-S{co.semestre})")
                if col_co2.button("Eliminar", key=f"bf_co_{co.id_comision}", use_container_width=True):
                    try:
                        # Borrar la planificación asociada primero
                        db.query(ComisionActividad).filter(ComisionActividad.id_comision == co.id_comision).delete()
                        db.delete(co)
                        db.commit()
                        st.rerun()
                    except:
                        db.rollback()
                        st.error("Posee alumnos inscriptos.")
        db.close()

    # ====================================================
    # PESTAÑA 2: CRUD DICCIONARIO ACTIVIDADES EVALUATIVAS
    # ====================================================
    with tab_actividades:
        db = SessionLocal()
        st.subheader("Catálogo Global de Tipos de Evaluación")
        
        col_act1, col_act2 = st.columns([1, 1.5])
        with col_act1:
            st.markdown("#### Nueva Actividad")
            n_act_nom = st.text_input("Concepto (Ej: Examen Parcial, TP)", key="n_act_nom")
            if st.button("Registrar Tipo", type="primary"):
                if n_act_nom:
                    try:
                        db.add(ActividadEvaluativa(nombre=n_act_nom, activo=1))
                        db.commit()
                        st.success("Registrado.")
                        st.rerun()
                    except:
                        db.rollback()
                        st.error("Ya existe.")
        
        with col_act2:
            st.markdown("#### Tipos Registrados")
            acts = db.query(ActividadEvaluativa).all()
            for a in acts:
                ca1, ca2, ca3 = st.columns([2, 1, 1])
                est_a = "🟢" if a.activo == 1 else " </br>🔴"
                ca1.write(f"{est_a} **{a.nombre}**")
                
                if a.activo == 1:
                    if ca2.button("Desactivar", key=f"bl_a_{a.id_actividad}"):
                        a.activo = 2
                        db.commit()
                        st.rerun()
                else:
                    if ca2.button("Activar", key=f"al_a_{a.id_actividad}"):
                        a.activo = 1
                        db.commit()
                        st.rerun()
                        
                if ca3.button("Borrar", key=f"bf_a_{a.id_actividad}"):
                    try:
                        db.delete(a)
                        db.commit()
                        st.rerun()
                    except:
                        db.rollback()
                        st.error("En uso.")
        db.close()

    # ====================================================
    # PESTAÑA 3: CRUD DE ESTUDIANTES
    # ====================================================
    with tab_estudiantes:
        db = SessionLocal()
        st.subheader("Gestión Integral de Alumnos")
        
        with st.expander("➕ Matricular Nuevo Estudiante", expanded=False):
            with st.form("f_est", clear_on_submit=True):
                f1, f2 = st.columns(2)
                nom = f1.text_input("Nombre")
                ape = f1.text_input("Apellido")
                mail = f1.text_input("Email")
                tel = f1.text_input("Teléfono")
                dni = f2.text_input("DNI")
                leg = f2.number_input("Legajo", min_value=1000, value=1005)
                usr = f2.text_input("Username")
                pwd = f2.text_input("Password", type="password")
                
                if st.form_submit_button("Guardar Registro"):
                    try:
                        ne = Estudiante(nombre=nom, apellido=ape, e_mail=mail, dni=dni, legajo=leg, telefono=tel if tel else None, activo=1)
                        db.add(ne)
                        db.flush()
                        db.add(UsuarioSistema(username=usr, password_hash=pwd, rol="estudiante", id_estudiante=ne.id_estudiante))
                        db.commit()
                        st.success("Matriculado con éxito.")
                        st.rerun()
                    except Exception as ex:
                        db.rollback()
                        st.error(f"Clave duplicada o error: {ex}")
        
        st.markdown("#### Alumnos en Sistema")
        alumnos_todos = db.query(Estudiante).all()
        for al in alumnos_todos:
            col_al1, col_al2, col_al3 = st.columns([3, 1, 1])
            est_al = "🟢" if al.activo == 1 else "🔴"
            col_al1.write(f"{est_al} **{al.apellido}, {al.nombre}** (Legajo: {al.legajo} | DNI: {al.dni})")
            
            if al.activo == 1:
                if col_al2.button("Desactivar", key=f"bl_al_{al.id_estudiante}"):
                    al.activo = 2
                    db.commit()
                    st.rerun()
            else:
                if col_al2.button("Activar", key=f"al_al_{al.id_estudiante}"):
                    al.activo = 1
                    db.commit()
                    st.rerun()
                    
            if col_al3.button("Eliminar", key=f"bf_al_{al.id_estudiante}"):
                try:
                    db.query(UsuarioSistema).filter(UsuarioSistema.id_estudiante == al.id_estudiante).delete()
                    db.delete(al)
                    db.commit()
                    st.rerun()
                except:
                    db.rollback()
                    st.error("Tiene inscripciones vigentes.")
        db.close()

    # ====================================================
    # PESTAÑA 4: ASIGNACIÓN DE INSCRIPCIONES
    # ====================================================
    with tab_inscripciones:
        db = SessionLocal()
        st.subheader("Inscripciones del Periodo")
        
        col_in1, col_in2 = st.columns([1, 2])
        with col_in1:
            estuds = db.query(Estudiante).filter(Estudiante.activo == 1).all()
            coms = db.query(Comision).all()
            
            d_est = {f"{e.apellido}, {e.nombre} ({e.legajo})": e.id_estudiante for e in estuds}
            d_com = {f"Com #{c.id_comision} - {c.curso.nombre}": c.id_comision for c in coms}
            
            if d_est and d_com:
                e_s = st.selectbox("Estudiante", list(d_est.keys()), key="ins_es")
                c_s = st.selectbox("Comisión Oferta", list(d_com.keys()), key="ins_cs")
                if st.button("Efectuar Inscripción", type="primary", use_container_width=True):
                    id_e = d_est[e_s]
                    id_c = d_com[c_s]
                    
                    rep = db.query(Inscripcion).filter(Inscripcion.id_estudiante == id_e, Inscripcion.id_comision == id_c).first()
                    if rep:
                        st.error("Ya está inscrito.")
                    else:
                        db.add(Inscripcion(id_estudiante=id_e, id_comision=id_c, fecha=date.today(), activo=1))
                        db.commit()
                        st.success("Inscrito.")
                        st.rerun()
        
        with col_in2:
            st.markdown("#### Historial de Inscripciones")
            ins_list = db.query(Inscripcion).all()
            for ins in ins_list:
                ci1, ci2 = st.columns([3, 1])
                ci1.write(f"🔹 **{ins.estudiante.apellido}** en *{ins.comision.curso.nombre}* (Com: #{ins.id_comision})")
                if ci2.button("Dar de Baja", key=f"bf_in_{ins.id_inscripcion}"):
                    db.delete(ins)
                    db.commit()
                    st.rerun()
        db.close()

    # ====================================================
    # PESTAÑA 5: NOTAS Y CIERRE DE ACTAS (CONTROL TOTAL)
    # ====================================================
    with tab_notas:
        db = SessionLocal()
        st.subheader("Seguimiento de Calificaciones por Comisión")
        
        coms_eval = db.query(Comision).all()
        d_com_eval = {f"Comisión #{c.id_comision} - {c.curso.nombre} ({c.anio}-S{c.semestre})": c.id_comision for c in coms_eval}
        
        if d_com_eval:
            com_seleccionada = st.selectbox("Seleccionar Comisión para Visualizar Planilla", list(d_com_eval.keys()))
            id_com_v = d_com_eval[com_seleccionada]
            
            # Traer alumnos e instancias planificadas
            alumnos_inscriptos = db.query(Inscripcion).filter(Inscripcion.id_comision == id_com_v, Inscripcion.activo == 1).all()
            plan_actividades = db.query(ComisionActividad).filter(ComisionActividad.id_comision == id_com_v).all()
            
            if alumnos_inscriptos and plan_actividades:
                
                # --- CARGA INDIVIDUAL DE NOTAS PARCIALES ---
                with st.expander("📝 Cargar Calificación Parcial", expanded=False):
                    nc1, nc2, nc3 = st.columns(3)
                    d_al_nota = {f"{i.estudiante.apellido}, {i.estudiante.nombre}": i.id_inscripcion for i in alumnos_inscriptos}
                    d_pl_nota = {f"{p.actividad.nombre} ({p.ponderacion_porcentaje}%)": p.id_comision_actividad for p in plan_actividades}
                    
                    al_sel = nc1.selectbox("Alumno", list(d_al_nota.keys()))
                    ac_sel = nc2.selectbox("Instancia", list(d_pl_nota.keys()))
                    cal_n = nc3.number_input("Nota", min_value=1, max_value=10, value=7)
                    ob_n = st.text_input("Feedback / Observación")
                    
                    if st.button("Asentar Nota Parcial", use_container_width=True):
                        id_ins = d_al_nota[al_sel]
                        id_ca = d_pl_nota[ac_sel]
                        
                        ya_existe = db.query(Nota).filter(Nota.id_inscripcion == id_ins, Nota.id_comision_actividad == id_ca).first()
                        if ya_existe:
                            st.warning("Esta instancia ya fue calificada para este alumno.")
                        else:
                            db.add(Nota(calificacion=cal_n, observaciones=ob_n if ob_n else None, id_inscripcion=id_ins, id_comision_actividad=id_ca))
                            db.commit()
                            st.success("Nota cargada.")
                            st.rerun()

                st.write("---")
                st.markdown("### 📋 Planilla de Calificaciones Vigente")
                
                # Renderizar registros detallados de cada estudiante
                for ins in alumnos_inscriptos:
                    with st.container(border=True):
                        col_r1, col_r2 = st.columns([3, 1])
                        
                        with col_r1:
                            st.markdown(f"👤 **{ins.estudiante.apellido}, {ins.estudiante.nombre}** (Legajo: {ins.estudiante.legajo})")
                            
                            # Mostrar notas parciales que tiene cargadas
                            notas_cargadas = db.query(Nota).filter(Nota.id_inscripcion == ins.id_inscripcion).all()
                            if notas_cargadas:
                                items_notas = []
                                for nt in notas_cargadas:
                                    items_notas.append(f"**{nt.comision_actividad.actividad.nombre}**: {nt.calificacion}")
                                st.write(" | ".join(items_notas))
                            else:
                                st.write("*Sin notas parciales asentadas.*")
                            
                            # Mostrar estado de la nota final
                            if ins.nota_final:
                                st.markdown(f"🔒 **Nota Final Asentada: {ins.nota_final}**")
                            else:
                                st.markdown("🔓 *Nota Final: Pendiente de Cierre*")
                        
                        # --- BOTÓN TRANSACCIONAL INDIVIDUAL ---
                        with col_r2:
                            st.write("")
                            if st.button("Cerrar Nota", key=f"cierre_ind_{ins.id_inscripcion}", use_container_width=True):
                                try:
                                    notas_al = db.query(Nota).filter(Nota.id_inscripcion == ins.id_inscripcion).all()
                                    if not notas_al:
                                        st.error("No posee notas parciales.")
                                    else:
                                        acumulado = 0.0
                                        for n in notas_al:
                                            acumulado += float(n.calificacion) * (float(n.comision_actividad.ponderacion_porcentaje) / 100.0)
                                        
                                        ins.nota_final = round(acumulado, 2)
                                        db.commit()
                                        st.success(f"Cerrado: {round(acumulado, 2)}")
                                        st.rerun()
                                except Exception as ex:
                                    db.rollback()
                                    st.error(f"Error: {ex}")

                # ====================================================
                # CONTROL TRANSACCIONAL MASIVO DE LA COMISIÓN
                # ====================================================
                st.write("---")
                st.markdown("### ⚡ Cierre Masivo Automatizado")
                st.write("Esta instrucción procesará la nota final de **todos** los alumnos de la comisión en un único bloque atómico.")
                
                # Check aclaratorio exigido
                confirmar_blancos = st.checkbox("Confirmar cierre masivo. Entiendo que si hay alumnos con instancias en blanco, se computará un 0.00 en ese porcentaje.")
                
                if st.button("🔒 Ejecutar Cierre Completo de Comisión", type="primary", use_container_width=True):
                    if not confirmar_blancos:
                        st.warning("Debés marcar la casilla de verificación para confirmar que controlaste las notas en blanco.")
                    else:
                        try:
                            # START TRANSACTION implícito de SQLAlchemy
                            conteo_cierres = 0
                            for ins in alumnos_inscriptos:
                                notas_al = db.query(Nota).filter(Nota.id_inscripcion == ins.id_inscripcion).all()
                                
                                acumulado = 0.0
                                # Si no tiene ninguna nota cargada pero confirmamos el cierre, acumula 0
                                for n in notas_al:
                                    acumulado += float(n.calificacion) * (float(n.comision_actividad.ponderacion_porcentaje) / 100.0)
                                
                                ins.nota_final = round(acumulado, 2)
                                conteo_cierres += 1
                            
                            db.commit() # COMMIT total
                            st.success(f"¡Transacción masiva exitosa! Se cerraron las actas de {conteo_cierres} estudiantes de forma consistente.")
                            st.rerun()
                        except Exception as e:
                            db.rollback() # Aborta todo si falla cualquier restricción física de las tablas
                            st.error(f"Error crítico detectado. Rollback ejecutado. Motivo: {e}")
            else:
                st.info("Sin registros de alumnos o planificación de ponderaciones para esta comisión.")
        else:
            st.info("No hay comisiones dadas de alta.")
        db.close()