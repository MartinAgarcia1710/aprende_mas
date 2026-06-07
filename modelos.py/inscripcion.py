from datetime import date

class Inscripcion:
    def __init__(self, id_estudiante, id_comision, fecha=None, nota_final=None, activo=1, id_inscripcion=None):
        self.id_inscripcion = id_inscripcion
        self.fecha = fecha if fecha else date.today()
        self.nota_final = nota_final
        self.activo = activo
        self.id_estudiante = id_estudiante
        self.id_comision = id_comision