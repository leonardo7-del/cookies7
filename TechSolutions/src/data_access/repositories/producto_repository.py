from ..database import DatabaseConnection, Transaction
from mysql.connector import Error
from src.domain.entities.producto import Producto

class ProductoRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todos(self):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                return [Producto(**data) for data in self._get_demo_data()]
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, codigo, nombre, descripcion, precio, stock, 
                       stock_minimo, activo, fecha_creacion
                FROM productos 
                WHERE activo = TRUE 
                ORDER BY nombre
            """
            cursor.execute(query)
            productos_data = cursor.fetchall()
            
            cursor.close()
            
            # Convertir a objetos Producto
            productos = []
            for data in productos_data:
                producto = Producto(
                    id=data['id'],
                    codigo=data['codigo'],
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion'),
                    precio=float(data['precio']),
                    stock=int(data['stock']),
                    stock_minimo=int(data['stock_minimo']),
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
                productos.append(producto)
            
            return productos
        except Error as e:
            print(f"Error al obtener productos: {e}")
            return [Producto(**data) for data in self._get_demo_data()]
    
    def obtener_por_id(self, producto_id):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                demo_data = next((data for data in self._get_demo_data() if data['id'] == producto_id), None)
                return Producto(**demo_data) if demo_data else None
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, codigo, nombre, descripcion, precio, stock,
                       stock_minimo, activo, fecha_creacion
                FROM productos 
                WHERE id = %s AND activo = TRUE
            """
            cursor.execute(query, (producto_id,))
            data = cursor.fetchone()
            
            cursor.close()
            
            if data:
                return Producto(
                    id=data['id'],
                    codigo=data['codigo'],
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion'),
                    precio=float(data['precio']),
                    stock=int(data['stock']),
                    stock_minimo=int(data['stock_minimo']),
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
            return None
        except Error as e:
            print(f"Error al obtener producto: {e}")
            demo_data = next((data for data in self._get_demo_data() if data['id'] == producto_id), None)
            return Producto(**demo_data) if demo_data else None
    
    def obtener_por_codigo(self, codigo):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                demo_data = next((data for data in self._get_demo_data() if data['codigo'] == codigo), None)
                return Producto(**demo_data) if demo_data else None
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, codigo, nombre, descripcion, precio, stock,
                       stock_minimo, activo, fecha_creacion
                FROM productos 
                WHERE codigo = %s AND activo = TRUE
            """
            cursor.execute(query, (codigo,))
            data = cursor.fetchone()
            
            cursor.close()
            
            if data:
                return Producto(
                    id=data['id'],
                    codigo=data['codigo'],
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion'),
                    precio=float(data['precio']),
                    stock=int(data['stock']),
                    stock_minimo=int(data['stock_minimo']),
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
            return None
        except Error as e:
            print(f"Error al obtener producto por código: {e}")
            demo_data = next((data for data in self._get_demo_data() if data['codigo'] == codigo), None)
            return Producto(**demo_data) if demo_data else None
    
    def buscar_por_nombre(self, nombre):
        try:
            connection = self.db.get_connection()
            if not connection:
                print("No hay conexión a la base de datos, usando datos demo")
                demo_data = [data for data in self._get_demo_data() if nombre.lower() in data['nombre'].lower()]
                return [Producto(**data) for data in demo_data]
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id, codigo, nombre, descripcion, precio, stock,
                       stock_minimo, activo, fecha_creacion
                FROM productos 
                WHERE nombre LIKE %s AND activo = TRUE 
                ORDER BY nombre
            """
            cursor.execute(query, (f"%{nombre}%",))
            productos_data = cursor.fetchall()
            
            cursor.close()
            
            # Convertir a objetos Producto
            productos = []
            for data in productos_data:
                producto = Producto(
                    id=data['id'],
                    codigo=data['codigo'],
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion'),
                    precio=float(data['precio']),
                    stock=int(data['stock']),
                    stock_minimo=int(data['stock_minimo']),
                    activo=bool(data['activo']),
                    fecha_creacion=data['fecha_creacion']
                )
                productos.append(producto)
            
            return productos
        except Error as e:
            print(f"Error al buscar productos: {e}")
            demo_data = [data for data in self._get_demo_data() if nombre.lower() in data['nombre'].lower()]
            return [Producto(**data) for data in demo_data]
    
    def crear_producto(self, producto):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede crear el producto")
                    return None
                    
                cursor = transaction.cursor()
                
                # Verificar si ya existe un producto con el mismo código
                cursor.execute("SELECT id FROM productos WHERE codigo = %s AND activo = TRUE", (producto.codigo,))
                if cursor.fetchone():
                    print(f"Ya existe un producto activo con el código {producto.codigo}")
                    return None
                
                query = """
                    INSERT INTO productos (codigo, nombre, descripcion, precio, 
                                         stock, stock_minimo, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(query, (
                    producto.codigo,
                    producto.nombre,
                    producto.descripcion,
                    float(producto.precio),
                    int(producto.stock),
                    int(producto.stock_minimo)
                ))
                
                producto_id = cursor.lastrowid
                
                # Verificar que el producto se creó correctamente
                if producto_id:
                    # Actualizar el ID del producto
                    producto.id = producto_id
                    producto.activo = True
                    return producto_id
                else:
                    print("No se pudo obtener el ID del producto creado")
                    return None
                    
        except Error as e:
            print(f"Error al crear producto: {e}")
            return None
    
    def actualizar_producto(self, producto_id, datos_producto):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede actualizar el producto")
                    return False
                
                cursor = transaction.cursor()
                
                # Verificar si el producto existe y está activo
                cursor.execute("SELECT id FROM productos WHERE id = %s AND activo = TRUE", (producto_id,))
                if not cursor.fetchone():
                    print(f"No se encontró un producto activo con ID {producto_id}")
                    return False
                
                # Si se está actualizando el código, verificar que no exista otro producto con el mismo código
                if 'codigo' in datos_producto:
                    cursor.execute("""
                        SELECT id FROM productos 
                        WHERE codigo = %s AND id != %s AND activo = TRUE
                    """, (datos_producto['codigo'], producto_id))
                    if cursor.fetchone():
                        print(f"Ya existe otro producto activo con el código {datos_producto['codigo']}")
                        return False
                
                query = """
                    UPDATE productos 
                    SET codigo = %s, 
                        nombre = %s, 
                        descripcion = %s, 
                        precio = %s, 
                        stock = %s, 
                        stock_minimo = %s
                    WHERE id = %s AND activo = TRUE
                """
                cursor.execute(query, (
                    datos_producto['codigo'],
                    datos_producto['nombre'],
                    datos_producto.get('descripcion'),
                    float(datos_producto['precio']),
                    int(datos_producto['stock']),
                    int(datos_producto['stock_minimo']),
                    producto_id
                ))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    print("No se realizaron cambios en el producto")
                    return False
                    
        except Error as e:
            print(f"Error al actualizar producto: {e}")
            return False
    
    def actualizar_stock(self, producto_id, nueva_cantidad):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede actualizar el stock")
                    return False
                
                cursor = transaction.cursor()
                
                # Verificar si el producto existe y está activo
                cursor.execute("SELECT id FROM productos WHERE id = %s AND activo = TRUE", (producto_id,))
                if not cursor.fetchone():
                    print(f"No se encontró un producto activo con ID {producto_id}")
                    return False
                
                # Actualizar el stock
                query = "UPDATE productos SET stock = %s WHERE id = %s AND activo = TRUE"
                cursor.execute(query, (int(nueva_cantidad), producto_id))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    print("No se pudo actualizar el stock del producto")
                    return False
                    
        except Error as e:
            print(f"Error al actualizar stock: {e}")
            return False
    
    def eliminar_producto(self, producto_id):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede eliminar el producto")
                    return False
                
                cursor = transaction.cursor()
                
                # Verificar si el producto existe y está activo
                cursor.execute("SELECT id FROM productos WHERE id = %s AND activo = TRUE", (producto_id,))
                if not cursor.fetchone():
                    print(f"No se encontró un producto activo con ID {producto_id}")
                    return False
                
                # Eliminación lógica del producto
                query = "UPDATE productos SET activo = FALSE WHERE id = %s AND activo = TRUE"
                cursor.execute(query, (producto_id,))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    print("No se pudo eliminar el producto")
                    return False
                    
        except Error as e:
            print(f"Error al eliminar producto: {e}")
            return False
    
    def obtener_productos_bajo_stock(self):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, retornando datos demo")
                    return [Producto(**data) for data in self._get_demo_data() if data['stock'] <= data['stock_minimo']]
                
                cursor = transaction.cursor()
                
                query = """
                    SELECT id, codigo, nombre, descripcion, precio, stock, stock_minimo, activo, fecha_creacion
                    FROM productos 
                    WHERE stock <= stock_minimo AND activo = TRUE
                    ORDER BY stock ASC
                """
                cursor.execute(query)
                productos = cursor.fetchall()
                
                return [
                    Producto(
                        id=producto[0],
                        codigo=producto[1],
                        nombre=producto[2],
                        descripcion=producto[3],
                        precio=float(producto[4]),
                        stock=int(producto[5]),
                        stock_minimo=int(producto[6]),
                        activo=bool(producto[7]),
                        fecha_creacion=producto[8]
                    )
                    for producto in productos
                ]
                
        except Error as e:
            print(f"Error al obtener productos bajo stock: {e}")
            return [Producto(**data) for data in self._get_demo_data() if data['stock'] <= data['stock_minimo']]
            
    def _get_demo_data(self):
        from datetime import datetime
        return [
            {
                'id': 1,
                'codigo': 'LAP-001',
                'nombre': 'Laptop Dell XPS 13',
                'descripcion': 'Laptop ultradelgada 13 pulgadas',
                'precio': 1500.00,
                'stock': 10,
                'stock_minimo': 5,
                'activo': True,
                'fecha_creacion': datetime.now()
            },
            {
                'id': 2,
                'codigo': 'MON-001',
                'nombre': 'Monitor Samsung 24"',
                'descripcion': 'Monitor LED Full HD 24 pulgadas',
                'precio': 250.00,
                'stock': 25,
                'stock_minimo': 5,
                'activo': True,
                'fecha_creacion': datetime.now()
            },
            {
                'id': 3,
                'codigo': 'TEC-001',
                'nombre': 'Teclado Mecánico RGB',
                'descripcion': 'Teclado mecánico retroiluminado',
                'precio': 120.00,
                'stock': 15,
                'stock_minimo': 5,
                'activo': True,
                'fecha_creacion': datetime.now()
            }
        ]