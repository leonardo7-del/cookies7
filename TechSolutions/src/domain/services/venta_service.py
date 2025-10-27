from ..entities.venta import Venta
from ..entities.venta_detalle import VentaDetalle
from ..entities.cliente import Cliente
from ..entities.usuario import Usuario
from src.data_access.repositories.venta_repository import VentaRepository

class VentaService:
    def __init__(self):
        self.venta_repository = VentaRepository()
    
    def obtener_todas(self):
        ventas_data = self.venta_repository.obtener_todas()
        # Mantener compatibilidad: mapear dicts a objetos Venta básicos
        ventas = []
        for data in ventas_data:
            venta = Venta(
                id=data['id'],
                numero_factura=data.get('numero_factura'),
                cliente=Cliente(id=data.get('cliente_id'), nombre=data.get('cliente_nombre')) if data.get('cliente_id') else None,
                usuario=Usuario(id=data.get('usuario_id'), nombre=data.get('usuario_nombre')) if data.get('usuario_id') else None,
                fecha_venta=data.get('fecha_venta'),
                subtotal=data.get('subtotal') or 0.0,
                impuesto=data.get('impuesto') or 0.0,
                total=data.get('total') or 0.0,
                estado=data.get('estado') or 'COMPLETADA'
            )
            ventas.append(venta)
        return ventas
    
    def obtener_por_id(self, venta_id):
        data = self.venta_repository.obtener_por_id(venta_id)
        if not data:
            return None
        venta = Venta(
            id=data['id'],
            numero_factura=data.get('numero_factura'),
            cliente=Cliente(id=data.get('cliente_id'), nombre=data.get('cliente_nombre')) if data.get('cliente_id') else None,
            usuario=Usuario(id=data.get('usuario_id'), nombre=data.get('usuario_nombre')) if data.get('usuario_id') else None,
            fecha_venta=data.get('fecha_venta'),
            subtotal=data.get('subtotal') or 0.0,
            impuesto=data.get('impuesto') or 0.0,
            total=data.get('total') or 0.0,
            estado=data.get('estado') or 'COMPLETADA'
        )
        # Mapear detalles si están presentes
        detalles = []
        for d in data.get('detalles', []):
            detalles.append(VentaDetalle(
                id=d.get('id'),
                venta_id=venta.id,
                producto_id=d.get('producto_id'),
                cantidad=d.get('cantidad'),
                precio_unitario=d.get('precio_unitario'),
                subtotal=d.get('subtotal')
            ))
        venta.detalles = detalles
        return venta
    
    def obtener_por_numero_factura(self, numero_factura):
        data = self.venta_repository.obtener_por_numero_factura(numero_factura)
        if not data:
            return None
        return Venta(
            id=data['id'],
            numero_factura=data.get('numero_factura'),
            cliente=Cliente(id=data.get('cliente_id')) if data.get('cliente_id') else None,
            usuario=Usuario(id=data.get('usuario_id')) if data.get('usuario_id') else None,
            fecha_venta=data.get('fecha_venta'),
            subtotal=data.get('subtotal') or 0.0,
            impuesto=data.get('impuesto') or 0.0,
            total=data.get('total') or 0.0,
            estado=data.get('estado') or 'COMPLETADA'
        )
    
    def procesar_venta(self, venta: Venta):
        """Procesa una venta completa usando la transacción del repositorio"""
        # Asegurar número de factura y totales
        if not getattr(venta, 'numero_factura', None):
            venta.generar_numero_factura()
        venta.calcular_totales()
        
        try:
            venta_id = self.venta_repository.crear_venta_completa(venta)
            if not venta_id:
                return {'success': False, 'error': 'No se pudo crear la venta'}
            return {'success': True, 'venta_id': venta_id, 'numero_factura': venta.numero_factura}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def obtener_ventas_por_fecha(self, fecha_inicio, fecha_fin):
        ventas_data = self.venta_repository.obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
        # Mapear a objetos Venta
        ventas = []
        for data in ventas_data:
            ventas.append(Venta(
                id=data['id'],
                numero_factura=data.get('numero_factura'),
                cliente=Cliente(id=data.get('cliente_id')) if data.get('cliente_id') else None,
                usuario=Usuario(id=data.get('usuario_id')) if data.get('usuario_id') else None,
                fecha_venta=data.get('fecha_venta'),
                subtotal=data.get('subtotal') or 0.0,
                impuesto=data.get('impuesto') or 0.0,
                total=data.get('total') or 0.0,
                estado=data.get('estado') or 'COMPLETADA'
            ))
        return ventas
    
    def anular_venta(self, venta_id):
        return self.venta_repository.anular_venta(venta_id)