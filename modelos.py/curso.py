class Curso:
    def __init__(self, nombre, activo=1, id_curso=None):
        self.id_curso = id_curso
        self.nombre = nombre
        self.activo = activo