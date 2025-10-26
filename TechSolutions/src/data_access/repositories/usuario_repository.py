from ..database import DatabaseConnection
from mysql.connector import Error

class UsuarioRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def autenticar_usuario(self, username, password):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_user(username, password)
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT id, username, nombre, nivel_acceso FROM usuarios WHERE username = %s AND password = %s AND activo = 1"
            cursor.execute(query, (username, password))
            usuario = cursor.fetchone()
            
            cursor.close()
            return usuario
        except Error as e:
            print(f"Error en autenticación: {e}")
            return self._get_demo_user(username, password)
    
    def obtener_por_id(self, usuario_id):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT id, username, nombre, nivel_acceso FROM usuarios WHERE id = %s"
            cursor.execute(query, (usuario_id,))
            usuario = cursor.fetchone()
            
            cursor.close()
            return usuario
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def _get_demo_user(self, username, password):
        """Datos de demo por si falla la conexión a MySQL"""
        demo_users = {
            'admin': {'id': 1, 'username': 'admin', 'nombre': 'Administrador Principal', 'nivel_acceso': 3},
            'supervisor': {'id': 2, 'username': 'supervisor', 'nombre': 'Supervisor de Ventas', 'nivel_acceso': 2},
            'operador': {'id': 3, 'username': 'operador', 'nombre': 'Operador de Sistema', 'nivel_acceso': 1}
        }
        if username in demo_users and password == f"{username}123":
            return demo_users[username]
        return None