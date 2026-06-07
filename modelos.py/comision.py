class Comision:
    def __init__(self, anio, semestre, cantidad_maxima, id_curso, fecha_inicio=None, fecha_fin=None, id_comision=None):
        self.id_comision = id_comision
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.anio = anio
        self.semestre = semestre
        self.cantidad_maxima = cantidad_maxima
        self.id_curso = id_curso