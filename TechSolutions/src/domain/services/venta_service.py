from ..entities.venta import Venta
from src.data_access.repositories.venta_repository import VentaRepository
from src.data_access.database import Transaction

class VentaService:
    def __init__(self):
        self.venta_repository = VentaRepository()
    
    def obtener_todas(self):
        ventas_data = self.venta_repository.obtener_todas()
        return [Venta(**venta) for venta in ventas_data]
    
    def obtener_por_id(self, venta_id):
        venta_data = self.venta_repository.obtener_por_id(venta_id)
        return Venta(**venta_data) if venta_data else None
    
    def obtener_por_numero_factura(self, numero_factura):
        venta_data = self.venta_repository.obtener_por_numero_factura(numero_factura)
        return Venta(**venta_data) if venta_data else None
    
    def procesar_venta(self, venta_data):
        """
        Procesa una venta con transacción y rollback en caso de error
        """
        try:
            with Transaction() as connection:
                # Generar número de factura
                from datetime import datetime
                numero_factura = f"FACT-{datetime.now().strftime('%Y%m%d')}-{self._generar_secuencia()}"
                
                # Crear la venta
                venta_id = self.venta_repository.crear_venta({
                    'numero_factura': numero_factura,
                    'cliente_id': venta_data['cliente_id'],
                    'usuario_id': venta_data['usuario_id'],
                    'fecha_venta': datetime.now().date(),
                    'subtotal': venta_data['subtotal'],
                    'impuesto': venta_data['impuesto'],
                    'total': venta_data['total']
                }, connection)
                
                if not venta_id:
                    raise Exception("No se pudo crear la venta")
                
                # Crear detalles de venta y actualizar stock
                for detalle in venta_data['detalles']:
                    # Crear detalle
                    detalle_id = self.venta_repository.crear_detalle_venta({
                        'venta_id': venta_id,
                        'producto_id': detalle['producto_id'],
                        'cantidad': detalle['cantidad'],
                        'precio_unitario': detalle['precio_unitario'],
                        'subtotal': detalle['subtotal']
                    }, connection)
                    
                    if not detalle_id:
                        raise Exception("No se pudo crear el detalle de venta")
                    
                    # Actualizar stock del producto
                    from src.domain.services.producto_service import ProductoService
                    producto_service = ProductoService()
                    producto = producto_service.obtener_por_id(detalle['producto_id'])
                    
                    if producto:
                        nuevo_stock = producto.stock - detalle['cantidad']
                        if nuevo_stock < 0:
                            raise Exception(f"Stock insuficiente para el producto {producto.nombre}")
                        
                        if not self.venta_repository.actualizar_stock_producto(
                            detalle['producto_id'], nuevo_stock, connection
                        ):
                            raise Exception(f"No se pudo actualizar el stock del producto {producto.nombre}")
                
                return {
                    'success': True,
                    'venta_id': venta_id,
                    'numero_factura': numero_factura
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generar_secuencia(self):
        """Genera una secuencia única para el número de factura"""
        import random
        return random.randint(1000, 9999)
    
    def obtener_ventas_por_fecha(self, fecha_inicio, fecha_fin):
        ventas_data = self.venta_repository.obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
        return [Venta(**venta) for venta in ventas_data]
    
    def anular_venta(self, venta_id):
        return self.venta_repository.anular_venta(venta_id)