from ..database import DatabaseConnection, Transaction
from mysql.connector import Error
from src.domain.entities.venta import Venta
from src.domain.entities.venta_detalle import VentaDetalle
from src.domain.entities.cliente import Cliente
from src.domain.entities.usuario import Usuario
from src.domain.entities.producto import Producto

class VentaRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_todas(self):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.fecha_creacion DESC
            """
            cursor.execute(query)
            ventas = cursor.fetchall()
            
            cursor.close()
            return ventas
        except Exception as e:
            print(f"Error al obtener ventas: {e}")
            return []
    
    def obtener_por_id(self, venta_id):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = %s
            """
            cursor.execute(query, (venta_id,))
            venta = cursor.fetchone()
            
            if venta:
                # Obtener detalles de la venta
                detalles_query = """
                    SELECT vd.*, p.nombre as producto_nombre, p.codigo as producto_codigo
                    FROM venta_detalles vd
                    LEFT JOIN productos p ON vd.producto_id = p.id
                    WHERE vd.venta_id = %s
                """
                cursor.execute(detalles_query, (venta_id,))
                venta['detalles'] = cursor.fetchall()
            
            cursor.close()
            return venta
        except Exception as e:
            print(f"Error al obtener venta: {e}")
            return None
    
    def obtener_por_numero_factura(self, numero_factura):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM ventas WHERE numero_factura = %s"
            cursor.execute(query, (numero_factura,))
            venta = cursor.fetchone()
            
            cursor.close()
            return venta
        except Exception as e:
            print(f"Error al obtener venta por número de factura: {e}")
            return None
    
    def crear_venta_completa(self, venta):
        """Crea una venta completa con sus detalles en una transacción"""
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Insertar venta
            query_venta = """
                INSERT INTO ventas (numero_factura, cliente_id, usuario_id, fecha_venta, 
                                  subtotal, impuesto, total, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_venta, (
                venta.numero_factura,
                venta.cliente.id if venta.cliente else None,
                venta.usuario.id if venta.usuario else None,
                venta.fecha_venta,
                venta.subtotal,
                venta.impuesto,
                venta.total,
                venta.estado
            ))
            
            venta_id = cursor.lastrowid
            venta.id = venta_id
            
            # Insertar detalles de venta
            for detalle in venta.detalles:
                query_detalle = """
                    INSERT INTO venta_detalles (venta_id, producto_id, cantidad, 
                                              precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query_detalle, (
                    venta_id,
                    detalle.producto_id,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.subtotal
                ))
                
                # Actualizar stock del producto
                query_stock = """
                    UPDATE productos 
                    SET stock = stock - %s 
                    WHERE id = %s AND stock >= %s
                """
                cursor.execute(query_stock, (
                    detalle.cantidad,
                    detalle.producto_id,
                    detalle.cantidad
                ))
                
                # Verificar que se actualizó el stock
                if cursor.rowcount == 0:
                    raise Exception(f"Stock insuficiente para producto ID {detalle.producto_id}")
            
            connection.commit()
            cursor.close()
            return venta_id
                
        except Exception as e:
            print(f"Error al crear venta: {e}")
            if connection:
                connection.rollback()
            if cursor:
                cursor.close()
            return None
    
    def crear_detalle_venta(self, datos_detalle, connection=None):
        try:
            if connection is None:
                connection = self.db.get_connection()
            
            cursor = connection.cursor()
            
            query = """
                INSERT INTO venta_detalles (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                datos_detalle['venta_id'],
                datos_detalle['producto_id'],
                datos_detalle['cantidad'],
                datos_detalle['precio_unitario'],
                datos_detalle['subtotal']
            ))
            
            detalle_id = cursor.lastrowid
            cursor.close()
            
            return detalle_id
        except Exception as e:
            print(f"Error al crear detalle de venta: {e}")
            if connection:
                connection.rollback()
            return None
    
    def actualizar_stock_producto(self, producto_id, nueva_cantidad, connection=None):
        try:
            if connection is None:
                connection = self.db.get_connection()
            
            cursor = connection.cursor()
            
            query = "UPDATE productos SET stock = %s WHERE id = %s"
            cursor.execute(query, (nueva_cantidad, producto_id))
            
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
            if connection:
                connection.rollback()
            return False
    
    def obtener_ventas_por_fecha(self, fecha_inicio, fecha_fin):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT v.*, c.nombre as cliente_nombre, u.nombre as usuario_nombre
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.fecha_venta BETWEEN %s AND %s
                ORDER BY v.fecha_venta DESC, v.fecha_creacion DESC
            """
            cursor.execute(query, (fecha_inicio, fecha_fin))
            ventas = cursor.fetchall()
            
            cursor.close()
            return ventas
        except Exception as e:
            print(f"Error al obtener ventas por fecha: {e}")
            return []
    
    def anular_venta(self, venta_id):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Primero, obtener los detalles para restaurar stock
            detalles_query = "SELECT producto_id, cantidad FROM venta_detalles WHERE venta_id = %s"
            cursor.execute(detalles_query, (venta_id,))
            detalles = cursor.fetchall()
            
            # Restaurar stock de productos
            for detalle in detalles:
                restore_query = """
                    UPDATE productos 
                    SET stock = stock + %s 
                    WHERE id = %s
                """
                cursor.execute(restore_query, (detalle['cantidad'], detalle['producto_id']))
            
            # Anular la venta
            anular_query = "UPDATE ventas SET estado = 'CANCELADA' WHERE id = %s"
            cursor.execute(anular_query, (venta_id,))
            
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al anular venta: {e}")
            connection.rollback()
            return False