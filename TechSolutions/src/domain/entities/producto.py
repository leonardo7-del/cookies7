class Producto:
    def __init__(self, id=None, codigo=None, nombre=None, descripcion=None, 
                 precio=0.0, stock=0, stock_minimo=5, activo=True, fecha_creacion=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.activo = activo
        self.fecha_creacion = fecha_creacion
    
    def __str__(self):
        return f"Producto {self.codigo}: {self.nombre} - ${self.precio:.2f}"
    
    def tiene_stock_suficiente(self, cantidad):
        return self.stock >= cantidad
    
    def esta_bajo_stock(self):
        return self.stock <= self.stock_minimo