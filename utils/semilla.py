from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Curso, ActividadEvaluativa, Comision, ComisionActividad, Inscripcion, Nota, UsuarioSistema
from datetime import date

def poblar_base_de_datos():
    db = SessionLocal()
    try:
        # Verificar si ya existen usuarios para no duplicar datos
        if db.query(UsuarioSistema).first():
            print("La base de datos ya contiene datos semilla.")
            return

        print("Poblando base de datos con datos semilla...")

        # 1. Crear Estudiante
        martin = Estudiante(nombre="Martin", apellido="Gomez", e_mail="martin.gomez@aprendemas.edu", dni="40123456", legajo=1001, activo=1)
        db.add(martin)
        db.flush() # flush nos da el id_estudiante generado por SQLite antes de hacer el commit

        # 2. Crear Usuarios del Sistema (Admin y Alumno)
        admin_user = UsuarioSistema(username="admin", password_hash="admin123", rol="administrador")
        alumno_user = UsuarioSistema(username="alumno", password_hash="alumno123", rol="estudiante", id_estudiante=martin.id_estudiante)
        db.add_all([admin_user, alumno_user])

        # 3. Crear Curso
        bd1 = Curso(nombre="Bases de Datos I", activo=1)
        db.add(bd1)
        db.flush()

        # 4. Crear Actividades Evaluativas (Catálogo)
        parcial = ActividadEvaluativa(nombre="Examen Parcial", activo=1)
        proyecto = ActividadEvaluativa(nombre="Proyecto Integrador", activo=1)
        tp = ActividadEvaluativa(nombre="Trabajo Práctico", activo=1)
        db.add_all([parcial, proyecto, tp])
        db.flush()

        # 5. Crear Comisión (Año 2026, Semestre 1)
        comision1 = Comision(fecha_inicio=date(2026, 3, 10), fecha_fin=date(2026, 7, 1), anio=2026, semestre=1, cantidad_maxima=30, id_curso=bd1.id_curso)
        db.add(comision1)
        db.flush()

        # 6. Planificar Actividades de la Comisión (Pesos)
        ca1 = ComisionActividad(id_comision=comision1.id_comision, id_actividad=parcial.id_actividad, ponderacion_porcentaje=50.00)
        ca2 = ComisionActividad(id_comision=comision1.id_comision, id_actividad=proyecto.id_actividad, ponderacion_porcentaje=30.00)
        ca3 = ComisionActividad(id_comision=comision1.id_comision, id_actividad=tp.id_actividad, ponderacion_porcentaje=20.00)
        db.add_all([ca1, ca2, ca3])
        db.flush()

        # 7. Inscribir al Alumno
        inscripcion1 = Inscripcion(id_estudiante=martin.id_estudiante, id_comision=comision1.id_comision, fecha=date(2026, 3, 1), activo=1)
        db.add(inscripcion1)
        db.flush()

        # 8. Cargar algunas Notas Parciales iniciales
        nota1 = Nota(calificacion=8, observaciones="Excelente desempeño conceptual", fecha=date(2026, 5, 10), id_inscripcion=inscripcion1.id_inscripcion, id_comision_actividad=ca1.id_comision_actividad)
        nota2 = Nota(calificacion=7, observaciones="Faltaron algunos diagramas", fecha=date(2026, 6, 1), id_inscripcion=inscripcion1.id_inscripcion, id_comision_actividad=ca2.id_comision_actividad)
        db.add_all([nota1, nota2])

        db.commit()
        print("¡Base de datos poblada con éxito!")
    except Exception as e:
        db.rollback()
        print(f"Error al poblar la base de datos: {e}")
    finally:
        db.close()