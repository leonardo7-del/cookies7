from datetime import datetime

class Venta:
    def __init__(self, id=None, numero_factura=None, cliente_id=None, usuario_id=None,
                 fecha_venta=None, subtotal=0.0, impuesto=0.0, total=0.0, 
                 estado='COMPLETADA', fecha_creacion=None, detalles=None, 
                 cliente=None, usuario=None):
        self.id = id
        self.numero_factura = numero_factura
        self.cliente_id = cliente_id
        self.usuario_id = usuario_id
        self.fecha_venta = fecha_venta or datetime.now().date()
        self.subtotal = subtotal
        self.impuesto = impuesto
        self.total = total
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.detalles = detalles or []  # Lista de VentaDetalle
        self.cliente = cliente  # Objeto Cliente
        self.usuario = usuario  # Objeto Usuario
    
    def __str__(self):
        return f"Venta {self.numero_factura}: ${self.total:.2f}"
    
    def es_anulable(self):
        return self.estado == 'COMPLETADA'
    
    def puede_cancelarse(self):
        return self.estado in ['PENDIENTE', 'COMPLETADA']
    
    def calcular_totales(self, tax_rate=0.10):
        """Calcula subtotal, impuesto y total basado en los detalles"""
        if self.detalles:
            # Si detalles son objetos VentaDetalle
            if hasattr(self.detalles[0], 'subtotal'):
                self.subtotal = sum(detalle.subtotal for detalle in self.detalles)
            else:
                # Si detalles son diccionarios
                self.subtotal = sum(detalle.get('subtotal', 0) for detalle in self.detalles)
        else:
            self.subtotal = 0.0
            
        self.impuesto = self.subtotal * tax_rate
        self.total = self.subtotal + self.impuesto
        return self.total
    
    def agregar_detalle(self, detalle):
        """Agrega un detalle a la venta y recalcula totales"""
        self.detalles.append(detalle)
        self.calcular_totales()
    
    def generar_numero_factura(self):
        """Genera un número de factura único basado en timestamp"""
        if not self.numero_factura:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.numero_factura = f"FAC-{timestamp}"
        return self.numero_factura