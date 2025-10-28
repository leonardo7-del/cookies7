from ..database import DatabaseConnection, Transaction
from mysql.connector import Error
from src.domain.entities.cliente import Cliente

class ClienteRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todos(self):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                return [Cliente(**data) for data in self._get_demo_data()]
                
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, nombre, email, telefono, direccion, ruc, 
                       activo, fecha_creacion 
                FROM clientes 
                WHERE activo = TRUE 
                ORDER BY nombre
            """
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
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
                clientes.append(cliente)
            
            return clientes
        except Error as e:
            print(f"Error al obtener clientes: {e}")
            return [Cliente(**data) for data in self._get_demo_data()]
    
    def obtener_por_id(self, cliente_id):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                demo_data = next((data for data in self._get_demo_data() if data['id'] == cliente_id), None)
                return Cliente(**demo_data) if demo_data else None
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, nombre, email, telefono, direccion, ruc,
                       activo, fecha_creacion
                FROM clientes 
                WHERE id = %s AND activo = TRUE
            """
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
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
            return None
        except Error as e:
            print(f"Error al obtener cliente: {e}")
            demo_data = next((data for data in self._get_demo_data() if data['id'] == cliente_id), None)
            return Cliente(**demo_data) if demo_data else None
    
    def buscar_por_nombre(self, nombre):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                demo_data = [data for data in self._get_demo_data() if nombre.lower() in data['nombre'].lower()]
                return [Cliente(**data) for data in demo_data]
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, nombre, email, telefono, direccion, ruc,
                       activo, fecha_creacion
                FROM clientes 
                WHERE nombre LIKE %s AND activo = TRUE 
                ORDER BY nombre
            """
            cursor.execute(query, (f"%{nombre}%",))
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
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
                clientes.append(cliente)
            
            return clientes
        except Error as e:
            print(f"Error al buscar clientes: {e}")
            demo_data = [data for data in self._get_demo_data() if nombre.lower() in data['nombre'].lower()]
            return [Cliente(**data) for data in demo_data]
    
    def crear_cliente(self, cliente):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede crear el cliente")
                    return None
                    
                cursor = transaction.cursor()
                
                query = """
                    INSERT INTO clientes (nombre, email, telefono, direccion, ruc, activo)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(query, (
                    cliente.nombre,
                    cliente.email,
                    cliente.telefono,
                    cliente.direccion,
                    cliente.ruc
                ))
                
                cliente_id = cursor.lastrowid
                
                # Verificar que el cliente se creó correctamente
                if cliente_id:
                    # Actualizar el ID del cliente
                    cliente.id = cliente_id
                    cliente.activo = True
                    return cliente_id
                else:
                    print("No se pudo obtener el ID del cliente creado")
                    return None
                    
        except Error as e:
            print(f"Error al crear cliente: {e}")
            return None
    
    def actualizar_cliente(self, cliente_id, datos_cliente):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede actualizar el cliente")
                    return False
                
                cursor = transaction.cursor()
                
                # Verificar si el cliente existe y está activo
                cursor.execute("SELECT id FROM clientes WHERE id = %s AND activo = TRUE", (cliente_id,))
                if not cursor.fetchone():
                    print(f"No se encontró un cliente activo con ID {cliente_id}")
                    return False
                
                query = """
                    UPDATE clientes 
                    SET nombre = %s, 
                        email = %s, 
                        telefono = %s, 
                        direccion = %s, 
                        ruc = %s
                    WHERE id = %s AND activo = TRUE
                """
                cursor.execute(query, (
                    datos_cliente['nombre'],
                    datos_cliente.get('email'),
                    datos_cliente.get('telefono'),
                    datos_cliente.get('direccion'),
                    datos_cliente.get('ruc'),
                    cliente_id
                ))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    print("No se realizaron cambios en el cliente")
                    return False
                    
        except Error as e:
            print(f"Error al actualizar cliente: {e}")
            return False
    
    def eliminar_cliente(self, cliente_id):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede eliminar el cliente")
                    return False
                
                cursor = transaction.cursor()
                
                # Verificar si el cliente existe y está activo
                cursor.execute("SELECT id FROM clientes WHERE id = %s AND activo = TRUE", (cliente_id,))
                if not cursor.fetchone():
                    print(f"No se encontró un cliente activo con ID {cliente_id}")
                    return False
                
                # Realizar eliminación lógica
                query = "UPDATE clientes SET activo = FALSE WHERE id = %s AND activo = TRUE"
                cursor.execute(query, (cliente_id,))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    print("No se pudo eliminar el cliente")
                    return False
                    
        except Error as e:
            print(f"Error al eliminar cliente: {e}")
            return False
    
    # Métodos de demo para cuando no hay conexión a BD
    def _get_demo_data(self):
        from datetime import datetime
        return [
            {
                'id': 1, 
                'nombre': 'Empresa ABC SA', 
                'email': 'abc@empresa.com', 
                'telefono': '123-4567', 
                'direccion': 'Av. Principal 123', 
                'ruc': '12345678901',
                'activo': 1,
                'fecha_creacion': datetime.now()
            },
            {
                'id': 2, 
                'nombre': 'Comercial XYZ Ltda', 
                'email': 'xyz@comercial.com', 
                'telefono': '987-6543', 
                'direccion': 'Calle Secundaria 456', 
                'ruc': '98765432109',
                'activo': 1,
                'fecha_creacion': datetime.now()
            },
            {
                'id': 3,
                'nombre': 'Distribuidora Nacional SA',
                'email': 'ventas@distribuidora.com',
                'telefono': '555-1234',
                'direccion': 'Zona Industrial, Calle 5',
                'ruc': '20123456789',
                'activo': 1,
                'fecha_creacion': datetime.now()
            }
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