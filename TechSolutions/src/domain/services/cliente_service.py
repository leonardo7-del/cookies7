from ..entities.cliente import Cliente
from src.data_access.repositories.cliente_repository import ClienteRepository

class ClienteService:
    def __init__(self):
        self.cliente_repository = ClienteRepository()
    
    def obtener_todos(self):
        # El repositorio ya retorna objetos Cliente
        return self.cliente_repository.obtener_todos()
    
    def obtener_por_id(self, cliente_id):
        return self.cliente_repository.obtener_por_id(cliente_id)
    
    def buscar_por_nombre(self, nombre):
        clientes_data = self.cliente_repository.buscar_por_nombre(nombre)
        # Puede retornar dicts, mapear a objetos Cliente
        clientes = []
        for data in clientes_data:
            clientes.append(Cliente(
                id=data['id'],
                nombre=data['nombre'],
                email=data.get('email'),
                telefono=data.get('telefono'),
                direccion=data.get('direccion'),
                ruc=data.get('ruc'),
                activo=data['activo'],
                fecha_creacion=data['fecha_creacion']
            ))
        return clientes
    
    def crear_cliente(self, datos_cliente):
        # Convertir el diccionario a objeto Cliente
        cliente = Cliente(
            nombre=datos_cliente['nombre'],
            email=datos_cliente.get('email'),
            telefono=datos_cliente.get('telefono'),
            direccion=datos_cliente.get('direccion'),
            ruc=datos_cliente.get('ruc')
        )
        return self.cliente_repository.crear_cliente(cliente)
    
    def actualizar_cliente(self, cliente_id, datos_cliente):
        return self.cliente_repository.actualizar_cliente(cliente_id, datos_cliente)
    
    def eliminar_cliente(self, cliente_id):
        return self.cliente_repository.eliminar_cliente(cliente_id)