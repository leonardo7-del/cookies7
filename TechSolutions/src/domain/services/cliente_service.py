from ..entities.cliente import Cliente
from src.data_access.repositories.cliente_repository import ClienteRepository

class ClienteService:
    def __init__(self):
        self.cliente_repository = ClienteRepository()
    
    def obtener_todos(self):
        clientes_data = self.cliente_repository.obtener_todos()
        return [Cliente(**cliente) for cliente in clientes_data]
    
    def obtener_por_id(self, cliente_id):
        cliente_data = self.cliente_repository.obtener_por_id(cliente_id)
        return Cliente(**cliente_data) if cliente_data else None
    
    def buscar_por_nombre(self, nombre):
        clientes_data = self.cliente_repository.buscar_por_nombre(nombre)
        return [Cliente(**cliente) for cliente in clientes_data]
    
    def crear_cliente(self, datos_cliente):
        return self.cliente_repository.crear_cliente(datos_cliente)
    
    def actualizar_cliente(self, cliente_id, datos_cliente):
        return self.cliente_repository.actualizar_cliente(cliente_id, datos_cliente)
    
    def eliminar_cliente(self, cliente_id):
        return self.cliente_repository.eliminar_cliente(cliente_id)