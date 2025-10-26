from ..entities.producto import Producto
from src.data_access.repositories.producto_repository import ProductoRepository

class ProductoService:
    def __init__(self):
        self.producto_repository = ProductoRepository()
    
    def obtener_todos(self):
        productos_data = self.producto_repository.obtener_todos()
        return [Producto(**producto) for producto in productos_data]
    
    def obtener_por_id(self, producto_id):
        producto_data = self.producto_repository.obtener_por_id(producto_id)
        return Producto(**producto_data) if producto_data else None
    
    def obtener_por_codigo(self, codigo):
        producto_data = self.producto_repository.obtener_por_codigo(codigo)
        return Producto(**producto_data) if producto_data else None
    
    def buscar_por_nombre(self, nombre):
        productos_data = self.producto_repository.buscar_por_nombre(nombre)
        return [Producto(**producto) for producto in productos_data]
    
    def crear_producto(self, datos_producto):
        return self.producto_repository.crear_producto(datos_producto)
    
    def actualizar_producto(self, producto_id, datos_producto):
        return self.producto_repository.actualizar_producto(producto_id, datos_producto)
    
    def actualizar_stock(self, producto_id, nueva_cantidad):
        return self.producto_repository.actualizar_stock(producto_id, nueva_cantidad)
    
    def eliminar_producto(self, producto_id):
        return self.producto_repository.eliminar_producto(producto_id)
    
    def obtener_productos_bajo_stock(self):
        productos_data = self.producto_repository.obtener_productos_bajo_stock()
        return [Producto(**producto) for producto in productos_data]