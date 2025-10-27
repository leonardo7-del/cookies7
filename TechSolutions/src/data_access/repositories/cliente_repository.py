from ..database import DatabaseConnection, Transaction
from mysql.connector import Error
from src.domain.entities.cliente import Cliente

class ClienteRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todos(self):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_data()
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre"
            cursor.execute(query)
            clientes_data = cursor.fetchall()
            
            cursor.close()
            
            # Convertir a objetos Cliente
            clientes = []
            for data in clientes_data:
                cliente = Cliente(
                    id=data['id'],
                    nombre=data['nombre'],
                    email=data.get('email'),
                    telefono=data.get('telefono'),
                    direccion=data.get('direccion'),
                    ruc=data.get('ruc'),
                    activo=data['activo'],
                    fecha_creacion=data['fecha_creacion']
                )
                clientes.append(cliente)
            
            return clientes
        except Error as e:
            print(f"Error al obtener clientes: {e}")
            return self._get_demo_data()
    
    def obtener_por_id(self, cliente_id):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_cliente(cliente_id)
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM clientes WHERE id = %s AND activo = 1"
            cursor.execute(query, (cliente_id,))
            data = cursor.fetchone()
            
            cursor.close()
            
            if data:
                return Cliente(
                    id=data['id'],
                    nombre=data['nombre'],
                    email=data.get('email'),
                    telefono=data.get('telefono'),
                    direccion=data.get('direccion'),
                    ruc=data.get('ruc'),
                    activo=data['activo'],
                    fecha_creacion=data['fecha_creacion']
                )
            return None
        except Error as e:
            print(f"Error al obtener cliente: {e}")
            return self._get_demo_cliente(cliente_id)
    
    def buscar_por_nombre(self, nombre):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._search_demo_clientes(nombre)
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM clientes WHERE nombre LIKE %s AND activo = 1 ORDER BY nombre"
            cursor.execute(query, (f"%{nombre}%",))
            clientes = cursor.fetchall()
            
            cursor.close()
            return clientes
        except Error as e:
            print(f"Error al buscar clientes: {e}")
            return self._search_demo_clientes(nombre)
    
    def crear_cliente(self, cliente):
        try:
            with Transaction() as transaction:
                cursor = transaction.cursor()
                
                query = """
                    INSERT INTO clientes (nombre, email, telefono, direccion, ruc)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    cliente.nombre,
                    cliente.email,
                    cliente.telefono,
                    cliente.direccion,
                    cliente.ruc
                ))
                
                cliente_id = cursor.lastrowid
                transaction.commit()
                
                # Actualizar el ID del cliente
                cliente.id = cliente_id
                return cliente_id
        except Error as e:
            print(f"Error al crear cliente: {e}")
            return None
    
    def actualizar_cliente(self, cliente_id, datos_cliente):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return True
            
            cursor = connection.cursor()
            
            query = """
                UPDATE clientes 
                SET nombre = %s, email = %s, telefono = %s, direccion = %s, ruc = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                datos_cliente['nombre'],
                datos_cliente.get('email'),
                datos_cliente.get('telefono'),
                datos_cliente.get('direccion'),
                datos_cliente.get('ruc'),
                cliente_id
            ))
            
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error al actualizar cliente: {e}")
            if connection:
                connection.rollback()
            return False
    
    def eliminar_cliente(self, cliente_id):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return True
            
            cursor = connection.cursor()
            
            query = "UPDATE clientes SET activo = 0 WHERE id = %s"
            cursor.execute(query, (cliente_id,))
            
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error al eliminar cliente: {e}")
            if connection:
                connection.rollback()
            return False
    
    # Métodos de demo para cuando no hay conexión a BD
    def _get_demo_data(self):
        return [
            {'id': 1, 'nombre': 'Empresa ABC SA', 'email': 'abc@empresa.com', 
             'telefono': '123-4567', 'direccion': 'Av. Principal 123', 'ruc': '12345678901'},
            {'id': 2, 'nombre': 'Comercial XYZ Ltda', 'email': 'xyz@comercial.com', 
             'telefono': '987-6543', 'direccion': 'Calle Secundaria 456', 'ruc': '98765432109'}
        ]
    
    def _get_demo_cliente(self, cliente_id):
        clientes = self._get_demo_data()
        for cliente in clientes:
            if cliente['id'] == cliente_id:
                return cliente
        return None
    
    def _search_demo_clientes(self, nombre):
        clientes = self._get_demo_data()
        return [cliente for cliente in clientes if nombre.lower() in cliente['nombre'].lower()]