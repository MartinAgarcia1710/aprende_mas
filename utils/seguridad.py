import hashlib

def generar_hash(password: str) -> str:
    """Convierte una contraseña en texto plano a un hash SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()