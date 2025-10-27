class VentaDetalle:
    def __init__(self, id=None, venta_id=None, producto_id=None, cantidad=0, 
                 precio_unitario=0.0, subtotal=0.0, producto=None):
        self.id = id
        self.venta_id = venta_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal
        self.producto = producto  # Objeto Producto para mostrar información
    
    def calcular_subtotal(self):
        """Calcula el subtotal basado en cantidad y precio unitario"""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal
    
    def __str__(self):
        producto_nombre = self.producto.nombre if self.producto else f"Producto ID: {self.producto_id}"
        return f"{producto_nombre} x{self.cantidad} = ${self.subtotal:.2f}"