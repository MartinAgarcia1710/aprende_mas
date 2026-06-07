from datetime import date

class Nota:
    def __init__(self, calificacion, id_inscripcion, id_comision_actividad, observaciones=None, fecha=None, id_nota=None):
        self.id_nota = id_nota
        self.calificacion = calificacion
        self.observaciones = observaciones
        self.fecha = fecha if fecha else date.today()
        self.id_inscripcion = id_inscripcion
        self.id_comision_actividad = id_comision_actividad