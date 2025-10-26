from ..database import DatabaseConnection
from mysql.connector import Error

class ProductoRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todos(self):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_data()
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE activo = 1 ORDER BY nombre"
            cursor.execute(query)
            productos = cursor.fetchall()
            
            cursor.close()
            return productos
        except Error as e:
            print(f"Error al obtener productos: {e}")
            return self._get_demo_data()
    
    def obtener_por_id(self, producto_id):
        try:
            connection = self.db.get_connection()
            if connection is None:
                return self._get_demo_producto(producto_id)
            
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE id = %s AND activo = 1"
            cursor.execute(query, (producto_id,))
            producto = cursor.fetchone()
            
            cursor.close()
            return producto
        except Error as e:
            print(f"Error al obtener producto: {e}")
            return self._get_demo_producto(producto_id)
    
    def obtener_por_codigo(self, codigo):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE codigo = %s AND activo = 1"
            cursor.execute(query, (codigo,))
            producto = cursor.fetchone()
            
            cursor.close()
            return producto
        except Exception as e:
            print(f"Error al obtener producto por código: {e}")
            return None
    
    def buscar_por_nombre(self, nombre):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE nombre LIKE %s AND activo = 1 ORDER BY nombre"
            cursor.execute(query, (f"%{nombre}%",))
            productos = cursor.fetchall()
            
            cursor.close()
            return productos
        except Exception as e:
            print(f"Error al buscar productos: {e}")
            return []
    
    def crear_producto(self, datos_producto):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO productos (codigo, nombre, descripcion, precio, stock, stock_minimo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                datos_producto['codigo'],
                datos_producto['nombre'],
                datos_producto.get('descripcion'),
                datos_producto['precio'],
                datos_producto['stock'],
                datos_producto['stock_minimo']
            ))
            
            connection.commit()
            producto_id = cursor.lastrowid
            cursor.close()
            
            return producto_id
        except Exception as e:
            print(f"Error al crear producto: {e}")
            connection.rollback()
            return None
    
    def actualizar_producto(self, producto_id, datos_producto):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE productos 
                SET codigo = %s, nombre = %s, descripcion = %s, precio = %s, 
                    stock = %s, stock_minimo = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                datos_producto['codigo'],
                datos_producto['nombre'],
                datos_producto.get('descripcion'),
                datos_producto['precio'],
                datos_producto['stock'],
                datos_producto['stock_minimo'],
                producto_id
            ))
            
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            connection.rollback()
            return False
    
    def actualizar_stock(self, producto_id, nueva_cantidad):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            query = "UPDATE productos SET stock = %s WHERE id = %s"
            cursor.execute(query, (nueva_cantidad, producto_id))
            
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
            connection.rollback()
            return False
    
    def eliminar_producto(self, producto_id):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            query = "UPDATE productos SET activo = 0 WHERE id = %s"
            cursor.execute(query, (producto_id,))
            
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            connection.rollback()
            return False
    
    def obtener_productos_bajo_stock(self):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE stock <= stock_minimo AND activo = 1 ORDER BY stock"
            cursor.execute(query)
            productos = cursor.fetchall()
            
            cursor.close()
            return productos
        except Exception as e:
            print(f"Error al obtener productos bajo stock: {e}")
            return []