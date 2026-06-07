class Estudiante:
    def __init__(self, nombre, apellido, e_mail, dni, legajo, telefono=None, activo=1, id_estudiante=None):
        self.id_estudiante = id_estudiante
        self.nombre = nombre
        self.apellido = apellido
        self.e_mail = e_mail
        self.telefono = telefono
        self.dni = dni
        self.legajo = legajo
        self.activo = activo