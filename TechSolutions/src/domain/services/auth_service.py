class AuthService:
    def __init__(self):
        self.usuario_actual = None
    
    def login(self, username, password):
        # Implementación temporal para pruebas
        if username == "admin" and password == "admin123":
            # Crear usuario temporal
            from src.domain.entities.usuario import Usuario
            self.usuario_actual = Usuario(1, "admin", "Administrador Principal", 3)
            return True, "Login exitoso"
        return False, "Credenciales inválidas"
    
    def logout(self):
        self.usuario_actual = None
    
    def obtener_usuario_actual(self):
        return self.usuario_actual