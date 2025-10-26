from datetime import datetime

class Venta:
    def __init__(self, id=None, numero_factura=None, cliente_id=None, usuario_id=None,
                 fecha_venta=None, subtotal=0.0, impuesto=0.0, total=0.0, 
                 estado='COMPLETADA', fecha_creacion=None, detalles=None):
        self.id = id
        self.numero_factura = numero_factura
        self.cliente_id = cliente_id
        self.usuario_id = usuario_id
        self.fecha_venta = fecha_venta
        self.subtotal = subtotal
        self.impuesto = impuesto
        self.total = total
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.detalles = detalles or []
    
    def __str__(self):
        return f"Venta {self.numero_factura}: ${self.total:.2f}"
    
    def es_anulable(self):
        return self.estado == 'COMPLETADA'
    
    def calcular_totales(self):
        """Calcula subtotal, impuesto y total basado en los detalles"""
        self.subtotal = sum(detalle['subtotal'] for detalle in self.detalles)
        self.impuesto = self.subtotal * 0.10  # 10% de impuesto
        self.total = self.subtotal + self.impuesto