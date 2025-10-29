from ..entities.producto import Producto
from src.data_access.repositories.producto_repository import ProductoRepository

class ProductoService:
    def __init__(self):
        self.producto_repository = ProductoRepository()
    
    def obtener_todos(self):
        productos = self.producto_repository.obtener_todos()
        return productos  # Ya son objetos Producto
    
    def obtener_por_id(self, producto_id):
        return self.producto_repository.obtener_por_id(producto_id)
    
    def obtener_por_codigo(self, codigo):
        data = self.producto_repository.obtener_por_codigo(codigo)
        if not data:
            return None
        return Producto(
            id=data['id'],
            codigo=data['codigo'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            precio=float(data['precio']),
            stock=data['stock'],
            stock_minimo=data['stock_minimo'],
            activo=data['activo'],
            fecha_creacion=data['fecha_creacion']
        )
    
    def buscar_por_nombre(self, nombre):
        productos_data = self.producto_repository.buscar_por_nombre(nombre)
        # Puede retornar dicts; mapear a objetos Producto
        productos = []
        for data in productos_data:
            productos.append(Producto(
                id=data['id'],
                codigo=data['codigo'],
                nombre=data['nombre'],
                descripcion=data.get('descripcion'),
                precio=float(data['precio']),
                stock=data['stock'],
                stock_minimo=data['stock_minimo'],
                activo=data['activo'],
                fecha_creacion=data['fecha_creacion']
            ))
        return productos
    
    def crear_producto(self, datos_producto):
        # Convertir el diccionario a un objeto Producto
        if isinstance(datos_producto, dict):
            producto = Producto(
                codigo=datos_producto.get('codigo'),
                nombre=datos_producto.get('nombre'),
                descripcion=datos_producto.get('descripcion'),
                precio=float(datos_producto.get('precio', 0)),
                stock=int(datos_producto.get('stock', 0)),
                stock_minimo=int(datos_producto.get('stock_minimo', 5)),
                activo=datos_producto.get('activo', True)
            )
        else:
            producto = datos_producto
            
        return self.producto_repository.crear_producto(producto)
    
    def actualizar_producto(self, producto_id, datos_producto):
        return self.producto_repository.actualizar_producto(producto_id, datos_producto)
    
    def actualizar_stock(self, producto_id, nueva_cantidad):
        return self.producto_repository.actualizar_stock(producto_id, nueva_cantidad)
    
    def eliminar_producto(self, producto_id):
        return self.producto_repository.eliminar_producto(producto_id)
    
    def obtener_productos_bajo_stock(self):
        productos_data = self.producto_repository.obtener_productos_bajo_stock()
        # Mapear dicts a objetos Producto si aplica
        productos = []
        for data in productos_data:
            try:
                productos.append(Producto(
                    id=data['id'],
                    codigo=data['codigo'],
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion'),
                    precio=float(data['precio']),
                    stock=data['stock'],
                    stock_minimo=data['stock_minimo'],
                    activo=data.get('activo', 1),
                    fecha_creacion=data.get('fecha_creacion')
                ))
            except Exception:
                # El reporte puede traer solo algunas columnas; crear objeto parcial
                productos.append(Producto(
                    id=None,
                    codigo=data.get('codigo'),
                    nombre=data.get('nombre'),
                    descripcion=None,
                    precio=float(data.get('precio', 0.0)),
                    stock=data.get('stock', 0),
                    stock_minimo=data.get('stock_minimo', 0),
                    activo=1,
                    fecha_creacion=None
                ))
        return productos