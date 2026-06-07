class UsuarioSistema:
    def __init__(self, username, password_hash, rol, id_estudiante=None, id_usuario=None):
        self.id_usuario = id_usuario
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
        self.id_estudiante = id_estudiante