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
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, retornando datos demo")
                    return self._get_demo_data()
                
                cursor = transaction.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        v.id, v.numero_factura, v.cliente_id, v.usuario_id,
                        v.fecha_venta, v.subtotal, v.impuesto, v.total,
                        v.estado, v.fecha_creacion,
                        c.nombre as cliente_nombre,
                        u.nombre as usuario_nombre
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id
                    LEFT JOIN usuarios u ON v.usuario_id = u.id
                    ORDER BY v.fecha_creacion DESC
                """
                cursor.execute(query)
                ventas = cursor.fetchall()
                
                # Obtener detalles para cada venta
                for venta in ventas:
                    detalles_query = """
                        SELECT 
                            vd.id, vd.venta_id, vd.producto_id,
                            vd.cantidad, vd.precio_unitario, vd.subtotal,
                            p.nombre as producto_nombre,
                            p.codigo as producto_codigo
                        FROM venta_detalles vd
                        LEFT JOIN productos p ON vd.producto_id = p.id
                        WHERE vd.venta_id = %s
                    """
                    cursor.execute(detalles_query, (venta['id'],))
                    venta['detalles'] = cursor.fetchall()
                
                return ventas
                
        except Error as e:
            print(f"Error al obtener ventas: {e}")
            return self._get_demo_data()
    
    def obtener_por_id(self, venta_id):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, retornando datos demo")
                    return self._get_demo_venta(venta_id)
                
                cursor = transaction.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        v.id, v.numero_factura, v.cliente_id, v.usuario_id,
                        v.fecha_venta, v.subtotal, v.impuesto, v.total,
                        v.estado, v.fecha_creacion,
                        c.nombre as cliente_nombre,
                        u.nombre as usuario_nombre
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
                        SELECT 
                            vd.id, vd.venta_id, vd.producto_id,
                            vd.cantidad, vd.precio_unitario, vd.subtotal,
                            p.nombre as producto_nombre,
                            p.codigo as producto_codigo
                        FROM venta_detalles vd
                        LEFT JOIN productos p ON vd.producto_id = p.id
                        WHERE vd.venta_id = %s
                    """
                    cursor.execute(detalles_query, (venta_id,))
                    venta['detalles'] = cursor.fetchall()
                
                return venta
                
        except Error as e:
            print(f"Error al obtener venta: {e}")
            return self._get_demo_venta(venta_id)
    
    def obtener_por_numero_factura(self, numero_factura):
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, retornando datos demo")
                    return self._get_demo_venta_por_numero_factura(numero_factura)
                
                cursor = transaction.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        v.id, v.numero_factura, v.cliente_id, v.usuario_id,
                        v.fecha_venta, v.subtotal, v.impuesto, v.total,
                        v.estado, v.fecha_creacion,
                        c.nombre as cliente_nombre,
                        u.nombre as usuario_nombre
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id
                    LEFT JOIN usuarios u ON v.usuario_id = u.id
                    WHERE v.numero_factura = %s
                """
                cursor.execute(query, (numero_factura,))
                venta = cursor.fetchone()
                
                if venta:
                    # Obtener detalles de la venta
                    detalles_query = """
                        SELECT 
                            vd.id, vd.venta_id, vd.producto_id,
                            vd.cantidad, vd.precio_unitario, vd.subtotal,
                            p.nombre as producto_nombre,
                            p.codigo as producto_codigo
                        FROM venta_detalles vd
                        LEFT JOIN productos p ON vd.producto_id = p.id
                        WHERE vd.venta_id = %s
                    """
                    cursor.execute(detalles_query, (venta['id'],))
                    venta['detalles'] = cursor.fetchall()
                
                return venta
                
        except Error as e:
            print(f"Error al obtener venta por número de factura: {e}")
            return self._get_demo_venta_por_numero_factura(numero_factura)
    
    def crear_venta_completa(self, venta):
        """Crea una venta completa con sus detalles en una transacción"""
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos, no se puede crear la venta")
                    return None
                
                cursor = transaction.cursor()
                
                # Verificar que el cliente exista y esté activo
                if venta.cliente and venta.cliente.id:
                    cursor.execute("SELECT id FROM clientes WHERE id = %s AND activo = TRUE", (venta.cliente.id,))
                    if not cursor.fetchone():
                        raise Error("El cliente no existe o no está activo")
                
                # Verificar que el usuario exista y esté activo
                if venta.usuario and venta.usuario.id:
                    cursor.execute("SELECT id FROM usuarios WHERE id = %s AND activo = TRUE", (venta.usuario.id,))
                    if not cursor.fetchone():
                        raise Error("El usuario no existe o no está activo")
                
                # Verificar stock disponible para todos los productos antes de proceder
                for detalle in venta.detalles:
                    cursor.execute("""
                        SELECT id, stock, nombre 
                        FROM productos 
                        WHERE id = %s AND activo = TRUE
                    """, (detalle.producto.id,))
                    producto = cursor.fetchone()
                    
                    if not producto:
                        raise Error(f"El producto con ID {detalle.producto.id} no existe o no está activo")
                    
                    if producto[1] < detalle.cantidad:
                        raise Error(f"Stock insuficiente para el producto {producto[2]} (ID: {producto[0]})")
                
                # Insertar venta
                query_venta = """
                    INSERT INTO ventas (
                        numero_factura, cliente_id, usuario_id, fecha_venta,
                        subtotal, impuesto, total, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_venta, (
                    venta.numero_factura,
                    venta.cliente.id if venta.cliente else None,
                    venta.usuario.id if venta.usuario else None,
                    venta.fecha_venta,
                    float(venta.subtotal),
                    float(venta.impuesto),
                    float(venta.total),
                    venta.estado
                ))
                
                venta_id = cursor.lastrowid
                if not venta_id:
                    raise Error("No se pudo obtener el ID de la venta creada")
                
                venta.id = venta_id
                
                # Insertar detalles de venta y actualizar stock
                for detalle in venta.detalles:
                    # Insertar detalle
                    query_detalle = """
                        INSERT INTO venta_detalles (
                            venta_id, producto_id, cantidad,
                            precio_unitario, subtotal
                        ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query_detalle, (
                        venta_id,
                        detalle.producto.id,
                        int(detalle.cantidad),
                        float(detalle.precio_unitario),
                        float(detalle.subtotal)
                    ))
                    
                    # Actualizar stock del producto
                    query_stock = """
                        UPDATE productos 
                        SET stock = stock - %s 
                        WHERE id = %s AND activo = TRUE
                    """
                    cursor.execute(query_stock, (
                        int(detalle.cantidad),
                        detalle.producto.id
                    ))
                
                return venta_id
                
        except Error as e:
            print(f"Error al crear venta: {e}")
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
        """Obtiene las ventas realizadas entre dos fechas"""
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos")
                    return self._get_demo_data()
                
                cursor = transaction.cursor(dictionary=True)
                
                query = """
                    SELECT 
                        v.id, v.numero_factura, v.cliente_id, v.usuario_id,
                        v.fecha_venta, v.subtotal, v.impuesto, v.total,
                        v.estado, v.fecha_creacion,
                        c.nombre as cliente_nombre,
                        u.nombre as usuario_nombre
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id AND c.activo = TRUE
                    LEFT JOIN usuarios u ON v.usuario_id = u.id AND u.activo = TRUE
                    WHERE v.fecha_venta BETWEEN %s AND %s
                    ORDER BY v.fecha_venta DESC, v.fecha_creacion DESC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin))
                ventas = cursor.fetchall()
                
                # Obtener detalles para cada venta
                for venta in ventas:
                    detalles_query = """
                        SELECT 
                            vd.id, vd.venta_id, vd.producto_id,
                            vd.cantidad, vd.precio_unitario, vd.subtotal,
                            p.nombre as producto_nombre,
                            p.codigo as producto_codigo
                        FROM venta_detalles vd
                        LEFT JOIN productos p ON vd.producto_id = p.id
                        WHERE vd.venta_id = %s
                    """
                    cursor.execute(detalles_query, (venta['id'],))
                    venta['detalles'] = cursor.fetchall()
                
                return ventas
                
        except Error as e:
            print(f"Error al obtener ventas por fecha: {e}")
            return self._get_demo_data()
    
    def anular_venta(self, venta_id):
        """Anula una venta y restaura el stock de los productos"""
        try:
            with Transaction() as transaction:
                if not transaction:
                    print("No hay conexión a la base de datos")
                    return False
                
                cursor = transaction.cursor(dictionary=True)
                
                # Verificar si la venta existe y su estado actual
                query_venta = """
                    SELECT id, estado 
                    FROM ventas 
                    WHERE id = %s
                """
                cursor.execute(query_venta, (venta_id,))
                venta = cursor.fetchone()
                
                if not venta:
                    print(f"No se encontró la venta con ID {venta_id}")
                    return False
                
                if venta['estado'] == 'CANCELADA':
                    print(f"La venta {venta_id} ya está cancelada")
                    return False
                
                # Obtener detalles de la venta antes de anularla
                query_detalles = """
                    SELECT vd.producto_id, vd.cantidad, p.nombre as producto_nombre
                    FROM venta_detalles vd
                    JOIN productos p ON vd.producto_id = p.id AND p.activo = TRUE
                    WHERE vd.venta_id = %s
                """
                cursor.execute(query_detalles, (venta_id,))
                detalles = cursor.fetchall()
                
                if not detalles:
                    print(f"No se encontraron detalles para la venta {venta_id}")
                    return False
                
                # Restaurar stock de productos
                for detalle in detalles:
                    query_stock = """
                        UPDATE productos 
                        SET stock = stock + %s 
                        WHERE id = %s AND activo = TRUE
                    """
                    cursor.execute(query_stock, (
                        int(detalle['cantidad']),
                        detalle['producto_id']
                    ))
                    
                    if cursor.rowcount == 0:
                        print(f"No se pudo restaurar el stock del producto {detalle['producto_nombre']} (ID: {detalle['producto_id']})")
                        return False
                
                # Anular la venta
                query_anular = """
                    UPDATE ventas 
                    SET estado = 'CANCELADA' 
                    WHERE id = %s AND estado != 'CANCELADA'
                """
                cursor.execute(query_anular, (venta_id,))
                
                if cursor.rowcount == 0:
                    print(f"No se pudo anular la venta {venta_id}")
                    return False
                
                return True
                
        except Error as e:
            print(f"Error al anular venta: {e}")
            return False