from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import date
from datos.base import Base

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    
    id_estudiante = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    e_mail = Column(String(150), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)
    dni = Column(String(20), nullable=False, unique=True)
    legajo = Column(Integer, nullable=False, unique=True)
    activo = Column(Integer, nullable=False, default=1)
    
    __table_args__ = (CheckConstraint('activo IN (1, 2)', name='chk_estudiante_activo'),)

    inscripciones = relationship("Inscripcion", back_populates="estudiante")


class Curso(Base):
    __tablename__ = 'cursos'
    
    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, unique=True)
    activo = Column(Integer, nullable=False, default=1)
    
    __table_args__ = (CheckConstraint('activo IN (1, 2)', name='chk_curso_activo'),)

    comisiones = relationship("Comision", back_populates="curso")


class ActividadEvaluativa(Base):
    __tablename__ = 'actividades_evaluativas'
    
    id_actividad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, unique=True)
    activo = Column(Integer, nullable=False, default=1)
    
    __table_args__ = (CheckConstraint('activo IN (1, 2)', name='chk_actividad_activo'),)

    comisiones_actividades = relationship("ComisionActividad", back_populates="actividad")


class Comision(Base):
    __tablename__ = 'comisiones'
    
    id_comision = Column(Integer, primary_key=True, autoincrement=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    anio = Column(Integer, nullable=False)
    semestre = Column(Integer, nullable=False)
    cantidad_maxima = Column(Integer, nullable=False)
    id_curso = Column(Integer, ForeignKey('cursos.id_curso'), nullable=False)
    
    __table_args__ = (CheckConstraint('semestre IN (1, 2)', name='chk_semestre'),)

    curso = relationship("Curso", back_populates="comisiones")
    planificaciones = relationship("ComisionActividad", back_populates="comision")
    inscripciones = relationship("Inscripcion", back_populates="comision")


class ComisionActividad(Base):
    __tablename__ = 'comisiones_actividades'
    
    id_comision_actividad = Column(Integer, primary_key=True, autoincrement=True)
    id_comision = Column(Integer, ForeignKey('comisiones.id_comision'), nullable=False)
    id_actividad = Column(Integer, ForeignKey('actividades_evaluativas.id_actividad'), nullable=False)
    ponderacion_porcentaje = Column(Numeric(5, 2), nullable=False)
    
    __table_args__ = (CheckConstraint('ponderacion_porcentaje BETWEEN 0.00 AND 100.00', name='CHK_porcentaje'),)

    comision = relationship("Comision", back_populates="planificaciones")
    actividad = relationship("ActividadEvaluativa", back_populates="comisiones_actividades")
    notas = relationship("Nota", back_populates="comision_actividad")


class Inscripcion(Base):
    __tablename__ = 'inscripciones'
    
    id_inscripcion = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False, default=date.today)
    nota_final = Column(Numeric(4, 2), nullable=True)
    activo = Column(Integer, nullable=False, default=1)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id_estudiante'), nullable=False)
    id_comision = Column(Integer, ForeignKey('comisiones.id_comision'), nullable=False)
    
    __table_args__ = (
        CheckConstraint('activo IN (1, 2)', name='chk_inscripcion_activo'),
        CheckConstraint('nota_final BETWEEN 1.00 AND 10.00', name='CHK_nota_final'),
    )

    estudiante = relationship("Estudiante", back_populates="inscripciones")
    comision = relationship("Comision", back_populates="inscripciones")
    notas = relationship("Nota", back_populates="inscripcion")


class Nota(Base):
    __tablename__ = 'notas'
    
    id_nota = Column(Integer, primary_key=True, autoincrement=True)
    calificacion = Column(Integer, nullable=False)
    observaciones = Column(String(250), nullable=True)
    fecha = Column(Date, nullable=False, default=date.today)
    id_inscripcion = Column(Integer, ForeignKey('inscripciones.id_inscripcion'), nullable=False)
    id_comision_actividad = Column(Integer, ForeignKey('comisiones_actividades.id_comision_actividad'), nullable=False)

    inscripcion = relationship("Inscripcion", back_populates="notas")
    comision_actividad = relationship("ComisionActividad", back_populates="notas")

class UsuarioSistema(Base):
    __tablename__ = 'usuarios_sistema'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False) # Para guardar la clave plana o con hash
    rol = Column(String(20), nullable=False) # 'administrador' o 'estudiante'
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id_estudiante'), nullable=True)
    
    __table_args__ = (CheckConstraint("rol IN ('administrador', 'estudiante')", name='chk_rol_usuario'),)
    
    estudiante = relationship("Estudiante")