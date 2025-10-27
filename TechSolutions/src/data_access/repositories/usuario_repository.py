from ..database import DatabaseConnection, Transaction
from mysql.connector import Error
from src.domain.entities.usuario import Usuario
import hashlib

class UsuarioRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def autenticar_usuario(self, username, password):
        """Autentica un usuario con username y password"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_user(username, password)
            
            cursor = connection.cursor(dictionary=True)
            
            # Buscar usuario activo
            query = """
                SELECT id, username, nombre, nivel_acceso, activo, fecha_creacion 
                FROM usuarios 
                WHERE username = %s AND password = %s AND activo = 1
            """
            cursor.execute(query, (username, password))
            usuario_data = cursor.fetchone()
            
            cursor.close()
            
            if usuario_data:
                return Usuario(
                    id=usuario_data['id'],
                    username=usuario_data['username'],
                    nombre=usuario_data['nombre'],
                    nivel_acceso=usuario_data['nivel_acceso']
                )
            return None
            
        except Error as e:
            print(f"Error en autenticación: {e}")
            return self._get_demo_user(username, password)
    
    def obtener_por_id(self, usuario_id):
        """Obtiene un usuario por su ID"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, username, nombre, nivel_acceso, activo, fecha_creacion 
                FROM usuarios 
                WHERE id = %s AND activo = 1
            """
            cursor.execute(query, (usuario_id,))
            usuario_data = cursor.fetchone()
            
            cursor.close()
            
            if usuario_data:
                return Usuario(
                    id=usuario_data['id'],
                    username=usuario_data['username'],
                    nombre=usuario_data['nombre'],
                    nivel_acceso=usuario_data['nivel_acceso']
                )
            return None
            
        except Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def obtener_todos(self):
        """Obtiene todos los usuarios activos"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, username, nombre, nivel_acceso, activo, fecha_creacion 
                FROM usuarios 
                WHERE activo = 1 
                ORDER BY nombre
            """
            cursor.execute(query)
            usuarios_data = cursor.fetchall()
            
            cursor.close()
            
            usuarios = []
            for usuario_data in usuarios_data:
                usuarios.append(Usuario(
                    id=usuario_data['id'],
                    username=usuario_data['username'],
                    nombre=usuario_data['nombre'],
                    nivel_acceso=usuario_data['nivel_acceso']
                ))
            
            return usuarios
            
        except Error as e:
            print(f"Error al obtener usuarios: {e}")
            return []
    
    def crear_usuario(self, username, password, nombre, nivel_acceso=1):
        """Crea un nuevo usuario"""
        try:
            with Transaction() as connection:
                if connection is None:
                    return False
                
                cursor = connection.cursor()
                
                query = """
                    INSERT INTO usuarios (username, password, nombre, nivel_acceso, activo) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (username, password, nombre, nivel_acceso, True))
                
                cursor.close()
                return True
                
        except Error as e:
            print(f"Error al crear usuario: {e}")
            return False
    
    def _get_demo_user(self, username, password):
        """Datos de demo por si falla la conexión a MySQL"""
        demo_users = {
            'admin': Usuario(1, 'admin', 'Administrador Principal', 3),
            'supervisor': Usuario(2, 'supervisor', 'Supervisor de Ventas', 2),
            'operador': Usuario(3, 'operador', 'Operador de Sistema', 1)
        }
        if username in demo_users and password == f"{username}123":
            return demo_users[username]
        return None