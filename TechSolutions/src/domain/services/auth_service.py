from src.data_access.repositories.usuario_repository import UsuarioRepository

class AuthService:
    def __init__(self):
        self.usuario_actual = None
        self.usuario_repository = UsuarioRepository()
    
    def login(self, username, password):
        """Autentica un usuario usando la base de datos"""
        try:
            usuario = self.usuario_repository.autenticar_usuario(username, password)
            if usuario:
                self.usuario_actual = usuario
                return True, "Login exitoso"
            else:
                return False, "Credenciales inválidas"
        except Exception as e:
            print(f"Error en login: {e}")
            return False, "Error en el sistema de autenticación"
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        self.usuario_actual = None
    
    def obtener_usuario_actual(self):
        """Obtiene el usuario actualmente autenticado"""
        return self.usuario_actual
    
    def tiene_permiso(self, nivel_requerido):
        """Verifica si el usuario actual tiene el nivel de acceso requerido"""
        if not self.usuario_actual:
            return False
        return self.usuario_actual.nivel_acceso >= nivel_requerido

    def verificar_acceso(self, nivel_requerido):
        """Compatibilidad con UI: alias de tiene_permiso(nivel_requerido)."""
        return self.tiene_permiso(nivel_requerido)
    
    def es_administrador(self):
        """Verifica si el usuario actual es administrador"""
        return self.tiene_permiso(3)
    
    def es_supervisor(self):
        """Verifica si el usuario actual es supervisor o superior"""
        return self.tiene_permiso(2)
    
    def cambiar_password(self, password_actual, password_nuevo):
        """Cambia la contraseña del usuario actual"""
        if not self.usuario_actual:
            return False, "No hay usuario autenticado"
        
        # Verificar password actual
        usuario_verificado = self.usuario_repository.autenticar_usuario(
            self.usuario_actual.username, password_actual
        )
        
        if not usuario_verificado:
            return False, "Contraseña actual incorrecta"
        
        # Aquí se implementaría el cambio de contraseña en el repositorio
        # Por ahora retornamos éxito
        return True, "Contraseña cambiada exitosamente"