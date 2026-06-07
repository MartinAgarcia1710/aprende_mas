from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Curso, ActividadEvaluativa, Comision, ComisionActividad, Inscripcion, Nota, UsuarioSistema
from datetime import date
''' 
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

'''

from datos.conexion import SessionLocal
from datos.tablas_sql import Estudiante, Curso, ActividadEvaluativa, Comision, ComisionActividad, Inscripcion, Nota, UsuarioSistema
from utils.seguridad import generar_hash
from datetime import date

def poblar_base_de_datos():
    db = SessionLocal()
    try:
        # 1. Verificar si ya existen usuarios para no duplicar datos en los reinicios
        if db.query(UsuarioSistema).first():
            return

        print("Iniciando la carga de datos semilla para la Demo...")

        # 2. Crear el Usuario Administrador Global (admin / admin)
        admin_u = UsuarioSistema(
            username="admin", 
            password_hash=generar_hash("admin"), 
            rol="administrador"
        )
        db.add(admin_u)

        # 3. Crear un catálogo base de Cursos y Actividades
        prog2 = Curso(nombre="Programación II", activo=1)
        mate = Curso(nombre="Matemática Discreta", activo=1)
        db.add_all([prog2, mate])
        db.flush()

        parcial = ActividadEvaluativa(nombre="Examen Parcial", activo=1)
        proyecto = ActividadEvaluativa(nombre="Proyecto Integrador", activo=1)
        tp = ActividadEvaluativa(nombre="Trabajo Práctico", activo=1)
        db.add_all([parcial, proyecto, tp])
        db.flush()

        # 4. Abrir comisiones para el ciclo 2026
        com_prog = Comision(fecha_inicio=date(2026, 3, 10), fecha_fin=date(2026, 7, 1), anio=2026, semestre=1, cantidad_maxima=30, id_curso=prog2.id_curso)
        com_mate = Comision(fecha_inicio=date(2026, 3, 10), fecha_fin=date(2026, 7, 1), anio=2026, semestre=1, cantidad_maxima=30, id_curso=mate.id_curso)
        db.add_all([com_prog, com_mate])
        db.flush()

        # 5. Planificar ponderaciones (Suman 100%)
        # Para Programación II: Parcial 40%, Proyecto 40%, TP 20%
        cp1 = ComisionActividad(id_comision=com_prog.id_comision, id_actividad=parcial.id_actividad, ponderacion_porcentaje=40.00)
        cp2 = ComisionActividad(id_comision=com_prog.id_comision, id_actividad=proyecto.id_actividad, ponderacion_porcentaje=40.00)
        cp3 = ComisionActividad(id_comision=com_prog.id_comision, id_actividad=tp.id_actividad, ponderacion_porcentaje=20.00)
        
        # Para Matemática: Parcial 50%, Proyecto 30%, TP 20%
        cm1 = ComisionActividad(id_comision=com_mate.id_comision, id_actividad=parcial.id_actividad, ponderacion_porcentaje=50.00)
        cm2 = ComisionActividad(id_comision=com_mate.id_comision, id_actividad=proyecto.id_actividad, ponderacion_porcentaje=30.00)
        cm3 = ComisionActividad(id_comision=com_mate.id_comision, id_actividad=tp.id_actividad, ponderacion_porcentaje=20.00)
        
        db.add_all([cp1, cp2, cp3, cm1, cm2, cm3])
        db.flush()

        # 6. Datos crudos para los 10 alumnos exigidos
        datos_alumnos = [
            {"nombre": "ricardo", "apellido": "gomez", "dni": "45000001", "legajo": 2001, "mail": "ricardo@aprendemas.edu"},
            {"nombre": "laura", "apellido": "martinez", "dni": "45000002", "legajo": 2002, "mail": "laura@aprendemas.edu"},
            {"nombre": "martin", "apellido": "alvarez", "dni": "45000003", "legajo": 2003, "mail": "martin@aprendemas.edu"},
            {"nombre": "sofia", "apellido": "rodriguez", "dni": "45000004", "legajo": 2004, "mail": "sofia@aprendemas.edu"},
            {"nombre": "carlos", "apellido": "fernandez", "dni": "45000005", "legajo": 2005, "mail": "carlos@aprendemas.edu"},
            {"nombre": "lucia", "apellido": "lopez", "dni": "45000006", "legajo": 2006, "mail": "lucia@aprendemas.edu"},
            {"nombre": "diego", "apellido": "diaz", "dni": "45000007", "legajo": 2007, "mail": "diego@aprendemas.edu"},
            {"nombre": "elena", "apellido": "perez", "dni": "45000008", "legajo": 2008, "mail": "elena@aprendemas.edu"},
            {"nombre": "jorge", "apellido": "sanchez", "dni": "45000009", "legajo": 2009, "mail": "jorge@aprendemas.edu"},
            {"nombre": "ana", "apellido": "romero", "dni": "45000010", "legajo": 2010, "mail": "ana@aprendemas.edu"}
        ]

        # 7. Iterar, matricular, crear usuarios e inscribir alumnos de forma dinámica
        for idx, datos in enumerate(datos_alumnos):
            # Formateamos nombre para visualización limpia capitalizada en la UI
            nom_cap = datos["nombre"].capitalize()
            ape_cap = datos["apellido"].capitalize()
            
            # Crear Entidad Alumno Relacional
            alumno_db = Estudiante(
                nombre=nom_cap, apellido=ape_cap, e_mail=datos["mail"], 
                dni=datos["dni"], legajo=datos["legajo"], activo=1
            )
            db.add(alumno_db)
            db.flush()

            # Crear credenciales seguras (user: nombre en minúscula / password: nombre en minúscula)
            usr_alumno = UsuarioSistema(
                username=datos["nombre"], 
                password_hash=generar_hash(datos["nombre"]), 
                rol="estudiante", 
                id_estudiante=alumno_db.id_estudiante
            )
            db.add(usr_alumno)

            # Inscribir a todos en Programación II
            ins_p = Inscripcion(id_estudiante=alumno_db.id_estudiante, id_comision=com_prog.id_comision, fecha=date(2026, 3, 12), activo=1)
            db.add(ins_p)
            db.flush()

            # Inscribir solo a los primeros 5 en Matemática para simular escenarios cruzados
            if idx < 5:
                ins_m = Inscripcion(id_estudiante=alumno_db.id_estudiante, id_comision=com_mate.id_comision, fecha=date(2026, 3, 12), activo=1)
                db.add(ins_m)
                db.flush()

            # Cargar un par de notas de ejemplo para dinamizar los tableros al arrancar
            # Ricardo y Laura arrancan con notas parciales cargadas en Prog II
            if datos["nombre"] in ["ricardo", "laura"]:
                n1 = Nota(calificacion=8, observaciones="Buen parcial conceptual", fecha=date(2026, 5, 15), id_inscripcion=ins_p.id_inscripcion, id_comision_actividad=cp1.id_comision_actividad)
                n2 = Nota(calificacion=9, observaciones="Excelente código modular", fecha=date(2026, 6, 2), id_inscripcion=ins_p.id_inscripcion, id_comision_actividad=cp2.id_comision_actividad)
                db.add_all([n1, n2])

        db.commit()
        print("¡Ecosistema semilla generado con éxito!")
    except Exception as e:
        db.rollback()
        print(f"Fallo crítico al inyectar las semillas: {e}")
    finally:
        db.close()